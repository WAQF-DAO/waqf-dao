// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AccessRoles} from "../libraries/AccessRoles.sol";
import {IERC20} from "../libraries/IERC20.sol";
import {SafeERC20} from "../libraries/SafeERC20.sol";
import {ReentrancyGuard} from "../libraries/ReentrancyGuard.sol";
import {IPSAK412WaterfallSplitter} from "../interfaces/IWaqfProtocol.sol";

/// @title PSAK412WaterfallSplitter
/// @notice Deterministic realized-cash yield waterfall enforcing UU No. 41/2004 & PSAK 412 distribution caps.
/// @dev Enforces:
///      1. Nazhir operational fee <= 10.00% (1000 bps) of realized cash yield.
///      2. Mauquf 'Alaih (beneficiaries) allocation >= 50.00% (5000 bps).
///      3. Total waterfall bps == 10000 (100.00%).
///      4. Mauquf 'Alaih funds stay in escrow until released with a non-zero BAST attestation hash.
contract PSAK412WaterfallSplitter is AccessRoles, ReentrancyGuard, IPSAK412WaterfallSplitter {
    using SafeERC20 for IERC20;

    uint16 public constant BPS_DENOMINATOR = 10_000;
    uint16 public constant MAX_NAZHIR_FEE_BPS = 1_000;
    uint16 public constant MIN_MAUQUF_ALAIH_BPS = 5_000;

    // Nautera Genesis Preset (40.0% Sinking Fund / 50.5% Mauquf 'Alaih / 9.5% Nazhir)
    uint16 public constant DEFAULT_SINKING_FUND_BPS = 4_000;
    uint16 public constant DEFAULT_MAUQUF_ALAIH_BPS = 5_050;
    uint16 public constant DEFAULT_NAZHIR_FEE_BPS = 950;

    IERC20 public immutable reserveAsset;
    address public sinkingFundReserve;
    address public nazhirTreasury;

    uint16 public sinkingFundBps;
    uint16 public mauqufAlaihBps;
    uint16 public nazhirFeeBps;

    uint256 public totalYieldDistributed;
    uint256 public totalSinkingDistributed;
    uint256 public totalEscrowedMauqufAlaih;
    uint256 public totalMauqufAlaihReleased;
    uint256 public totalNazhirDistributed;

    mapping(bytes32 poolCode => uint256 escrowed) public escrowedMauqufAlaih;
    mapping(bytes32 poolCode => uint256 released) public releasedMauqufAlaih;
    mapping(bytes32 poolCode => uint256 sinkingTotal) public poolSinkingDistributed;
    mapping(bytes32 poolCode => uint256 nazhirTotal) public poolNazhirDistributed;

    struct DisbursementRecord {
        bytes32 poolCode;
        address beneficiary;
        uint256 amount;
        bytes32 bastAttestationHash;
        uint256 timestamp;
        address releasedBy;
    }

    DisbursementRecord[] private _disbursements;

    event WaterfallConfigured(uint16 sinkingFundBps, uint16 mauqufAlaihBps, uint16 nazhirFeeBps);
    event TreasuryAddressesUpdated(address indexed sinkingFundReserve, address indexed nazhirTreasury);
    event YieldDistributed(
        bytes32 indexed poolCode,
        uint256 realizedCashAmount,
        uint256 sinkingAmount,
        uint256 mauqufEscrowAmount,
        uint256 nazhirFeeAmount,
        address indexed sender
    );
    event MauqufAlaihReleased(
        bytes32 indexed poolCode,
        address indexed beneficiary,
        uint256 amount,
        bytes32 indexed bastAttestationHash,
        address releasedBy
    );

    error NazhirFeeExceedsStatutoryCap();
    error MauqufAlaihBelowMinimum();
    error InvalidWaterfallBasisPoints();
    error InvalidPoolCode();
    error ZeroAmount();
    error MissingBastAttestation();
    error InsufficientMauqufEscrow(bytes32 poolCode, uint256 requested, uint256 available);
    error DisbursementNotFound(uint256 index);

    constructor(
        address admin,
        address reserveAssetAddress,
        address sinkingFundReserveAddress,
        address nazhirTreasuryAddress,
        uint16 initialSinkingFundBps,
        uint16 initialMauqufAlaihBps,
        uint16 initialNazhirFeeBps
    ) {
        if (
            admin == address(0) ||
            reserveAssetAddress == address(0) ||
            sinkingFundReserveAddress == address(0) ||
            nazhirTreasuryAddress == address(0)
        ) {
            revert ZeroAddress();
        }

        reserveAsset = IERC20(reserveAssetAddress);
        sinkingFundReserve = sinkingFundReserveAddress;
        nazhirTreasury = nazhirTreasuryAddress;

        _setRoleAdmin(NAZHIR_ADMIN_ROLE, DEFAULT_ADMIN_ROLE);
        _setRoleAdmin(IMPACT_VALIDATOR_ROLE, DEFAULT_ADMIN_ROLE);
        _setRoleAdmin(GOVERNOR_ROLE, DEFAULT_ADMIN_ROLE);

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(NAZHIR_ADMIN_ROLE, admin);

        _validateAndSetWaterfall(initialSinkingFundBps, initialMauqufAlaihBps, initialNazhirFeeBps);
        emit TreasuryAddressesUpdated(sinkingFundReserveAddress, nazhirTreasuryAddress);
    }

    /// @notice Updates the PSAK 412 waterfall split basis points while strictly enforcing statutory caps.
    function setWaterfallConfig(
        uint16 newSinkingFundBps,
        uint16 newMauqufAlaihBps,
        uint16 newNazhirFeeBps
    ) external {
        if (!hasRole(DEFAULT_ADMIN_ROLE, msg.sender) && !hasRole(GOVERNOR_ROLE, msg.sender)) {
            revert AccessControlUnauthorizedAccount(msg.sender, GOVERNOR_ROLE);
        }
        _validateAndSetWaterfall(newSinkingFundBps, newMauqufAlaihBps, newNazhirFeeBps);
    }

    /// @notice Updates destination addresses for sinking fund reserve and Nazhir treasury.
    function setTreasuryAddresses(address newSinkingFundReserve, address newNazhirTreasury) external {
        if (!hasRole(DEFAULT_ADMIN_ROLE, msg.sender) && !hasRole(GOVERNOR_ROLE, msg.sender)) {
            revert AccessControlUnauthorizedAccount(msg.sender, GOVERNOR_ROLE);
        }
        if (newSinkingFundReserve == address(0) || newNazhirTreasury == address(0)) {
            revert ZeroAddress();
        }
        sinkingFundReserve = newSinkingFundReserve;
        nazhirTreasury = newNazhirTreasury;
        emit TreasuryAddressesUpdated(newSinkingFundReserve, newNazhirTreasury);
    }

    /// @inheritdoc IPSAK412WaterfallSplitter
    function distributeYield(bytes32 poolCode, uint256 realizedCashAmount) external override nonReentrant {
        if (poolCode == bytes32(0)) revert InvalidPoolCode();
        if (realizedCashAmount == 0) revert ZeroAmount();

        reserveAsset.safeTransferFrom(msg.sender, address(this), realizedCashAmount);

        // Round Nazhir and Sinking Fund down; any integer division dust goes to Mauquf 'Alaih escrow
        // ensuring Nazhir NEVER exceeds 10.00% even by 1 wei and 100% of cash is conserved.
        uint256 sinkingAmount = (realizedCashAmount * sinkingFundBps) / BPS_DENOMINATOR;
        uint256 nazhirAmount = (realizedCashAmount * nazhirFeeBps) / BPS_DENOMINATOR;
        uint256 mauqufAmount = realizedCashAmount - sinkingAmount - nazhirAmount;

        totalYieldDistributed += realizedCashAmount;
        totalSinkingDistributed += sinkingAmount;
        totalEscrowedMauqufAlaih += mauqufAmount;
        totalNazhirDistributed += nazhirAmount;

        poolSinkingDistributed[poolCode] += sinkingAmount;
        escrowedMauqufAlaih[poolCode] += mauqufAmount;
        poolNazhirDistributed[poolCode] += nazhirAmount;

        emit YieldDistributed(
            poolCode,
            realizedCashAmount,
            sinkingAmount,
            mauqufAmount,
            nazhirAmount,
            msg.sender
        );

        if (sinkingAmount > 0) {
            reserveAsset.safeTransfer(sinkingFundReserve, sinkingAmount);
        }
        if (nazhirAmount > 0) {
            reserveAsset.safeTransfer(nazhirTreasury, nazhirAmount);
        }
    }

    /// @notice Releases escrowed Mauquf 'Alaih yield to a verified beneficiary upon BAST attestation.
    function releaseMauqufAlaih(
        bytes32 poolCode,
        address beneficiary,
        uint256 amount,
        bytes32 bastAttestationHash
    ) external nonReentrant {
        if (!hasRole(IMPACT_VALIDATOR_ROLE, msg.sender) && !hasRole(NAZHIR_ADMIN_ROLE, msg.sender)) {
            revert AccessControlUnauthorizedAccount(msg.sender, IMPACT_VALIDATOR_ROLE);
        }
        if (poolCode == bytes32(0)) revert InvalidPoolCode();
        if (beneficiary == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        if (bastAttestationHash == bytes32(0)) revert MissingBastAttestation();

        uint256 available = escrowedMauqufAlaih[poolCode];
        if (amount > available) {
            revert InsufficientMauqufEscrow(poolCode, amount, available);
        }

        escrowedMauqufAlaih[poolCode] = available - amount;
        totalEscrowedMauqufAlaih -= amount;
        releasedMauqufAlaih[poolCode] += amount;
        totalMauqufAlaihReleased += amount;

        _disbursements.push(
            DisbursementRecord({
                poolCode: poolCode,
                beneficiary: beneficiary,
                amount: amount,
                bastAttestationHash: bastAttestationHash,
                timestamp: block.timestamp,
                releasedBy: msg.sender
            })
        );

        emit MauqufAlaihReleased(poolCode, beneficiary, amount, bastAttestationHash, msg.sender);

        reserveAsset.safeTransfer(beneficiary, amount);
    }

    function disbursementCount() external view returns (uint256) {
        return _disbursements.length;
    }

    function getDisbursement(uint256 index) external view returns (DisbursementRecord memory) {
        if (index >= _disbursements.length) revert DisbursementNotFound(index);
        return _disbursements[index];
    }

    function _validateAndSetWaterfall(
        uint16 newSinkingFundBps,
        uint16 newMauqufAlaihBps,
        uint16 newNazhirFeeBps
    ) private {
        if (newNazhirFeeBps > MAX_NAZHIR_FEE_BPS) {
            revert NazhirFeeExceedsStatutoryCap();
        }
        if (newMauqufAlaihBps < MIN_MAUQUF_ALAIH_BPS) {
            revert MauqufAlaihBelowMinimum();
        }
        if (uint256(newSinkingFundBps) + uint256(newMauqufAlaihBps) + uint256(newNazhirFeeBps) != BPS_DENOMINATOR) {
            revert InvalidWaterfallBasisPoints();
        }

        sinkingFundBps = newSinkingFundBps;
        mauqufAlaihBps = newMauqufAlaihBps;
        nazhirFeeBps = newNazhirFeeBps;

        emit WaterfallConfigured(newSinkingFundBps, newMauqufAlaihBps, newNazhirFeeBps);
    }
}
