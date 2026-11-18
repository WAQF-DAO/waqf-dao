// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {TestBase} from "./utils/TestBase.sol";
import {WaqfAuditRegistry} from "../src/oracle/WaqfAuditRegistry.sol";
import {IWaqfAuditRegistry} from "../src/interfaces/IWaqfProtocol.sol";
import {AccessRoles} from "../src/libraries/AccessRoles.sol";

contract WaqfAuditRegistryTest is TestBase {
    WaqfAuditRegistry internal registry;

    address internal admin = makeAddr("admin");
    address internal notarizer = makeAddr("notarizer");
    address internal unauthorized = makeAddr("unauthorized");

    bytes internal constant PAYLOAD_0 =
        '{"account":"10101","pool":"WPUD","amount_idr":1500000000,"type":"muabbad"}';
    bytes internal constant PAYLOAD_1 =
        '{"account":"20101","pool":"WPUM","amount_idr":500000000,"type":"muaqqat"}';
    bytes internal constant PAYLOAD_2 =
        '{"account":"40101","pool":"WPAIR","amount_idr":120000000,"type":"yield"}';
    bytes internal constant PAYLOAD_3 =
        '{"account":"50101","pool":"WPPAL","amount_idr":60600000,"type":"mauquf_alaih"}';
    bytes internal constant PAYLOAD_4 =
        '{"account":"50201","pool":"WPMAS","amount_idr":11400000,"type":"nazhir_ujrah"}';

    bytes32 internal constant LEAF_0 = 0x0512c80a30c35f6f80759defb25e332d2b0dacebead02dac9b43a9352e60c5ce;
    bytes32 internal constant LEAF_1 = 0x46b376898d288924b6f87678bb6c79da1813638e8a0becb6ab36ab5dbc4365a9;
    bytes32 internal constant LEAF_2 = 0xea16a8fa2bb93a54490f31ebc94b17f4c5a017150af29c14de7c72f4e2328679;
    bytes32 internal constant LEAF_3 = 0xcfc037c487d1dfbc5b08a2ec9849d56820cb7368463faffa336f4417b6ef8a86;
    bytes32 internal constant LEAF_4 = 0x791d2d2e3c9ed3fd4599f2f0364f3bff11d8bc7e0bc0c7b65962d985f59c536f;

    bytes32 internal constant ROOT_1 = 0x0512c80a30c35f6f80759defb25e332d2b0dacebead02dac9b43a9352e60c5ce;
    bytes32 internal constant ROOT_2 = 0xb570606c6d76e4bb465d8893037f116ba98ae1437446201d0c52f521126ad58d;
    bytes32 internal constant ROOT_3 = 0xc80cb18eda9fd4d1d8a811571effef7ee3c19e25227d774b22db7e4db3bc439d;
    bytes32 internal constant ROOT_4 = 0x387a38319fc952f91563fa232f8d8258772328af85032c329b245ff6f711d479;
    bytes32 internal constant ROOT_5 = 0x834e008333d94add62b38fd752c989bea9236b63d991690c200f5988e7c483c4;

    function setUp() public {
        registry = new WaqfAuditRegistry(admin, notarizer);
    }

    function testComputeLeafMatchesCrossLanguageSpec() public view {
        assertEq(registry.computeLeaf(PAYLOAD_0), LEAF_0);
        assertEq(registry.computeLeaf(PAYLOAD_1), LEAF_1);
        assertEq(registry.computeLeaf(PAYLOAD_2), LEAF_2);
        assertEq(registry.computeLeaf(PAYLOAD_3), LEAF_3);
        assertEq(registry.computeLeaf(PAYLOAD_4), LEAF_4);
    }

    function testMerkleSingleLeafProof() public {
        vm.prank(notarizer);
        uint256 epochId = registry.notarizeEpoch(
            "2026-Q1-SINGLE",
            ROOT_1,
            1_500_000_000,
            0,
            1_500_000_000,
            24500,
            keccak256("odoo-db-q1")
        );

        bytes32[] memory emptyProof = new bytes32[](0);
        assertTrue(registry.verifyInclusionProof(ROOT_1, LEAF_0, emptyProof));
        assertTrue(registry.verifyNotarizedLeaf(epochId, LEAF_0, emptyProof));
        assertTrue(registry.verifyNotarizedPayload(epochId, PAYLOAD_0, emptyProof));
        assertFalse(registry.verifyNotarizedLeaf(epochId, LEAF_1, emptyProof));
    }

    function testMerkleEvenLeavesTwoAndFour() public {
        // N = 2
        bytes32[] memory p2_0 = new bytes32[](1);
        p2_0[0] = LEAF_1;
        bytes32[] memory p2_1 = new bytes32[](1);
        p2_1[0] = LEAF_0;

        assertTrue(registry.verifyInclusionProof(ROOT_2, LEAF_0, p2_0));
        assertTrue(registry.verifyInclusionProof(ROOT_2, LEAF_1, p2_1));

        // N = 4
        vm.prank(notarizer);
        uint256 epochId = registry.notarizeEpoch(
            "2026-Q2-EVEN4",
            ROOT_4,
            2_000_000_000,
            500_000_000,
            1_500_000_000,
            28000,
            keccak256("odoo-db-q2")
        );

        bytes32 node23 = 0x71b13df7e7173e0a084d0800a50f42b4758e595d6cc10d8d1b789eff0f020ef6;
        bytes32[] memory p4_0 = new bytes32[](2);
        p4_0[0] = LEAF_1;
        p4_0[1] = node23;

        bytes32[] memory p4_2 = new bytes32[](2);
        p4_2[0] = LEAF_3;
        p4_2[1] = ROOT_2;

        bytes32[] memory p4_3 = new bytes32[](2);
        p4_3[0] = LEAF_2;
        p4_3[1] = ROOT_2;

        assertTrue(registry.verifyNotarizedLeaf(epochId, LEAF_0, p4_0));
        assertTrue(registry.verifyNotarizedPayload(epochId, PAYLOAD_2, p4_2));
        assertTrue(registry.verifyNotarizedPayload(epochId, PAYLOAD_3, p4_3));
    }

    function testMerkleOddLeavesThreeAndFive() public {
        // N = 3: leaf 0 and leaf 1 have depth 2; unpaired leaf 2 carried unchanged has depth 1
        vm.prank(notarizer);
        uint256 epoch3 = registry.notarizeEpoch(
            "2026-Q3-ODD3",
            ROOT_3,
            2_120_000_000,
            500_000_000,
            1_620_000_000,
            31000,
            keccak256("odoo-db-q3")
        );

        bytes32[] memory p3_0 = new bytes32[](2);
        p3_0[0] = LEAF_1;
        p3_0[1] = LEAF_2;

        bytes32[] memory p3_1 = new bytes32[](2);
        p3_1[0] = LEAF_0;
        p3_1[1] = LEAF_2;

        bytes32[] memory p3_2 = new bytes32[](1);
        p3_2[0] = ROOT_2;

        assertTrue(registry.verifyNotarizedLeaf(epoch3, LEAF_0, p3_0));
        assertTrue(registry.verifyNotarizedLeaf(epoch3, LEAF_1, p3_1));
        assertTrue(registry.verifyNotarizedLeaf(epoch3, LEAF_2, p3_2));

        // N = 5: leaves 0..3 have depth 3; unpaired leaf 4 carried across 2 levels has depth 1
        vm.prank(notarizer);
        uint256 epoch5 = registry.notarizeEpoch(
            "2026-Q4-ODD5",
            ROOT_5,
            2_192_000_000,
            500_000_000,
            1_692_000_000,
            32500,
            keccak256("odoo-db-q4")
        );

        bytes32 node23 = 0x71b13df7e7173e0a084d0800a50f42b4758e595d6cc10d8d1b789eff0f020ef6;
        bytes32[] memory p5_0 = new bytes32[](3);
        p5_0[0] = LEAF_1;
        p5_0[1] = node23;
        p5_0[2] = LEAF_4;

        bytes32[] memory p5_3 = new bytes32[](3);
        p5_3[0] = LEAF_2;
        p5_3[1] = ROOT_2;
        p5_3[2] = LEAF_4;

        bytes32[] memory p5_4 = new bytes32[](1);
        p5_4[0] = ROOT_4;

        assertTrue(registry.verifyNotarizedPayload(epoch5, PAYLOAD_0, p5_0));
        assertTrue(registry.verifyNotarizedPayload(epoch5, PAYLOAD_3, p5_3));
        assertTrue(registry.verifyNotarizedPayload(epoch5, PAYLOAD_4, p5_4));
    }

    function testRejectsInvalidProofAndTamperedPayload() public {
        vm.prank(notarizer);
        uint256 epochId = registry.notarizeEpoch(
            "2026-Q4-ODD5",
            ROOT_5,
            2_192_000_000,
            500_000_000,
            1_692_000_000,
            32500,
            keccak256("odoo-db-q4")
        );

        bytes32[] memory p5_4 = new bytes32[](1);
        p5_4[0] = ROOT_4;

        // Tampered payload
        bytes memory tamperedPayload =
            '{"account":"50201","pool":"WPMAS","amount_idr":11400001,"type":"nazhir_ujrah"}';
        assertFalse(registry.verifyNotarizedPayload(epochId, tamperedPayload, p5_4));

        // Tampered sibling
        bytes32[] memory wrongProof = new bytes32[](1);
        wrongProof[0] = bytes32(uint256(ROOT_4) ^ 1);
        assertFalse(registry.verifyNotarizedLeaf(epochId, LEAF_4, wrongProof));

        // Wrong root
        assertFalse(registry.verifyInclusionProof(bytes32(uint256(ROOT_5) ^ 1), LEAF_4, p5_4));

        // Non-existent epoch reverts
        vm.expectRevert(abi.encodeWithSelector(WaqfAuditRegistry.EpochNotFound.selector, 99));
        registry.verifyNotarizedLeaf(99, LEAF_4, p5_4);
    }

    function testNotarizeEnforcesPSAK412IdentityAndRole() public {
        bytes32 notarizerRole = registry.NOTARIZER_ROLE();
        vm.prank(unauthorized);
        vm.expectRevert(
            abi.encodeWithSelector(
                AccessRoles.AccessControlUnauthorizedAccount.selector,
                unauthorized,
                notarizerRole
            )
        );
        registry.notarizeEpoch("2026-M01", ROOT_1, 1000, 400, 600, 15000, keccak256("db"));

        // Mismatch: 1000 != 400 + 599
        vm.prank(notarizer);
        vm.expectRevert(WaqfAuditRegistry.PSAK412BalanceMismatch.selector);
        registry.notarizeEpoch("2026-M01", ROOT_1, 1000, 400, 599, 15000, keccak256("db"));

        // Mismatch: tempWaqfLiabilitiesIdr > totalAssetsIdr
        vm.prank(notarizer);
        vm.expectRevert(WaqfAuditRegistry.PSAK412BalanceMismatch.selector);
        registry.notarizeEpoch("2026-M01", ROOT_1, 1000, 1001, 0, 15000, keccak256("db"));

        // Valid epoch appends cleanly
        vm.prank(notarizer);
        uint256 id = registry.notarizeEpoch("2026-M01", ROOT_1, 1000, 400, 600, 15000, keccak256("db"));
        assertEq(id, 0);
        assertEq(registry.epochCount(), 1);
        IWaqfAuditRegistry.AuditEpoch memory epoch = registry.getEpoch(0);
        assertEq(epoch.periodCode, "2026-M01");
        assertEq(epoch.merkleRoot, ROOT_1);
        assertEq(epoch.totalAssetsIdr, 1000);
        assertEq(epoch.tempWaqfLiabilitiesIdr, 400);
        assertEq(epoch.netAssetsIdr, 600);
        assertEq(epoch.notarizer, notarizer);
    }

    function testFuzzPSAK412AccountingIdentity(
        uint128 tempLiabilities,
        uint128 netAssets,
        uint256 wrongDelta
    ) public {
        uint256 totalAssets = uint256(tempLiabilities) + uint256(netAssets);

        vm.prank(notarizer);
        uint256 epochId = registry.notarizeEpoch(
            "FUZZ-PERIOD",
            ROOT_2,
            totalAssets,
            uint256(tempLiabilities),
            uint256(netAssets),
            20000,
            keccak256("fuzz-db")
        );
        IWaqfAuditRegistry.AuditEpoch memory epoch = registry.getEpoch(epochId);
        assertEq(epoch.totalAssetsIdr, epoch.tempWaqfLiabilitiesIdr + epoch.netAssetsIdr);

        vm.assume(wrongDelta > 0 && wrongDelta <= type(uint256).max - totalAssets);
        vm.prank(notarizer);
        vm.expectRevert(WaqfAuditRegistry.PSAK412BalanceMismatch.selector);
        registry.notarizeEpoch(
            "FUZZ-BAD",
            ROOT_2,
            totalAssets + wrongDelta,
            uint256(tempLiabilities),
            uint256(netAssets),
            20000,
            keccak256("fuzz-db")
        );
    }

    function testFuzzSortedPairOrderCommutativity(bytes memory payloadA, bytes memory payloadB) public view {
        bytes32 leafA = registry.computeLeaf(payloadA);
        bytes32 leafB = registry.computeLeaf(payloadB);

        (bytes32 left, bytes32 right) = leafA <= leafB ? (leafA, leafB) : (leafB, leafA);
        bytes32 expectedRoot = sha256(abi.encodePacked(uint8(0x01), left, right));

        bytes32[] memory proofForA = new bytes32[](1);
        proofForA[0] = leafB;
        bytes32[] memory proofForB = new bytes32[](1);
        proofForB[0] = leafA;

        assertTrue(registry.verifyInclusionProof(expectedRoot, leafA, proofForA));
        assertTrue(registry.verifyInclusionProof(expectedRoot, leafB, proofForB));
    }
}
