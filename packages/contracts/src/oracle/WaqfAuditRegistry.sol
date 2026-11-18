// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AccessRoles} from "../libraries/AccessRoles.sol";
import {IWaqfAuditRegistry} from "../interfaces/IWaqfProtocol.sol";

/// @title WaqfAuditRegistry
/// @notice Append-only notarization registry for Odoo ERP PSAK 412 financial snapshots and SHA-256 Merkle proofs.
/// @dev Enforces PSAK 412 balance sheet identity (Assets = Temporary Waqf Liabilities + Net Waqf Assets)
///      and implements bit-for-bit cross-language SHA-256 domain-separated sorted-pair Merkle verification.
contract WaqfAuditRegistry is AccessRoles, IWaqfAuditRegistry {
    AuditEpoch[] private _epochs;
    mapping(bytes32 periodKey => uint256[] epochIds) private _periodEpochIds;

    event EpochNotarized(
        uint256 indexed epochId,
        string periodCode,
        bytes32 indexed merkleRoot,
        uint256 totalAssetsIdr,
        uint256 tempWaqfLiabilitiesIdr,
        uint256 netAssetsIdr,
        uint256 sroiRatioBps,
        bytes32 odooDbHash,
        uint256 timestamp,
        address indexed notarizer
    );

    error PSAK412BalanceMismatch();
    error EmptyPeriodCode();
    error ZeroMerkleRoot();
    error ZeroOdooDbHash();
    error EpochNotFound(uint256 epochId);

    constructor(address admin, address initialNotarizer) {
        if (admin == address(0) || initialNotarizer == address(0)) revert ZeroAddress();
        _setRoleAdmin(NOTARIZER_ROLE, DEFAULT_ADMIN_ROLE);
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(NOTARIZER_ROLE, initialNotarizer);
    }

    /// @notice Appends an immutable PSAK 412 audit epoch notarizing the ERP state and Merkle root.
    function notarizeEpoch(
        string calldata periodCode,
        bytes32 merkleRoot,
        uint256 totalAssetsIdr,
        uint256 tempWaqfLiabilitiesIdr,
        uint256 netAssetsIdr,
        uint256 sroiRatioBps,
        bytes32 odooDbHash
    ) external onlyRole(NOTARIZER_ROLE) returns (uint256 epochId) {
        if (bytes(periodCode).length == 0) revert EmptyPeriodCode();
        if (merkleRoot == bytes32(0)) revert ZeroMerkleRoot();
        if (odooDbHash == bytes32(0)) revert ZeroOdooDbHash();

        // Overflow-safe PSAK 412 accounting identity check:
        // Total Assets == Temporary Waqf Liabilities + Net Waqf Assets
        if (totalAssetsIdr < tempWaqfLiabilitiesIdr || totalAssetsIdr - tempWaqfLiabilitiesIdr != netAssetsIdr) {
            revert PSAK412BalanceMismatch();
        }

        epochId = _epochs.length;
        _epochs.push(
            AuditEpoch({
                periodCode: periodCode,
                merkleRoot: merkleRoot,
                totalAssetsIdr: totalAssetsIdr,
                tempWaqfLiabilitiesIdr: tempWaqfLiabilitiesIdr,
                netAssetsIdr: netAssetsIdr,
                sroiRatioBps: sroiRatioBps,
                odooDbHash: odooDbHash,
                timestamp: block.timestamp,
                notarizer: msg.sender
            })
        );
        _periodEpochIds[keccak256(bytes(periodCode))].push(epochId);

        emit EpochNotarized(
            epochId,
            periodCode,
            merkleRoot,
            totalAssetsIdr,
            tempWaqfLiabilitiesIdr,
            netAssetsIdr,
            sroiRatioBps,
            odooDbHash,
            block.timestamp,
            msg.sender
        );
    }

    /// @inheritdoc IWaqfAuditRegistry
    function computeLeaf(bytes memory payload) public pure override returns (bytes32) {
        bytes32 inner = sha256(payload);
        return sha256(abi.encodePacked(uint8(0x00), inner));
    }

    /// @inheritdoc IWaqfAuditRegistry
    function verifyInclusionProof(
        bytes32 root,
        bytes32 leaf,
        bytes32[] calldata proof
    ) public pure override returns (bool) {
        bytes32 computed = leaf;
        uint256 len = proof.length;
        for (uint256 i = 0; i < len; ) {
            bytes32 sibling = proof[i];
            if (computed <= sibling) {
                computed = sha256(abi.encodePacked(uint8(0x01), computed, sibling));
            } else {
                computed = sha256(abi.encodePacked(uint8(0x01), sibling, computed));
            }
            unchecked {
                ++i;
            }
        }
        return computed == root;
    }

    /// @inheritdoc IWaqfAuditRegistry
    function verifyNotarizedLeaf(
        uint256 epochId,
        bytes32 leaf,
        bytes32[] calldata proof
    ) external view override returns (bool) {
        if (epochId >= _epochs.length) revert EpochNotFound(epochId);
        return verifyInclusionProof(_epochs[epochId].merkleRoot, leaf, proof);
    }

    /// @notice Convenience helper computing the canonical leaf from UTF-8 payload bytes and verifying against `epochId`.
    function verifyNotarizedPayload(
        uint256 epochId,
        bytes memory payload,
        bytes32[] calldata proof
    ) external view returns (bool) {
        if (epochId >= _epochs.length) revert EpochNotFound(epochId);
        bytes32 leaf = computeLeaf(payload);
        return verifyInclusionProof(_epochs[epochId].merkleRoot, leaf, proof);
    }

    function epochCount() external view returns (uint256) {
        return _epochs.length;
    }

    function getEpoch(uint256 epochId) external view returns (AuditEpoch memory) {
        if (epochId >= _epochs.length) revert EpochNotFound(epochId);
        return _epochs[epochId];
    }

    function getEpochIdsForPeriod(string calldata periodCode) external view returns (uint256[] memory) {
        return _periodEpochIds[keccak256(bytes(periodCode))];
    }
}
