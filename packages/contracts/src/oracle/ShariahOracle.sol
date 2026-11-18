// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AccessRoles} from "../libraries/AccessRoles.sol";
import {IShariahOracle} from "../interfaces/IWaqfProtocol.sol";

/// @title ShariahOracle
/// @notice On-chain whitelist registry for Shariah-audited RWA/yield adapters and independent Istibdal appraisals.
/// @dev Enforces separation between accredited independent appraisers (APPRAISER_ROLE) and Shariah Supervisory Board (SSB_ROLE).
contract ShariahOracle is AccessRoles, IShariahOracle {
    struct AdapterMetadata {
        bool approved;
        uint256 updatedAt;
        bytes32 fatwaHash;
        address approvedBy;
        string category;
    }

    mapping(address adapter => AdapterMetadata) private _adapters;
    mapping(bytes32 assetId => AppraisalRecord) private _appraisals;

    event AdapterApprovalUpdated(
        address indexed adapter,
        bool approved,
        bytes32 indexed fatwaHash,
        string category,
        address indexed reviewer
    );
    event AppraisalSubmitted(
        bytes32 indexed assetId,
        uint256 appraisedValue,
        uint16 expectedAnnualYieldBps,
        uint256 expiresAt,
        address indexed appraiser,
        bytes32 reportHash
    );
    event AppraisalApproved(bytes32 indexed assetId, address indexed ssbMember, uint256 expiresAt);
    event AppraisalRevoked(bytes32 indexed assetId, address indexed ssbMember);

    error InvalidAssetId();
    error InvalidAppraisedValue();
    error InvalidAppraisalExpiry(uint256 expiresAt, uint256 currentTimestamp);
    error InvalidReportHash();
    error AppraisalNotFound(bytes32 assetId);
    error AppraisalAlreadyExpired(bytes32 assetId, uint256 expiresAt);

    constructor(address admin, address ssbMultisig) {
        if (admin == address(0) || ssbMultisig == address(0)) revert ZeroAddress();
        _setRoleAdmin(SSB_ROLE, DEFAULT_ADMIN_ROLE);
        _setRoleAdmin(APPRAISER_ROLE, DEFAULT_ADMIN_ROLE);
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(SSB_ROLE, ssbMultisig);
    }

    /// @notice Whitelists or revokes a Shariah-audited RWA or yield adapter.
    function setAdapterApproval(
        address adapter,
        bool approved,
        bytes32 fatwaHash,
        string calldata category
    ) external onlyRole(SSB_ROLE) {
        if (adapter == address(0)) revert ZeroAddress();
        _adapters[adapter] = AdapterMetadata({
            approved: approved,
            updatedAt: block.timestamp,
            fatwaHash: fatwaHash,
            approvedBy: msg.sender,
            category: category
        });
        emit AdapterApprovalUpdated(adapter, approved, fatwaHash, category, msg.sender);
    }

    /// @notice Submits an independent valuation and expected yield appraisal for an asset targeted for Istibdal.
    /// @dev Automatically clears `shariahApproved` so any revised valuation requires fresh SSB sign-off.
    function submitAppraisal(
        bytes32 assetId,
        uint256 appraisedValue,
        uint16 expectedAnnualYieldBps,
        uint256 expiresAt,
        bytes32 reportHash
    ) external onlyRole(APPRAISER_ROLE) {
        if (assetId == bytes32(0)) revert InvalidAssetId();
        if (appraisedValue == 0) revert InvalidAppraisedValue();
        // forge-lint: disable-next-line(block-timestamp)
        if (expiresAt <= block.timestamp) revert InvalidAppraisalExpiry(expiresAt, block.timestamp);
        if (reportHash == bytes32(0)) revert InvalidReportHash();

        _appraisals[assetId] = AppraisalRecord({
            appraisedValue: appraisedValue,
            expectedAnnualYieldBps: expectedAnnualYieldBps,
            appraiser: msg.sender,
            shariahApproved: false,
            expiresAt: expiresAt,
            appraisedAt: block.timestamp,
            reportHash: reportHash
        });

        emit AppraisalSubmitted(
            assetId,
            appraisedValue,
            expectedAnnualYieldBps,
            expiresAt,
            msg.sender,
            reportHash
        );
    }

    /// @notice Countersigns an unexpired independent appraisal for Istibdal eligibility.
    function approveAppraisal(bytes32 assetId) external onlyRole(SSB_ROLE) {
        AppraisalRecord storage rec = _appraisals[assetId];
        if (rec.appraisedValue == 0) revert AppraisalNotFound(assetId);
        // forge-lint: disable-next-line(block-timestamp)
        if (rec.expiresAt <= block.timestamp) revert AppraisalAlreadyExpired(assetId, rec.expiresAt);

        rec.shariahApproved = true;
        emit AppraisalApproved(assetId, msg.sender, rec.expiresAt);
    }

    /// @notice Revokes Shariah approval for an asset appraisal.
    function revokeAppraisal(bytes32 assetId) external onlyRole(SSB_ROLE) {
        AppraisalRecord storage rec = _appraisals[assetId];
        if (rec.appraisedValue == 0) revert AppraisalNotFound(assetId);

        rec.shariahApproved = false;
        emit AppraisalRevoked(assetId, msg.sender);
    }

    /// @inheritdoc IShariahOracle
    function isAdapterApproved(address adapter) external view override returns (bool) {
        return _adapters[adapter].approved;
    }

    /// @notice Returns full adapter metadata.
    function getAdapterMetadata(address adapter) external view returns (AdapterMetadata memory) {
        return _adapters[adapter];
    }

    /// @inheritdoc IShariahOracle
    function getAppraisal(bytes32 assetId) external view override returns (AppraisalRecord memory) {
        return _appraisals[assetId];
    }

    /// @inheritdoc IShariahOracle
    function isAppraisalValid(bytes32 assetId) external view override returns (bool) {
        AppraisalRecord storage rec = _appraisals[assetId];
        // forge-lint: disable-next-line(block-timestamp)
        return rec.shariahApproved && rec.appraisedValue > 0 && rec.expiresAt > block.timestamp;
    }
}
