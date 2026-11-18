// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {TestBase} from "./utils/TestBase.sol";
import {MockHalalToken} from "./mocks/MockHalalToken.sol";
import {MockYieldAdapter} from "./mocks/MockYieldAdapter.sol";
import {ShariahOracle} from "../src/oracle/ShariahOracle.sol";
import {PSAK412WaterfallSplitter} from "../src/vaults/PSAK412WaterfallSplitter.sol";
import {WaqfPrincipalVault} from "../src/vaults/WaqfPrincipalVault.sol";
import {ProtocolDeployer} from "../script/DeployGenesisPools.s.sol";
import {AccessRoles} from "../src/libraries/AccessRoles.sol";

contract WaqfPrincipalVaultTest is TestBase {
    MockHalalToken internal token;
    ShariahOracle internal oracle;
    PSAK412WaterfallSplitter internal splitter;
    WaqfPrincipalVault internal vault;
    MockYieldAdapter internal approvedAdapterA;
    MockYieldAdapter internal approvedAdapterB;
    MockYieldAdapter internal unapprovedAdapter;

    address internal admin = makeAddr("admin");
    address internal ssb = makeAddr("ssb");
    address internal appraiser = makeAddr("appraiser");
    address internal governor = makeAddr("governor");
    address internal sinkingReserve = makeAddr("sinkingReserve");
    address internal nazhirTreasury = makeAddr("nazhirTreasury");
    address internal wakifA = makeAddr("wakifA");
    address internal wakifB = makeAddr("wakifB");
    address internal heirB = makeAddr("heirB");
    address internal attacker = makeAddr("attacker");

    bytes32 internal poolWpud;
    bytes32 internal poolWpum;
    bytes32 internal poolWpair;
    bytes32 internal poolWppal;
    bytes32 internal poolWpmas;

    function setUp() public {
        vm.warp(1_700_000_000);

        token = new MockHalalToken();
        vm.startPrank(admin);
        ProtocolDeployer.ProtocolDeployment memory d = ProtocolDeployer.deployAndConfigure(
            admin,
            address(token),
            ssb,
            sinkingReserve,
            nazhirTreasury,
            admin
        );
        vm.stopPrank();

        oracle = d.shariahOracle;
        splitter = d.waterfallSplitter;
        vault = d.principalVault;

        poolWpud = vault.POOL_WPUD();
        poolWpum = vault.POOL_WPUM();
        poolWpair = vault.POOL_WPAIR();
        poolWppal = vault.POOL_WPPAL();
        poolWpmas = vault.POOL_WPMAS();

        vm.startPrank(admin);
        oracle.grantRole(oracle.APPRAISER_ROLE(), appraiser);
        vault.grantRole(vault.GOVERNOR_ROLE(), governor);
        vm.stopPrank();

        approvedAdapterA = new MockYieldAdapter(address(token), address(vault));
        approvedAdapterB = new MockYieldAdapter(address(token), address(vault));
        unapprovedAdapter = new MockYieldAdapter(address(token), address(vault));

        vm.startPrank(ssb);
        oracle.setAdapterApproval(
            address(approvedAdapterA),
            true,
            keccak256("FATWA-ADAPTER-A"),
            "Murabahah Working Capital"
        );
        oracle.setAdapterApproval(
            address(approvedAdapterB),
            true,
            keccak256("FATWA-ADAPTER-B"),
            "Ijarah Productive Infrastructure"
        );
        vm.stopPrank();

        token.mint(wakifA, 10_000_000e6);
        token.mint(wakifB, 10_000_000e6);
        token.mint(governor, 1_000_000e6);

        vm.prank(wakifA);
        token.approve(address(vault), type(uint256).max);
        vm.prank(wakifB);
        token.approve(address(vault), type(uint256).max);
        vm.prank(governor);
        token.approve(address(vault), type(uint256).max);
    }

    function testGenesisPoolsConfiguredCorrectly() public view {
        assertEq(vault.poolCount(), 5);
        assertEq(poolWpud, bytes32("WPUD"));
        assertEq(poolWpum, bytes32("WPUM"));
        assertEq(poolWpair, bytes32("WPAIR"));
        assertEq(poolWppal, bytes32("WPPAL"));
        assertEq(poolWpmas, bytes32("WPMAS"));

        assertTrue(vault.poolExists(poolWpud));
        assertTrue(vault.poolExists(poolWpum));
        assertTrue(vault.poolExists(poolWpair));
        assertTrue(vault.poolExists(poolWppal));
        assertTrue(vault.poolExists(poolWpmas));
    }

    function testPerpetualWaqfLockedPermanently() public {
        uint256 amount = 500_000e6;
        vm.prank(wakifA);
        uint256 depId = vault.depositPerpetualWaqf(poolWpud, amount);

        WaqfPrincipalVault.PoolInfo memory pool = vault.getPool(poolWpud);
        assertEq(pool.perpetualPrincipal, amount);
        assertEq(vault.totalPerpetualPrincipal(), amount);
        assertEq(token.balanceOf(address(vault)), amount);

        // Attempting redemption of Mu'abbad perpetual deposit MUST revert
        vm.prank(wakifA);
        vm.expectRevert(WaqfPrincipalVault.PerpetualWaqfNonRedeemable.selector);
        vault.redeemTemporaryWaqf(depId);

        vm.prank(admin);
        vm.expectRevert(WaqfPrincipalVault.PerpetualWaqfNonRedeemable.selector);
        vault.redeemTemporaryWaqf(depId);
    }

    function testTemporaryCashWaqfMaturityAndDesignatedHeirRedemption() public {
        uint256 amount = 300_000e6;
        uint256 lockDuration = 90 days;

        vm.prank(wakifB);
        uint256 depId = vault.depositTemporaryWaqf(poolWpum, amount, lockDuration, heirB);

        (uint256 totalAssets, uint256 tempLiabilities, uint256 netAssets) = vault.getPSAK412Balances();
        assertEq(tempLiabilities, amount);
        assertEq(netAssets, 0);
        assertEq(totalAssets, amount);

        // Before maturity: reverts
        uint256 t0 = vm.getBlockTimestamp();
        vm.warp(t0 + 89 days);
        vm.prank(heirB);
        vm.expectRevert(
            abi.encodeWithSelector(
                WaqfPrincipalVault.TemporaryWaqfNotMatured.selector,
                t0 + 90 days,
                t0 + 89 days
            )
        );
        vault.redeemTemporaryWaqf(depId);

        // Unauthorized third-party cannot redeem even after maturity
        vm.warp(t0 + 90 days);
        vm.prank(attacker);
        vm.expectRevert(
            abi.encodeWithSelector(WaqfPrincipalVault.UnauthorizedRedemption.selector, attacker)
        );
        vault.redeemTemporaryWaqf(depId);

        // Designated heir redeems 100% nominal principal
        uint256 heirBalanceBefore = token.balanceOf(heirB);
        vm.prank(heirB);
        vault.redeemTemporaryWaqf(depId);
        assertEq(token.balanceOf(heirB) - heirBalanceBefore, amount);

        // Double redemption reverts
        vm.prank(wakifB);
        vm.expectRevert(
            abi.encodeWithSelector(WaqfPrincipalVault.DepositAlreadyRedeemed.selector, depId)
        );
        vault.redeemTemporaryWaqf(depId);

        (totalAssets, tempLiabilities, netAssets) = vault.getPSAK412Balances();
        assertEq(tempLiabilities, 0);
        assertEq(totalAssets, 0);
    }

    function testDeployAndRecallFromShariahApprovedAdapter() public {
        vm.prank(wakifA);
        vault.depositPerpetualWaqf(poolWpair, 400_000e6);

        // Unapproved adapter rejected
        vm.prank(admin);
        vm.expectRevert(
            abi.encodeWithSelector(
                WaqfPrincipalVault.AdapterNotShariahApproved.selector,
                address(unapprovedAdapter)
            )
        );
        vault.deployToApprovedAdapter(poolWpair, address(unapprovedAdapter), 100_000e6);

        // Approved adapter succeeds
        vm.prank(admin);
        vault.deployToApprovedAdapter(poolWpair, address(approvedAdapterA), 250_000e6);
        assertEq(token.balanceOf(address(approvedAdapterA)), 250_000e6);
        assertEq(vault.totalDeployedPrincipal(), 250_000e6);

        // Adapter approves recall and vault pulls principal back cleanly
        approvedAdapterA.approveVaultRecall(250_000e6);
        vm.prank(admin);
        vault.recallFromAdapter(poolWpair, address(approvedAdapterA), 250_000e6);
        assertEq(token.balanceOf(address(vault)), 400_000e6);
        assertEq(vault.totalDeployedPrincipal(), 0);
    }

    function testExecuteIstibdalEnforcesAAOIFISS60Invariants() public {
        bytes32 poolCode = poolWppal;
        vm.prank(wakifA);
        vault.depositPerpetualWaqf(poolCode, 500_000e6);

        uint256 nowTs = vm.getBlockTimestamp();

        // First asset onboarding: 550,000e6 appraised, 800 bps (8.00%)
        bytes32 asset1 = keccak256("ASSET-AGRI-01");
        vm.prank(appraiser);
        oracle.submitAppraisal(asset1, 550_000e6, 800, nowTs + 30 days, keccak256("KJPP-01"));

        // Must fail before SSB approval
        vm.prank(admin);
        vm.expectRevert(abi.encodeWithSelector(WaqfPrincipalVault.IstibdalNotShariahApproved.selector, asset1));
        vault.executeIstibdal(poolCode, asset1, address(approvedAdapterA), keccak256("SSB-RES-01"));

        // SSB approves asset1
        vm.prank(ssb);
        oracle.approveAppraisal(asset1);

        // Succeeds
        vm.prank(admin);
        vault.executeIstibdal(poolCode, asset1, address(approvedAdapterA), keccak256("SSB-RES-01"));

        WaqfPrincipalVault.PoolInfo memory pool = vault.getPool(poolCode);
        assertEq(pool.currentAssetId, asset1);
        assertEq(pool.currentAppraisedValue, 550_000e6);
        assertEq(pool.currentYieldBps, 800);

        // Asset2 with lower value (549,999e6 < 550,000e6) MUST revert
        bytes32 assetLowValue = keccak256("ASSET-LOW-VAL");
        vm.prank(appraiser);
        oracle.submitAppraisal(assetLowValue, 549_999e6, 900, nowTs + 30 days, keccak256("KJPP-02"));
        vm.prank(ssb);
        oracle.approveAppraisal(assetLowValue);

        vm.prank(admin);
        vm.expectRevert(
            abi.encodeWithSelector(
                WaqfPrincipalVault.IstibdalValueBelowPrincipal.selector,
                549_999e6,
                550_000e6
            )
        );
        vault.executeIstibdal(poolCode, assetLowValue, address(approvedAdapterB), keccak256("SSB-RES-02"));

        // Asset3 with lower yield (799 bps < 800 bps) MUST revert
        bytes32 assetLowYield = keccak256("ASSET-LOW-YIELD");
        vm.prank(appraiser);
        oracle.submitAppraisal(assetLowYield, 600_000e6, 799, nowTs + 30 days, keccak256("KJPP-03"));
        vm.prank(ssb);
        oracle.approveAppraisal(assetLowYield);

        vm.prank(admin);
        vm.expectRevert(
            abi.encodeWithSelector(WaqfPrincipalVault.IstibdalYieldRegression.selector, 799, 800)
        );
        vault.executeIstibdal(poolCode, assetLowYield, address(approvedAdapterB), keccak256("SSB-RES-03"));

        // Asset4 with expired appraisal MUST revert
        bytes32 assetExpired = keccak256("ASSET-EXPIRED");
        uint256 exp = nowTs + 10 days;
        vm.prank(appraiser);
        oracle.submitAppraisal(assetExpired, 600_000e6, 850, exp, keccak256("KJPP-04"));
        vm.prank(ssb);
        oracle.approveAppraisal(assetExpired);
        vm.warp(exp);

        vm.prank(admin);
        vm.expectRevert(
            abi.encodeWithSelector(WaqfPrincipalVault.AppraisalExpired.selector, assetExpired, exp)
        );
        vault.executeIstibdal(poolCode, assetExpired, address(approvedAdapterB), keccak256("SSB-RES-04"));

        // Asset5 valid higher value & higher yield with unapproved adapter reverts, approved adapter succeeds
        bytes32 assetValid = keccak256("ASSET-VALID-05");
        vm.prank(appraiser);
        oracle.submitAppraisal(assetValid, 650_000e6, 920, block.timestamp + 60 days, keccak256("KJPP-05"));
        vm.prank(ssb);
        oracle.approveAppraisal(assetValid);

        vm.prank(admin);
        vm.expectRevert(
            abi.encodeWithSelector(
                WaqfPrincipalVault.AdapterNotShariahApproved.selector,
                address(unapprovedAdapter)
            )
        );
        vault.executeIstibdal(poolCode, assetValid, address(unapprovedAdapter), keccak256("SSB-RES-05"));

        vm.prank(admin);
        vault.executeIstibdal(poolCode, assetValid, address(approvedAdapterB), keccak256("SSB-RES-05"));
        pool = vault.getPool(poolCode);
        assertEq(pool.currentAssetId, assetValid);
        assertEq(pool.currentYieldAdapter, address(approvedAdapterB));
        assertEq(pool.currentAppraisedValue, 650_000e6);
        assertEq(pool.currentYieldBps, 920);
    }

    function testReceiveSeizedGovernanceDepositAndRouteYield() public {
        bytes32 poolCode = poolWpmas;
        bytes32 govRole = vault.GOVERNOR_ROLE();

        // Non-governor cannot call receiveSeizedGovernanceDeposit
        vm.prank(attacker);
        vm.expectRevert(
            abi.encodeWithSelector(
                AccessRoles.AccessControlUnauthorizedAccount.selector,
                attacker,
                govRole
            )
        );
        vault.receiveSeizedGovernanceDeposit(poolCode, 1_000e6);

        // Governor seizes deposit -> locked permanently in Mu'abbad principal
        vm.prank(governor);
        vault.receiveSeizedGovernanceDeposit(poolCode, 1_000e6);

        WaqfPrincipalVault.PoolInfo memory pool = vault.getPool(poolCode);
        assertEq(pool.perpetualPrincipal, 1_000e6);
        assertEq(pool.seizedGovernanceInflow, 1_000e6);
        assertEq(vault.totalPerpetualPrincipal(), 1_000e6);

        // Route realized yield without touching principal
        vm.prank(wakifA);
        vault.routeRealizedYield(poolCode, 100_000e6);

        assertEq(token.balanceOf(address(vault)), 1_000e6);
        assertEq(token.balanceOf(sinkingReserve), 40_000e6);
        assertEq(token.balanceOf(nazhirTreasury), 9_500e6);
        assertEq(splitter.escrowedMauqufAlaih(poolCode), 50_500e6);
    }

    function testFuzzTemporaryWaqfLockAndRedemption(uint64 lockDuration, uint96 depositAmt) public {
        uint256 duration = uint256(lockDuration % (3650 days)) + vault.MIN_TEMPORARY_LOCK();
        uint256 amount = uint256(depositAmt % 1_000_000e6) + 1;

        token.mint(wakifB, amount);
        vm.prank(wakifB);
        uint256 depId = vault.depositTemporaryWaqf(poolWpum, amount, duration, heirB);

        vm.warp(block.timestamp + duration);

        uint256 before = token.balanceOf(heirB);
        vm.prank(heirB);
        vault.redeemTemporaryWaqf(depId);
        assertEq(token.balanceOf(heirB) - before, amount);
    }
}
