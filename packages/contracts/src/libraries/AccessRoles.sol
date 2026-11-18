// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title AccessRoles
/// @notice Role-based access control and institutional role identifiers for WAQF DAO.
abstract contract AccessRoles {
    bytes32 public constant DEFAULT_ADMIN_ROLE = 0x00;
    bytes32 public constant NAZHIR_ADMIN_ROLE = keccak256("NAZHIR_ADMIN_ROLE");
    bytes32 public constant SSB_ROLE = keccak256("SSB_ROLE");
    bytes32 public constant NOTARIZER_ROLE = keccak256("NOTARIZER_ROLE");
    bytes32 public constant APPRAISER_ROLE = keccak256("APPRAISER_ROLE");
    bytes32 public constant IMPACT_VALIDATOR_ROLE = keccak256("IMPACT_VALIDATOR_ROLE");
    bytes32 public constant AI_CIO_SENTINEL_ROLE = keccak256("AI_CIO_SENTINEL_ROLE");
    bytes32 public constant GOVERNOR_ROLE = keccak256("GOVERNOR_ROLE");
    bytes32 public constant REGISTRAR_ROLE = keccak256("REGISTRAR_ROLE");

    struct RoleData {
        mapping(address account => bool) hasRole;
        bytes32 adminRole;
    }

    mapping(bytes32 role => RoleData) private _roles;

    event RoleAdminChanged(bytes32 indexed role, bytes32 indexed previousAdminRole, bytes32 indexed newAdminRole);
    event RoleGranted(bytes32 indexed role, address indexed account, address indexed sender);
    event RoleRevoked(bytes32 indexed role, address indexed account, address indexed sender);

    error AccessControlUnauthorizedAccount(address account, bytes32 neededRole);
    error AccessControlBadConfirmation();
    error ZeroAddress();

    modifier onlyRole(bytes32 role) {
        _checkRole(role, msg.sender);
        _;
    }

    function hasRole(bytes32 role, address account) public view virtual returns (bool) {
        return _roles[role].hasRole[account];
    }

    function getRoleAdmin(bytes32 role) public view virtual returns (bytes32) {
        return _roles[role].adminRole;
    }

    function grantRole(bytes32 role, address account) public virtual onlyRole(getRoleAdmin(role)) {
        if (account == address(0)) revert ZeroAddress();
        _grantRole(role, account);
    }

    function revokeRole(bytes32 role, address account) public virtual onlyRole(getRoleAdmin(role)) {
        _revokeRole(role, account);
    }

    function renounceRole(bytes32 role, address callerConfirmation) public virtual {
        if (callerConfirmation != msg.sender) {
            revert AccessControlBadConfirmation();
        }
        _revokeRole(role, msg.sender);
    }

    function _checkRole(bytes32 role, address account) internal view virtual {
        if (!hasRole(role, account)) {
            revert AccessControlUnauthorizedAccount(account, role);
        }
    }

    function _setRoleAdmin(bytes32 role, bytes32 adminRole) internal virtual {
        bytes32 previousAdminRole = getRoleAdmin(role);
        _roles[role].adminRole = adminRole;
        emit RoleAdminChanged(role, previousAdminRole, adminRole);
    }

    function _grantRole(bytes32 role, address account) internal virtual returns (bool) {
        if (!hasRole(role, account)) {
            _roles[role].hasRole[account] = true;
            emit RoleGranted(role, account, msg.sender);
            return true;
        }
        return false;
    }

    function _revokeRole(bytes32 role, address account) internal virtual returns (bool) {
        if (hasRole(role, account)) {
            _roles[role].hasRole[account] = false;
            emit RoleRevoked(role, account, msg.sender);
            return true;
        }
        return false;
    }
}
