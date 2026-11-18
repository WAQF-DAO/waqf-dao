// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {TestBase} from "./utils/TestBase.sol";
import {MockHalalToken} from "./mocks/MockHalalToken.sol";
import {MockYieldAdapter} from "./mocks/MockYieldAdapter.sol";
import {WaqfIdentitySBT} from "../src/identity/WaqfIdentitySBT.sol";
import {IWaqfIdentitySBT} from "../src/interfaces/IWaqfProtocol.sol";
import {ShariahOracle} from "../src/oracle/ShariahOracle.sol";
import {WaqfAuditRegistry} from "../src/oracle/WaqfAuditRegistry.sol";
import {PSAK412WaterfallSplitter} from "../src/vaults/PSAK412WaterfallSplitter.sol";
import {WaqfPrincipalVault} from "../src/vaults/WaqfPrincipalVault.sol";
import {DigitalHisbahGovernor} from "../src/governance/DigitalHisbahGovernor.sol";
import {ProtocolDeployer} from "../script/DeployGenesisPools.s.sol";

contract DigitalHisbahGovernorTest is TestBase {
    MockHalalToken internal token;
    WaqfIdentitySBT internal sbt;
    ShariahOracle internal oracle;
    WaqfAuditRegistry internal auditRegistry;
    PSAK412WaterfallSplitter internal splitter;
    WaqfPrincipalVault internal vault;
    DigitalHisbahGovernor internal governor;

    address internal admin = makeAddr("admin");
    address internal ssb = makeAddr("ssb");
    address internal appraiser = makeAddr("appraiser");
    address internal impactValidator = makeAddr("impactValidator");
    address internal sinkingReserve = makeAddr("sinkingReserve");
    address internal nazhirTreasury = makeAddr("nazhirTreasury");
    address internal notarizer = makeAddr("notarizer");

    address internal wakif1 = makeAddr("wakif1");
    address internal wakif2 = makeAddr("wakif2");
    address internal wakif3 = makeAddr("wakif3");
    address internal whale = makeAddr("whale");
    address internal unverified = makeAddr("unverified");
    address internal recipient = makeAddr("recipient");

    bytes32 internal poolWpud;
    bytes32 internal poolWpum;
    bytes32 internal poolWpair;
    bytes32 internal poolWppal;
    bytes32 internal poolWpmas;

    uint256 internal constant DEPOSIT_AMOUNT = 1_000e6;

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
            notarizer
        );
        vm.stopPrank();

        sbt = d.identitySBT;
        oracle = d.shariahOracle;
        auditRegistry = d.auditRegistry;
        splitter = d.waterfallSplitter;
        vault = d.principalVault;
        governor = d.governor;

        poolWpud = vault.POOL_WPUD();
        poolWpum = vault.POOL_WPUM();
        poolWpair = vault.POOL_WPAIR();
        poolWppal = vault.POOL_WPPAL();
        poolWpmas = vault.POOL_WPMAS();

        // Issue Soulbound credentials
        vm.startPrank(admin);
        oracle.grantRole(oracle.APPRAISER_ROLE(), appraiser);
        splitter.grantRole(splitter.IMPACT_VALIDATOR_ROLE(), impactValidator);

        // Modest wakifs with 1,600 units each => weight = 1 + sqrt(1600) = 41 each (3 wakifs = 123 votes)
        sbt.issueCredential(wakif1, IWaqfIdentitySBT.RoleBadge.WAKIF, 1_600);
        sbt.issueCredential(wakif2, IWaqfIdentitySBT.RoleBadge.WAKIF, 1_600);
        sbt.issueCredential(wakif3, IWaqfIdentitySBT.RoleBadge.WAKIF, 1_600);
        sbt.issueCredential(wakif1, IWaqfIdentitySBT.RoleBadge.NAZHIR_CERTIFIED, 0);
        sbt.issueCredential(ssb, IWaqfIdentitySBT.RoleBadge.SHARIAH_BOARD, 0);
        sbt.issueCredential(impactValidator, IWaqfIdentitySBT.RoleBadge.IMPACT_VALIDATOR, 0);

        // Mega-whale with 100,000,000 units => capped at MAX_VOTING_WEIGHT = 100
        sbt.issueCredential(whale, IWaqfIdentitySBT.RoleBadge.WAKIF, 100_000_000);
        vm.stopPrank();

        address[4] memory voters = [wakif1, wakif2, wakif3, whale];
        for (uint256 i = 0; i < voters.length; ++i) {
            token.mint(voters[i], 1_000_000e6);
            vm.prank(voters[i]);
            token.approve(address(governor), type(uint256).max);
        }
        token.mint(unverified, 1_000_000e6);
        vm.prank(unverified);
        token.approve(address(governor), type(uint256).max);
    }

    function testIdentitySBTErc5192NonTransferableAndRoleBadges() public {
        assertTrue(sbt.supportsInterface(0xb45a3c0e)); // ERC-5192
        assertTrue(sbt.supportsInterface(0x80ac58cd)); // ERC-721
        assertTrue(sbt.hasRoleBadge(wakif1, IWaqfIdentitySBT.RoleBadge.WAKIF));
        assertTrue(sbt.hasRoleBadge(wakif1, IWaqfIdentitySBT.RoleBadge.NAZHIR_CERTIFIED));
        assertTrue(sbt.hasRoleBadge(ssb, IWaqfIdentitySBT.RoleBadge.SHARIAH_BOARD));
        assertTrue(sbt.hasRoleBadge(impactValidator, IWaqfIdentitySBT.RoleBadge.IMPACT_VALIDATOR));

        (uint256 tokenId, , , , bool active, ) = sbt.getCredential(wakif1);
        assertTrue(active);
        assertTrue(sbt.locked(tokenId));

        vm.startPrank(wakif1);
        vm.expectRevert(WaqfIdentitySBT.SoulboundNonTransferable.selector);
        sbt.transferFrom(wakif1, recipient, tokenId);

        vm.expectRevert(WaqfIdentitySBT.SoulboundNonTransferable.selector);
        sbt.safeTransferFrom(wakif1, recipient, tokenId);

        vm.expectRevert(WaqfIdentitySBT.SoulboundNonTransferable.selector);
        sbt.safeTransferFrom(wakif1, recipient, tokenId, "");

        vm.expectRevert(WaqfIdentitySBT.SoulboundNonTransferable.selector);
        sbt.approve(recipient, tokenId);

        vm.expectRevert(WaqfIdentitySBT.SoulboundNonTransferable.selector);
        sbt.setApprovalForAll(recipient, true);
        vm.stopPrank();
    }

    function testQuadraticCappedVotingBlocksWhaleCapture() public {
        assertEq(sbt.getVotingWeight(wakif1), 41);
        assertEq(sbt.getVotingWeight(whale), 100);
        assertEq(sbt.getVotingWeight(unverified), 0);

        // Non-SBT account cannot propose
        bytes memory callData = abi.encodeCall(
            PSAK412WaterfallSplitter.setWaterfallConfig,
            (3_950, 5_100, 950)
        );
        vm.prank(unverified);
        vm.expectRevert(
            abi.encodeWithSelector(DigitalHisbahGovernor.UnauthorizedProposer.selector, unverified)
        );
        governor.propose(poolWpud, address(splitter), 0, callData, "Unauthorized test");

        // Wakif1 proposes; 3 modest wakifs (123 total) outvote whale (100 capped)
        vm.prank(wakif1);
        uint256 propId = governor.propose(
            poolWpud,
            address(splitter),
            0,
            callData,
            "Increase Mauquf Alaih allocation to 51%"
        );

        vm.prank(wakif1);
        governor.castVote(propId, true);
        vm.prank(wakif2);
        governor.castVote(propId, true);
        vm.prank(wakif3);
        governor.castVote(propId, true);
        vm.prank(whale);
        governor.castVote(propId, false);

        DigitalHisbahGovernor.Proposal memory p = governor.getProposal(propId);
        assertEq(p.forVotes, 123);
        assertEq(p.againstVotes, 100);

        vm.warp(p.votingEnd);
        assertTrue(governor.state(propId) == DigitalHisbahGovernor.ProposalState.PENDING_SSB);
    }

    function testDualChamberExecutionAndDepositRefund() public {
        bytes32 govRole = splitter.GOVERNOR_ROLE();
        vm.prank(admin);
        splitter.grantRole(govRole, address(governor));

        bytes memory callData = abi.encodeCall(
            PSAK412WaterfallSplitter.setWaterfallConfig,
            (3_950, 5_100, 950)
        );

        uint256 balBefore = token.balanceOf(wakif1);
        vm.prank(wakif1);
        uint256 propId = governor.propose(
            poolWpum,
            address(splitter),
            0,
            callData,
            "Adjust Nautera waterfall to 51% Mauquf Alaih"
        );
        assertEq(balBefore - token.balanceOf(wakif1), DEPOSIT_AMOUNT);

        vm.prank(wakif1);
        governor.castVote(propId, true);

        DigitalHisbahGovernor.Proposal memory p = governor.getProposal(propId);
        vm.warp(p.votingEnd);

        // Cannot execute without Chamber 2 SSB approval
        vm.expectRevert(
            abi.encodeWithSelector(DigitalHisbahGovernor.SSBApprovalRequired.selector, propId)
        );
        governor.executeProposal(propId);

        // SSB approves inside 21-day clock (exact boundary day 21)
        vm.warp(p.votingEnd + 1_814_400);
        vm.prank(ssb);
        governor.approveBySSB(propId);
        assertTrue(governor.state(propId) == DigitalHisbahGovernor.ProposalState.SSB_APPROVED);

        // Execute proposal -> updates splitter config AND refunds good-faith deposit
        governor.executeProposal(propId);
        assertTrue(governor.state(propId) == DigitalHisbahGovernor.ProposalState.EXECUTED);
        assertEq(splitter.mauqufAlaihBps(), 5_100);
        assertEq(token.balanceOf(wakif1), balBefore);
    }

    function test21DaySSBClockExpirationBlocksExecutionAndAllowsGoodFaithRefund() public {
        bytes memory callData = abi.encodeCall(
            PSAK412WaterfallSplitter.setWaterfallConfig,
            (3_950, 5_100, 950)
        );

        uint256 balBefore = token.balanceOf(wakif2);
        vm.prank(wakif2);
        uint256 propId = governor.propose(
            poolWpair,
            address(splitter),
            0,
            callData,
            "Expired proposal test"
        );

        vm.prank(wakif2);
        governor.castVote(propId, true);

        DigitalHisbahGovernor.Proposal memory p = governor.getProposal(propId);
        assertEq(p.ssbDeadline, p.votingEnd + 1_814_400);

        // Warp 1 second past the 21-day (1,814,400s) SSB review window
        vm.warp(p.ssbDeadline + 1);
        assertTrue(governor.state(propId) == DigitalHisbahGovernor.ProposalState.EXPIRED);

        vm.prank(ssb);
        vm.expectRevert(
            abi.encodeWithSelector(
                DigitalHisbahGovernor.SSBReviewClockExpired.selector,
                propId,
                p.ssbDeadline
            )
        );
        governor.approveBySSB(propId);

        vm.expectRevert(
            abi.encodeWithSelector(
                DigitalHisbahGovernor.SSBReviewClockExpired.selector,
                propId,
                p.ssbDeadline
            )
        );
        governor.executeProposal(propId);

        // Good-faith proposer claims deposit refund after expiration
        vm.prank(wakif2);
        governor.claimDepositRefund(propId);
        assertEq(token.balanceOf(wakif2), balBefore);
    }

    function testZeroBurnAntiSpamDepositCaptureOnShariahOrSpamVeto() public {
        bytes memory callData = abi.encodeCall(
            PSAK412WaterfallSplitter.setWaterfallConfig,
            (3_000, 5_000, 2_000)
        );

        // Case 1: Shariah/Spam violation veto -> 0 tokens burned, 100% locked into WaqfPrincipalVault Mu'abbad
        uint256 whaleBefore = token.balanceOf(whale);
        uint256 zeroAddrBefore = token.balanceOf(address(0));
        uint256 deadAddrBefore = token.balanceOf(address(0xdead));

        vm.prank(whale);
        uint256 spamPropId = governor.propose(
            poolWppal,
            address(splitter),
            0,
            callData,
            "Illegal proposal exceeding 10% Nazhir cap"
        );
        assertEq(whaleBefore - token.balanceOf(whale), DEPOSIT_AMOUNT);

        vm.prank(ssb);
        governor.vetoBySSB(spamPropId, true, "Violates UU 41/2004 Nazhir fee cap");

        assertTrue(governor.state(spamPropId) == DigitalHisbahGovernor.ProposalState.VETOED);
        WaqfPrincipalVault.PoolInfo memory pool = vault.getPool(poolWppal);
        assertEq(pool.perpetualPrincipal, DEPOSIT_AMOUNT);
        assertEq(pool.seizedGovernanceInflow, DEPOSIT_AMOUNT);
        assertEq(token.balanceOf(address(vault)), DEPOSIT_AMOUNT);
        assertEq(token.balanceOf(address(0)), zeroAddrBefore);
        assertEq(token.balanceOf(address(0xdead)), deadAddrBefore);

        // Cannot execute vetoed proposal
        vm.expectRevert(
            abi.encodeWithSelector(DigitalHisbahGovernor.ProposalAlreadyVetoed.selector, spamPropId)
        );
        governor.executeProposal(spamPropId);

        // Case 2: Good-faith veto (not spam/Shariah violation) -> deposit refunded to proposer
        uint256 wakifBefore = token.balanceOf(wakif1);
        vm.prank(wakif1);
        uint256 policyPropId = governor.propose(
            poolWpmas,
            address(splitter),
            0,
            callData,
            "Good-faith policy review"
        );
        vm.prank(ssb);
        governor.vetoBySSB(policyPropId, false, "Deferring to next quarter");

        assertEq(token.balanceOf(wakif1), wakifBefore);
        assertEq(vault.getPool(poolWpmas).seizedGovernanceInflow, 0);
    }

    function testDefeatedProposalRefundsGoodFaithDeposit() public {
        bytes memory callData = abi.encodeCall(
            PSAK412WaterfallSplitter.setWaterfallConfig,
            (3_950, 5_100, 950)
        );
        uint256 balBefore = token.balanceOf(wakif1);
        vm.prank(wakif1);
        uint256 propId = governor.propose(
            poolWpud,
            address(splitter),
            0,
            callData,
            "Defeated proposal test"
        );

        vm.prank(whale);
        governor.castVote(propId, false);
        vm.warp(governor.getProposal(propId).votingEnd);

        assertTrue(governor.state(propId) == DigitalHisbahGovernor.ProposalState.DEFEATED);

        vm.prank(wakif1);
        governor.claimDepositRefund(propId);
        assertEq(token.balanceOf(wakif1), balBefore);
    }

    function testEndToEndProtocolIntegrationFlow() public {
        // 1. Wakif endows Mu'abbad principal into WPUD
        vm.prank(wakif1);
        token.approve(address(vault), type(uint256).max);
        vm.prank(wakif1);
        vault.depositPerpetualWaqf(poolWpud, 200_000e6);

        // 2. Appraiser & SSB whitelist adapter & Istibdal asset
        MockYieldAdapter adapter = new MockYieldAdapter(address(token), address(vault));
        bytes32 newAssetId = keccak256("SUKUK-PRODUCTIVE-WPUD-01");
        vm.prank(ssb);
        oracle.setAdapterApproval(address(adapter), true, keccak256("FATWA-SUKUK-01"), "Sukuk Mudharabah");
        vm.prank(appraiser);
        oracle.submitAppraisal(newAssetId, 250_000e6, 950, block.timestamp + 180 days, keccak256("KJPP-WPUD-01"));
        vm.prank(ssb);
        oracle.approveAppraisal(newAssetId);

        // 3. Governor executes Istibdal via Dual-Chamber Governance
        bytes memory istibdalCall = abi.encodeCall(
            WaqfPrincipalVault.executeIstibdal,
            (poolWpud, newAssetId, address(adapter), keccak256("SSB-RES-ISTIBDAL-01"))
        );

        vm.prank(wakif1);
        uint256 propId = governor.propose(
            poolWpud,
            address(vault),
            0,
            istibdalCall,
            "Execute Istibdal to Productive Mudharabah Sukuk"
        );
        vm.prank(wakif1);
        governor.castVote(propId, true);
        vm.warp(governor.getProposal(propId).votingEnd + 1 days);
        vm.prank(ssb);
        governor.approveBySSB(propId);
        governor.executeProposal(propId);

        assertEq(vault.getPool(poolWpud).currentAssetId, newAssetId);

        // 4. Route realized cash yield through Nautera Genesis Waterfall (40% / 50.5% / 9.5%)
        vm.prank(wakif1);
        vault.routeRealizedYield(poolWpud, 20_000e6);
        assertEq(token.balanceOf(sinkingReserve), 8_000e6);
        assertEq(token.balanceOf(nazhirTreasury), 1_900e6);
        assertEq(splitter.escrowedMauqufAlaih(poolWpud), 10_100e6);

        // 5. Release Mauquf Alaih with BAST attestation
        vm.prank(impactValidator);
        splitter.releaseMauqufAlaih(poolWpud, recipient, 10_100e6, keccak256("BAST-WPUD-Q1"));
        assertEq(token.balanceOf(recipient), 10_100e6);

        // 6. Notarize PSAK 412 audit epoch
        bytes memory payload = '{"pool":"WPUD","net_assets_idr":200000000000}';
        bytes32 leaf = auditRegistry.computeLeaf(payload);
        vm.prank(notarizer);
        uint256 epochId = auditRegistry.notarizeEpoch(
            "2026-Q1",
            leaf,
            200_000_000_000,
            0,
            200_000_000_000,
            29000,
            keccak256("odoo-prod-snapshot-q1")
        );
        bytes32[] memory emptyProof = new bytes32[](0);
        assertTrue(auditRegistry.verifyNotarizedPayload(epochId, payload, emptyProof));
    }

    function testFuzzVotingWeightQuadraticAndCapped(uint256 units) public {
        address fuzzWakif = makeAddr("fuzzWakif");
        vm.prank(admin);
        sbt.issueCredential(fuzzWakif, IWaqfIdentitySBT.RoleBadge.WAKIF, units);

        uint256 weight = sbt.getVotingWeight(fuzzWakif);
        assertGe(weight, 1);
        assertLe(weight, sbt.MAX_VOTING_WEIGHT());
    }
}
