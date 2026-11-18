// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title IWaqfProtocol
/// @notice Shared interfaces and structs across WAQF DAO identity, oracle, vault, splitter, and governance modules.

interface IWaqfIdentitySBT {
    enum RoleBadge {
        NONE,
        WAKIF,
        NAZHIR_CERTIFIED,
        SHARIAH_BOARD,
        IMPACT_VALIDATOR
    }

    function hasRoleBadge(address account, RoleBadge badge) external view returns (bool);
    function isCredentialActive(address account) external view returns (bool);
    function getVotingWeight(address account) external view returns (uint256);
    function recordContributionUnits(address account, uint256 additionalUnits) external;
}

interface IShariahOracle {
    struct AppraisalRecord {
        uint256 appraisedValue;
        uint16 expectedAnnualYieldBps;
        address appraiser;
        bool shariahApproved;
        uint256 expiresAt;
        uint256 appraisedAt;
        bytes32 reportHash;
    }

    function isAdapterApproved(address adapter) external view returns (bool);
    function getAppraisal(bytes32 assetId) external view returns (AppraisalRecord memory);
    function isAppraisalValid(bytes32 assetId) external view returns (bool);
}

interface IWaqfAuditRegistry {
    struct AuditEpoch {
        string periodCode;
        bytes32 merkleRoot;
        uint256 totalAssetsIdr;
        uint256 tempWaqfLiabilitiesIdr;
        uint256 netAssetsIdr;
        uint256 sroiRatioBps;
        bytes32 odooDbHash;
        uint256 timestamp;
        address notarizer;
    }

    function computeLeaf(bytes memory payload) external pure returns (bytes32);
    function verifyInclusionProof(
        bytes32 root,
        bytes32 leaf,
        bytes32[] calldata proof
    ) external pure returns (bool);
    function verifyNotarizedLeaf(
        uint256 epochId,
        bytes32 leaf,
        bytes32[] calldata proof
    ) external view returns (bool);
}

interface IPSAK412WaterfallSplitter {
    function distributeYield(bytes32 poolCode, uint256 realizedCashAmount) external;
}

interface IWaqfPrincipalVault {
    function reserveAsset() external view returns (address);
    function poolExists(bytes32 poolCode) external view returns (bool);
    function receiveSeizedGovernanceDeposit(bytes32 poolCode, uint256 amount) external;
}
