// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {TestBase} from "./utils/TestBase.sol";
import {MockHalalToken} from "./mocks/MockHalalToken.sol";
import {PSAK412WaterfallSplitter} from "../src/vaults/PSAK412WaterfallSplitter.sol";
import {AccessRoles} from "../src/libraries/AccessRoles.sol";

contract PSAK412WaterfallSplitterTest is TestBase {
    MockHalalToken internal token;
    PSAK412WaterfallSplitter internal splitter;

    address internal admin = makeAddr("admin");
    address internal impactValidator = makeAddr("impactValidator");
    address internal sinkingReserve = makeAddr("sinkingReserve");
    address internal nazhirTreasury = makeAddr("nazhirTreasury");
    address internal beneficiary = makeAddr("beneficiary");
    address internal yieldSource = makeAddr("yieldSource");
    address internal attacker = makeAddr("attacker");

    bytes32 internal constant POOL_WPUD = 0x5750554400000000000000000000000000000000000000000000000000000000;

    function setUp() public {
        token = new MockHalalToken();
        splitter = new PSAK412WaterfallSplitter(
            admin,
            address(token),
            sinkingReserve,
            nazhirTreasury,
            4_000,
            5_050,
            950
        );

        bytes32 validatorRole = splitter.IMPACT_VALIDATOR_ROLE();
        vm.prank(admin);
        splitter.grantRole(validatorRole, impactValidator);

        token.mint(yieldSource, 100_000_000e6);
        vm.prank(yieldSource);
        token.approve(address(splitter), type(uint256).max);
    }

    function testNauteraGenesisPresetDistribution() public {
        uint256 yieldCash = 1_000_000e6;

        vm.prank(yieldSource);
        splitter.distributeYield(POOL_WPUD, yieldCash);

        // 40.0% = 400,000e6 upfront to sinkingFundReserve
        assertEq(token.balanceOf(sinkingReserve), 400_000e6);
        // 9.5% = 95,000e6 to nazhirTreasury
        assertEq(token.balanceOf(nazhirTreasury), 95_000e6);
        // 50.5% = 505,000e6 locked in mauqufAlaihEscrow on splitter
        assertEq(token.balanceOf(address(splitter)), 505_000e6);
        assertEq(splitter.escrowedMauqufAlaih(POOL_WPUD), 505_000e6);
        assertEq(splitter.totalEscrowedMauqufAlaih(), 505_000e6);
    }

    function testStatutoryCapRevertsWhenNazhirFeeExceeds1000Bps() public {
        // Constructor guard
        vm.expectRevert(PSAK412WaterfallSplitter.NazhirFeeExceedsStatutoryCap.selector);
        new PSAK412WaterfallSplitter(admin, address(token), sinkingReserve, nazhirTreasury, 3_900, 5_099, 1_001);

        // Config update guard
        vm.prank(admin);
        vm.expectRevert(PSAK412WaterfallSplitter.NazhirFeeExceedsStatutoryCap.selector);
        splitter.setWaterfallConfig(3_500, 5_400, 1_100);
    }

    function testStatutoryMinMauqufAlaihAndSumValidation() public {
        vm.prank(admin);
        vm.expectRevert(PSAK412WaterfallSplitter.MauqufAlaihBelowMinimum.selector);
        splitter.setWaterfallConfig(4_100, 4_999, 901);

        vm.prank(admin);
        vm.expectRevert(PSAK412WaterfallSplitter.InvalidWaterfallBasisPoints.selector);
        splitter.setWaterfallConfig(4_000, 5_000, 950);

        // Max allowed 1000 bps (10.00%) succeeds when Mauquf >= 5000 and sum == 10000
        vm.prank(admin);
        splitter.setWaterfallConfig(4_000, 5_000, 1_000);
        assertEq(splitter.nazhirFeeBps(), 1_000);
    }

    function testReleaseMauqufAlaihRequiresValidBastAndRole() public {
        vm.prank(yieldSource);
        splitter.distributeYield(POOL_WPUD, 1_000_000e6);

        // Missing BAST attestation reverts
        vm.prank(impactValidator);
        vm.expectRevert(PSAK412WaterfallSplitter.MissingBastAttestation.selector);
        splitter.releaseMauqufAlaih(POOL_WPUD, beneficiary, 100_000e6, bytes32(0));

        // Unauthorized caller reverts
        bytes32 bastHash = keccak256("BAST-2026-WPUD-001");
        bytes32 validatorRole = splitter.IMPACT_VALIDATOR_ROLE();
        vm.prank(attacker);
        vm.expectRevert(
            abi.encodeWithSelector(
                AccessRoles.AccessControlUnauthorizedAccount.selector,
                attacker,
                validatorRole
            )
        );
        splitter.releaseMauqufAlaih(POOL_WPUD, beneficiary, 100_000e6, bastHash);

        // Over-release reverts
        vm.prank(impactValidator);
        vm.expectRevert(
            abi.encodeWithSelector(
                PSAK412WaterfallSplitter.InsufficientMauqufEscrow.selector,
                POOL_WPUD,
                505_001e6,
                505_000e6
            )
        );
        splitter.releaseMauqufAlaih(POOL_WPUD, beneficiary, 505_001e6, bastHash);

        // Authorized release with valid BAST succeeds
        vm.prank(impactValidator);
        splitter.releaseMauqufAlaih(POOL_WPUD, beneficiary, 250_000e6, bastHash);

        assertEq(token.balanceOf(beneficiary), 250_000e6);
        assertEq(splitter.escrowedMauqufAlaih(POOL_WPUD), 255_000e6);
        assertEq(splitter.releasedMauqufAlaih(POOL_WPUD), 250_000e6);
        assertEq(splitter.disbursementCount(), 1);
        PSAK412WaterfallSplitter.DisbursementRecord memory rec = splitter.getDisbursement(0);
        assertEq(rec.bastAttestationHash, bastHash);
        assertEq(rec.beneficiary, beneficiary);
        assertEq(rec.amount, 250_000e6);
    }

    function testFuzzWaterfallConservationAndStatutoryCaps(uint96 realizedCash) public {
        vm.assume(realizedCash > 0);
        token.mint(yieldSource, uint256(realizedCash));

        uint256 sinkingBefore = token.balanceOf(sinkingReserve);
        uint256 nazhirBefore = token.balanceOf(nazhirTreasury);
        uint256 escrowBefore = splitter.escrowedMauqufAlaih(POOL_WPUD);

        vm.prank(yieldSource);
        splitter.distributeYield(POOL_WPUD, uint256(realizedCash));

        uint256 sinkingDelta = token.balanceOf(sinkingReserve) - sinkingBefore;
        uint256 nazhirDelta = token.balanceOf(nazhirTreasury) - nazhirBefore;
        uint256 mauqufDelta = splitter.escrowedMauqufAlaih(POOL_WPUD) - escrowBefore;

        // 100% value conservation (zero stuck dust)
        assertEq(sinkingDelta + nazhirDelta + mauqufDelta, uint256(realizedCash));
        // Nazhir NEVER exceeds 10.00% even by 1 wei
        assertLe(nazhirDelta * 10_000, uint256(realizedCash) * 1_000);
        // Mauquf 'Alaih receives >= 50.00% (actually >= 50.50% with preset)
        assertGe(mauqufDelta, (uint256(realizedCash) * 5_000) / 10_000);
    }

    function testFuzzRejectsAnyNazhirFeeAbove1000Bps(uint16 feeBps) public {
        vm.assume(feeBps > 1_000);
        uint16 remaining = feeBps <= 10_000 ? 10_000 - feeBps : 0;
        vm.prank(admin);
        vm.expectRevert(PSAK412WaterfallSplitter.NazhirFeeExceedsStatutoryCap.selector);
        splitter.setWaterfallConfig(0, remaining, feeBps);
    }
}
