// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AccessRoles} from "../libraries/AccessRoles.sol";
import {IERC20} from "../libraries/IERC20.sol";
import {SafeERC20} from "../libraries/SafeERC20.sol";
import {ReentrancyGuard} from "../libraries/ReentrancyGuard.sol";
import {
    IShariahOracle,
    IPSAK412WaterfallSplitter,
    IWaqfPrincipalVault
} from "../interfaces/IWaqfProtocol.sol";

/// @title WaqfPrincipalVault
/// @notice Multi-pool endowment vault implementing AAOIFI Shariah Standard No. 60 custody invariants.
/// @dev Enforces:
///      - Mu'abbad (Perpetual Waqf): permanently locked principal with ZERO admin drain or arbitrary withdrawal.
///      - Mu'aqqat (Temporary Cash Waqf): time-locked principal redeemable at 100% nominal value post-maturity.
///      - Istibdal (Asset Substitution): requires ShariahOracle approval, unexpired appraisal, non-decreasing value & yield.
///      - Zero-Burn Anti-Spam Capture: forfeited governance deposits become permanent Mu'abbad principal.
contract WaqfPrincipalVault is AccessRoles, ReentrancyGuard, IWaqfPrincipalVault {
    using SafeERC20 for IERC20;

    bytes32 public constant POOL_WPUD = 0x5750554400000000000000000000000000000000000000000000000000000000; // "WPUD"
    bytes32 public constant POOL_WPUM = 0x5750554d00000000000000000000000000000000000000000000000000000000; // "WPUM"
    bytes32 public constant POOL_WPAIR = 0x5750414952000000000000000000000000000000000000000000000000000000; // "WPAIR"
    bytes32 public constant POOL_WPPAL = 0x575050414c000000000000000000000000000000000000000000000000000000; // "WPPAL"
    bytes32 public constant POOL_WPMAS = 0x57504d4153000000000000000000000000000000000000000000000000000000; // "WPMAS"

    uint256 public constant MIN_TEMPORARY_LOCK = 1 days;

    enum DepositType {
        PERPETUAL,
        TEMPORARY
    }

    struct PoolInfo {
        bool exists;
        bool active;
        string name;
        bytes32 currentAssetId;
        address currentYieldAdapter;
        uint256 currentAppraisedValue;
        uint16 currentYieldBps;
        uint256 perpetualPrincipal;
        uint256 activeTemporaryPrincipal;
        uint256 deployedPrincipal;
        uint256 seizedGovernanceInflow;
        uint256 cumulativeYieldHarvested;
    }

    struct DepositRecord {
        uint256 depositId;
        bytes32 poolCode;
        address wakif;
        address beneficiary;
        uint256 principalAmount;
        uint256 depositedAt;
        uint256 maturityTimestamp;
        DepositType depositType;
        bool redeemed;
    }

    IERC20 private immutable _reserveAsset;
    IShariahOracle public shariahOracle;
    IPSAK412WaterfallSplitter public waterfallSplitter;

    uint256 public totalPerpetualPrincipal;
    uint256 public totalActiveTemporaryPrincipal;
    uint256 public totalDeployedPrincipal;

    bytes32[] private _poolCodes;
    mapping(bytes32 poolCode => PoolInfo) private _pools;
    mapping(bytes32 poolCode => mapping(address adapter => uint256 deployed)) public adapterDeployedPrincipal;

    uint256 private _nextDepositId;
    mapping(uint256 depositId => DepositRecord) private _deposits;

    event PoolConfigured(
        bytes32 indexed poolCode,
        string name,
        bytes32 indexed initialAssetId,
        address initialYieldAdapter,
        uint256 initialAppraisedValue,
        uint16 initialYieldBps
    );
    event PoolActiveStatusUpdated(bytes32 indexed poolCode, bool active);
    event PerpetualWaqfDeposited(
        uint256 indexed depositId,
        bytes32 indexed poolCode,
        address indexed wakif,
        uint256 amount
    );
    event TemporaryWaqfDeposited(
        uint256 indexed depositId,
        bytes32 indexed poolCode,
        address indexed wakif,
        address beneficiary,
        uint256 amount,
        uint256 maturityTimestamp
    );
    event TemporaryWaqfRedeemed(
        uint256 indexed depositId,
        bytes32 indexed poolCode,
        address indexed beneficiary,
        uint256 amount
    );
    event PrincipalDeployedToAdapter(bytes32 indexed poolCode, address indexed adapter, uint256 amount);
    event PrincipalRecalledFromAdapter(bytes32 indexed poolCode, address indexed adapter, uint256 amount);
    event IstibdalExecuted(
        bytes32 indexed poolCode,
        bytes32 indexed oldAssetId,
        bytes32 indexed newAssetId,
        address oldAdapter,
        address newAdapter,
        uint256 newAppraisedValue,
        uint16 newYieldBps,
        bytes32 ssbResolutionHash
    );
    event SeizedGovernanceDepositReceived(
        bytes32 indexed poolCode,
        address indexed governor,
        uint256 amount,
        uint256 newPoolPerpetualPrincipal
    );
    event RealizedYieldRouted(bytes32 indexed poolCode, uint256 yieldAmount, address indexed sender);
    event OracleUpdated(address indexed oldOracle, address indexed newOracle);
    event SplitterUpdated(address indexed oldSplitter, address indexed newSplitter);

    error InvalidPoolCode();
    error PoolAlreadyExists(bytes32 poolCode);
    error PoolNotFound(bytes32 poolCode);
    error PoolInactive(bytes32 poolCode);
    error ZeroAmount();
    error LockDurationTooShort(uint256 provided, uint256 minimum);
    error DepositNotFound(uint256 depositId);
    error PerpetualWaqfNonRedeemable();
    error DepositAlreadyRedeemed(uint256 depositId);
    error UnauthorizedRedemption(address caller);
    error TemporaryWaqfNotMatured(uint256 maturityTimestamp, uint256 currentTimestamp);
    error InsufficientLiquidPoolReserve(bytes32 poolCode, uint256 requested, uint256 available);
    error AdapterNotShariahApproved(address adapter);
    error InsufficientDeployedPrincipal(bytes32 poolCode, address adapter, uint256 requested, uint256 deployed);
    error InvalidAssetId();
    error MissingSsbResolution();
    error IstibdalNotShariahApproved(bytes32 assetId);
    error AppraisalExpired(bytes32 assetId, uint256 expiresAt);
    error IstibdalValueBelowPrincipal(uint256 newAppraisedValue, uint256 requiredPrincipalValue);
    error IstibdalYieldRegression(uint16 newYieldBps, uint16 currentYieldBps);
    error IncompleteTokenTransfer(uint256 expected, uint256 received);

    constructor(
        address admin,
        address reserveAssetAddress,
        address shariahOracleAddress,
        address waterfallSplitterAddress
    ) {
        if (
            admin == address(0) ||
            reserveAssetAddress == address(0) ||
            shariahOracleAddress == address(0) ||
            waterfallSplitterAddress == address(0)
        ) {
            revert ZeroAddress();
        }

        _reserveAsset = IERC20(reserveAssetAddress);
        shariahOracle = IShariahOracle(shariahOracleAddress);
        waterfallSplitter = IPSAK412WaterfallSplitter(waterfallSplitterAddress);

        _setRoleAdmin(NAZHIR_ADMIN_ROLE, DEFAULT_ADMIN_ROLE);
        _setRoleAdmin(GOVERNOR_ROLE, DEFAULT_ADMIN_ROLE);

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(NAZHIR_ADMIN_ROLE, admin);
    }

    function reserveAsset() external view override returns (address) {
        return address(_reserveAsset);
    }

    function poolExists(bytes32 poolCode) external view override returns (bool) {
        return _pools[poolCode].exists;
    }

    /// @notice Registers a new endowment pool (e.g., WPUD, WPUM, WPAIR, WPPAL, WPMAS).
    function configurePool(
        bytes32 poolCode,
        string calldata name,
        bytes32 initialAssetId,
        address initialYieldAdapter,
        uint256 initialAppraisedValue,
        uint16 initialYieldBps
    ) external onlyRole(NAZHIR_ADMIN_ROLE) {
        if (poolCode == bytes32(0)) revert InvalidPoolCode();
        if (_pools[poolCode].exists) revert PoolAlreadyExists(poolCode);
        if (initialYieldAdapter != address(0) && !shariahOracle.isAdapterApproved(initialYieldAdapter)) {
            revert AdapterNotShariahApproved(initialYieldAdapter);
        }

        _poolCodes.push(poolCode);
        _pools[poolCode] = PoolInfo({
            exists: true,
            active: true,
            name: name,
            currentAssetId: initialAssetId,
            currentYieldAdapter: initialYieldAdapter,
            currentAppraisedValue: initialAppraisedValue,
            currentYieldBps: initialYieldBps,
            perpetualPrincipal: 0,
            activeTemporaryPrincipal: 0,
            deployedPrincipal: 0,
            seizedGovernanceInflow: 0,
            cumulativeYieldHarvested: 0
        });

        emit PoolConfigured(
            poolCode,
            name,
            initialAssetId,
            initialYieldAdapter,
            initialAppraisedValue,
            initialYieldBps
        );
    }

    /// @notice Toggles whether a pool accepts new deposits (never allows withdrawal of Mu'abbad principal).
    function setPoolActive(bytes32 poolCode, bool active) external onlyRole(NAZHIR_ADMIN_ROLE) {
        if (!_pools[poolCode].exists) revert PoolNotFound(poolCode);
        _pools[poolCode].active = active;
        emit PoolActiveStatusUpdated(poolCode, active);
    }

    function setShariahOracle(address newOracle) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (newOracle == address(0)) revert ZeroAddress();
        address old = address(shariahOracle);
        shariahOracle = IShariahOracle(newOracle);
        emit OracleUpdated(old, newOracle);
    }

    function setWaterfallSplitter(address newSplitter) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (newSplitter == address(0)) revert ZeroAddress();
        address old = address(waterfallSplitter);
        waterfallSplitter = IPSAK412WaterfallSplitter(newSplitter);
        emit SplitterUpdated(old, newSplitter);
    }

    /// @notice Endows Perpetual Waqf (Mu'abbad) principal permanently locked in the vault.
    function depositPerpetualWaqf(
        bytes32 poolCode,
        uint256 amount
    ) external nonReentrant returns (uint256 depositId) {
        PoolInfo storage pool = _requireActivePool(poolCode);
        if (amount == 0) revert ZeroAmount();

        uint256 balanceBefore = _reserveAsset.balanceOf(address(this));
        _reserveAsset.safeTransferFrom(msg.sender, address(this), amount);
        uint256 received = _reserveAsset.balanceOf(address(this)) - balanceBefore;
        if (received < amount) revert IncompleteTokenTransfer(amount, received);

        pool.perpetualPrincipal += received;
        totalPerpetualPrincipal += received;

        depositId = ++_nextDepositId;
        _deposits[depositId] = DepositRecord({
            depositId: depositId,
            poolCode: poolCode,
            wakif: msg.sender,
            beneficiary: msg.sender,
            principalAmount: received,
            depositedAt: block.timestamp,
            maturityTimestamp: 0,
            depositType: DepositType.PERPETUAL,
            redeemed: false
        });

        emit PerpetualWaqfDeposited(depositId, poolCode, msg.sender, received);
    }

    /// @notice Endows Temporary Cash Waqf (Mu'aqqat) time-locked principal under AAOIFI SS 60 Cl. 2/4/12.
    function depositTemporaryWaqf(
        bytes32 poolCode,
        uint256 amount,
        uint256 lockDurationSeconds,
        address designatedHeir
    ) external nonReentrant returns (uint256 depositId) {
        PoolInfo storage pool = _requireActivePool(poolCode);
        if (amount == 0) revert ZeroAmount();
        if (lockDurationSeconds < MIN_TEMPORARY_LOCK) {
            revert LockDurationTooShort(lockDurationSeconds, MIN_TEMPORARY_LOCK);
        }

        address beneficiary = designatedHeir == address(0) ? msg.sender : designatedHeir;

        uint256 balanceBefore = _reserveAsset.balanceOf(address(this));
        _reserveAsset.safeTransferFrom(msg.sender, address(this), amount);
        uint256 received = _reserveAsset.balanceOf(address(this)) - balanceBefore;
        if (received < amount) revert IncompleteTokenTransfer(amount, received);

        uint256 maturity = block.timestamp + lockDurationSeconds;

        pool.activeTemporaryPrincipal += received;
        totalActiveTemporaryPrincipal += received;

        depositId = ++_nextDepositId;
        _deposits[depositId] = DepositRecord({
            depositId: depositId,
            poolCode: poolCode,
            wakif: msg.sender,
            beneficiary: beneficiary,
            principalAmount: received,
            depositedAt: block.timestamp,
            maturityTimestamp: maturity,
            depositType: DepositType.TEMPORARY,
            redeemed: false
        });

        emit TemporaryWaqfDeposited(depositId, poolCode, msg.sender, beneficiary, received, maturity);
    }

    /// @notice Redeems 100% nominal principal of a matured Temporary Cash Waqf (Mu'aqqat) to the wakif or designated heir.
    function redeemTemporaryWaqf(uint256 depositId) external nonReentrant {
        DepositRecord storage dep = _deposits[depositId];
        if (dep.principalAmount == 0) revert DepositNotFound(depositId);
        if (dep.depositType != DepositType.TEMPORARY) revert PerpetualWaqfNonRedeemable();
        if (dep.redeemed) revert DepositAlreadyRedeemed(depositId);
        if (msg.sender != dep.wakif && msg.sender != dep.beneficiary) {
            revert UnauthorizedRedemption(msg.sender);
        }
        // forge-lint: disable-next-line(block-timestamp)
        if (block.timestamp < dep.maturityTimestamp) {
            revert TemporaryWaqfNotMatured(dep.maturityTimestamp, block.timestamp);
        }

        PoolInfo storage pool = _pools[dep.poolCode];
        uint256 liquidPoolReserve = (pool.perpetualPrincipal + pool.activeTemporaryPrincipal) - pool.deployedPrincipal;
        if (liquidPoolReserve < dep.principalAmount) {
            revert InsufficientLiquidPoolReserve(dep.poolCode, dep.principalAmount, liquidPoolReserve);
        }

        dep.redeemed = true;
        pool.activeTemporaryPrincipal -= dep.principalAmount;
        totalActiveTemporaryPrincipal -= dep.principalAmount;

        emit TemporaryWaqfRedeemed(depositId, dep.poolCode, dep.beneficiary, dep.principalAmount);

        _reserveAsset.safeTransfer(dep.beneficiary, dep.principalAmount);
    }

    /// @notice Allocates liquid pool principal into a ShariahOracle-whitelisted RWA/yield adapter.
    function deployToApprovedAdapter(
        bytes32 poolCode,
        address adapter,
        uint256 amount
    ) external nonReentrant onlyRole(NAZHIR_ADMIN_ROLE) {
        PoolInfo storage pool = _requireActivePool(poolCode);
        if (amount == 0) revert ZeroAmount();
        if (adapter == address(0) || !shariahOracle.isAdapterApproved(adapter)) {
            revert AdapterNotShariahApproved(adapter);
        }

        uint256 liquidPoolReserve = (pool.perpetualPrincipal + pool.activeTemporaryPrincipal) - pool.deployedPrincipal;
        if (liquidPoolReserve < amount) {
            revert InsufficientLiquidPoolReserve(poolCode, amount, liquidPoolReserve);
        }

        pool.deployedPrincipal += amount;
        totalDeployedPrincipal += amount;
        adapterDeployedPrincipal[poolCode][adapter] += amount;

        emit PrincipalDeployedToAdapter(poolCode, adapter, amount);

        _reserveAsset.safeTransfer(adapter, amount);
    }

    /// @notice Recalls deployed principal from a yield adapter back into the vault's liquid reserve.
    function recallFromAdapter(
        bytes32 poolCode,
        address adapter,
        uint256 amount
    ) external nonReentrant onlyRole(NAZHIR_ADMIN_ROLE) {
        PoolInfo storage pool = _pools[poolCode];
        if (!pool.exists) revert PoolNotFound(poolCode);
        if (amount == 0) revert ZeroAmount();

        uint256 deployed = adapterDeployedPrincipal[poolCode][adapter];
        if (amount > deployed) {
            revert InsufficientDeployedPrincipal(poolCode, adapter, amount, deployed);
        }

        adapterDeployedPrincipal[poolCode][adapter] = deployed - amount;
        pool.deployedPrincipal -= amount;
        totalDeployedPrincipal -= amount;

        emit PrincipalRecalledFromAdapter(poolCode, adapter, amount);

        uint256 balanceBefore = _reserveAsset.balanceOf(address(this));
        // forge-lint: disable-next-line(arbitrary-send-erc20)
        _reserveAsset.safeTransferFrom(adapter, address(this), amount);
        uint256 received = _reserveAsset.balanceOf(address(this)) - balanceBefore;
        if (received < amount) revert IncompleteTokenTransfer(amount, received);
    }

    /// @notice Executes AAOIFI SS 60 Cl. 10/1/5 Istibdal (asset substitution) enforcing ShariahOracle sign-off,
    ///         unexpired independent appraisal, non-decreasing principal value, and non-decreasing yield rate.
    function executeIstibdal(
        bytes32 poolCode,
        bytes32 newAssetId,
        address newYieldAdapter,
        bytes32 ssbResolutionHash
    ) external nonReentrant {
        if (!hasRole(NAZHIR_ADMIN_ROLE, msg.sender) && !hasRole(GOVERNOR_ROLE, msg.sender)) {
            revert AccessControlUnauthorizedAccount(msg.sender, NAZHIR_ADMIN_ROLE);
        }

        PoolInfo storage pool = _requireActivePool(poolCode);
        if (newAssetId == bytes32(0)) revert InvalidAssetId();
        if (ssbResolutionHash == bytes32(0)) revert MissingSsbResolution();
        if (newYieldAdapter == address(0) || !shariahOracle.isAdapterApproved(newYieldAdapter)) {
            revert AdapterNotShariahApproved(newYieldAdapter);
        }

        IShariahOracle.AppraisalRecord memory appraisal = shariahOracle.getAppraisal(newAssetId);
        if (!appraisal.shariahApproved) {
            revert IstibdalNotShariahApproved(newAssetId);
        }
        // forge-lint: disable-next-line(block-timestamp)
        if (appraisal.expiresAt <= block.timestamp) {
            revert AppraisalExpired(newAssetId, appraisal.expiresAt);
        }

        uint256 currentPrincipalValue = _effectivePoolValue(pool);
        if (appraisal.appraisedValue < currentPrincipalValue) {
            revert IstibdalValueBelowPrincipal(appraisal.appraisedValue, currentPrincipalValue);
        }
        if (appraisal.expectedAnnualYieldBps < pool.currentYieldBps) {
            revert IstibdalYieldRegression(appraisal.expectedAnnualYieldBps, pool.currentYieldBps);
        }

        bytes32 oldAssetId = pool.currentAssetId;
        address oldAdapter = pool.currentYieldAdapter;

        pool.currentAssetId = newAssetId;
        pool.currentYieldAdapter = newYieldAdapter;
        pool.currentAppraisedValue = appraisal.appraisedValue;
        pool.currentYieldBps = appraisal.expectedAnnualYieldBps;

        emit IstibdalExecuted(
            poolCode,
            oldAssetId,
            newAssetId,
            oldAdapter,
            newYieldAdapter,
            appraisal.appraisedValue,
            appraisal.expectedAnnualYieldBps,
            ssbResolutionHash
        );
    }

    /// @inheritdoc IWaqfPrincipalVault
    function receiveSeizedGovernanceDeposit(
        bytes32 poolCode,
        uint256 amount
    ) external override nonReentrant onlyRole(GOVERNOR_ROLE) {
        PoolInfo storage pool = _requireActivePool(poolCode);
        if (amount == 0) revert ZeroAmount();

        uint256 balanceBefore = _reserveAsset.balanceOf(address(this));
        _reserveAsset.safeTransferFrom(msg.sender, address(this), amount);
        uint256 received = _reserveAsset.balanceOf(address(this)) - balanceBefore;
        if (received < amount) revert IncompleteTokenTransfer(amount, received);

        pool.perpetualPrincipal += received;
        pool.seizedGovernanceInflow += received;
        totalPerpetualPrincipal += received;

        emit SeizedGovernanceDepositReceived(poolCode, msg.sender, received, pool.perpetualPrincipal);
    }

    /// @notice Harvests/collects realized cash yield and routes 100% through PSAK412WaterfallSplitter.
    function routeRealizedYield(bytes32 poolCode, uint256 yieldAmount) external nonReentrant {
        PoolInfo storage pool = _pools[poolCode];
        if (!pool.exists) revert PoolNotFound(poolCode);
        if (yieldAmount == 0) revert ZeroAmount();

        uint256 balanceBefore = _reserveAsset.balanceOf(address(this));
        _reserveAsset.safeTransferFrom(msg.sender, address(this), yieldAmount);
        uint256 received = _reserveAsset.balanceOf(address(this)) - balanceBefore;
        if (received < yieldAmount) revert IncompleteTokenTransfer(yieldAmount, received);

        pool.cumulativeYieldHarvested += received;

        emit RealizedYieldRouted(poolCode, received, msg.sender);

        _reserveAsset.forceApprove(address(waterfallSplitter), received);
        // forge-lint: disable-next-line(reentrancy-no-eth)
        waterfallSplitter.distributeYield(poolCode, received);
    }

    function getPool(bytes32 poolCode) external view returns (PoolInfo memory) {
        if (!_pools[poolCode].exists) revert PoolNotFound(poolCode);
        return _pools[poolCode];
    }

    function getPoolCodes() external view returns (bytes32[] memory) {
        return _poolCodes;
    }

    function poolCount() external view returns (uint256) {
        return _poolCodes.length;
    }

    function getDeposit(uint256 depositId) external view returns (DepositRecord memory) {
        if (_deposits[depositId].principalAmount == 0) revert DepositNotFound(depositId);
        return _deposits[depositId];
    }

    function getPoolPrincipalValue(bytes32 poolCode) external view returns (uint256) {
        PoolInfo storage pool = _pools[poolCode];
        if (!pool.exists) revert PoolNotFound(poolCode);
        return _effectivePoolValue(pool);
    }

    function getPSAK412Balances()
        external
        view
        returns (uint256 totalAssets, uint256 tempWaqfLiabilities, uint256 netAssets)
    {
        tempWaqfLiabilities = totalActiveTemporaryPrincipal;
        netAssets = totalPerpetualPrincipal;
        totalAssets = tempWaqfLiabilities + netAssets;
    }

    function _requireActivePool(bytes32 poolCode) private view returns (PoolInfo storage pool) {
        pool = _pools[poolCode];
        if (!pool.exists) revert PoolNotFound(poolCode);
        if (!pool.active) revert PoolInactive(poolCode);
    }

    function _effectivePoolValue(PoolInfo storage pool) private view returns (uint256) {
        uint256 bookPrincipal = pool.perpetualPrincipal + pool.activeTemporaryPrincipal;
        return pool.currentAppraisedValue > bookPrincipal ? pool.currentAppraisedValue : bookPrincipal;
    }
}
