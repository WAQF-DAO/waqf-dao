// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AccessRoles} from "../libraries/AccessRoles.sol";
import {IERC165, IERC5192} from "../libraries/IERC5192.sol";
import {IWaqfIdentitySBT} from "../interfaces/IWaqfProtocol.sol";

/// @title WaqfIdentitySBT
/// @notice ERC-5192 non-transferable Soulbound credential registry with role badges and capped quadratic voting weights.
/// @dev Prevents plutocratic governance capture by combining integer square-root scaling with a hard MAX_VOTING_WEIGHT cap.
contract WaqfIdentitySBT is AccessRoles, IERC165, IERC5192, IWaqfIdentitySBT {
    uint256 public constant BASE_VOTING_WEIGHT = 1;
    uint256 public constant MAX_VOTING_WEIGHT = 100;

    bytes4 private constant _INTERFACE_ID_ERC165 = 0x01ffc9a7;
    bytes4 private constant _INTERFACE_ID_ERC721 = 0x80ac58cd;
    bytes4 private constant _INTERFACE_ID_ERC721_METADATA = 0x5b5e139f;
    bytes4 private constant _INTERFACE_ID_ERC5192 = 0xb45a3c0e;

    string public name;
    string public symbol;

    struct Credential {
        uint256 tokenId;
        uint256 contributionUnits;
        uint256 issuedAt;
        uint8 roleMask;
        bool active;
        string metadataUri;
    }

    uint256 private _nextTokenId;
    mapping(address account => Credential) private _credentials;
    mapping(uint256 tokenId => address owner) private _owners;
    mapping(address owner => uint256 balance) private _balances;

    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);

    event CredentialIssued(
        uint256 indexed tokenId,
        address indexed account,
        RoleBadge indexed badge,
        uint256 contributionUnits
    );
    event RoleBadgeGranted(uint256 indexed tokenId, address indexed account, RoleBadge indexed badge);
    event RoleBadgeRevoked(uint256 indexed tokenId, address indexed account, RoleBadge indexed badge);
    event CredentialRevoked(uint256 indexed tokenId, address indexed account);
    event ContributionUnitsRecorded(address indexed account, uint256 addedUnits, uint256 totalUnits);

    error SoulboundNonTransferable();
    error InvalidRoleBadge();
    error CredentialDoesNotExist(uint256 tokenId);
    error CredentialNotActive(address account);

    constructor(address admin, string memory tokenName, string memory tokenSymbol) {
        if (admin == address(0)) revert ZeroAddress();
        name = tokenName;
        symbol = tokenSymbol;
        _setRoleAdmin(REGISTRAR_ROLE, DEFAULT_ADMIN_ROLE);
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(REGISTRAR_ROLE, admin);
    }

    /// @notice Issues a new Soulbound credential or adds a role badge and contribution units to an existing active SBT.
    function issueCredential(
        address to,
        RoleBadge badge,
        uint256 initialContributionUnits,
        string memory uri
    ) public onlyRole(REGISTRAR_ROLE) returns (uint256 tokenId) {
        if (to == address(0)) revert ZeroAddress();
        if (badge == RoleBadge.NONE) revert InvalidRoleBadge();

        Credential storage cred = _credentials[to];
        uint8 badgeBit = _badgeMask(badge);

        if (cred.tokenId == 0) {
            tokenId = ++_nextTokenId;
            cred.tokenId = tokenId;
            cred.issuedAt = block.timestamp;
            cred.active = true;
            cred.roleMask = badgeBit;
            cred.contributionUnits = initialContributionUnits;
            cred.metadataUri = uri;

            _owners[tokenId] = to;
            _balances[to] = 1;

            emit Transfer(address(0), to, tokenId);
            emit Locked(tokenId);
            emit CredentialIssued(tokenId, to, badge, initialContributionUnits);
        } else {
            tokenId = cred.tokenId;
            cred.active = true;
            cred.roleMask |= badgeBit;
            if (initialContributionUnits > 0) {
                cred.contributionUnits += initialContributionUnits;
            }
            if (bytes(uri).length > 0) {
                cred.metadataUri = uri;
            }

            emit RoleBadgeGranted(tokenId, to, badge);
            if (initialContributionUnits > 0) {
                emit ContributionUnitsRecorded(to, initialContributionUnits, cred.contributionUnits);
            }
        }
    }

    /// @notice Convenience overload issuing a Soulbound credential without custom URI override.
    function issueCredential(
        address to,
        RoleBadge badge,
        uint256 initialContributionUnits
    ) external onlyRole(REGISTRAR_ROLE) returns (uint256 tokenId) {
        return issueCredential(to, badge, initialContributionUnits, "");
    }

    /// @notice Records additional verified endowment contribution units for quadratic voting weight calculation.
    function recordContributionUnits(
        address account,
        uint256 additionalUnits
    ) external override onlyRole(REGISTRAR_ROLE) {
        Credential storage cred = _credentials[account];
        if (!cred.active || cred.tokenId == 0) revert CredentialNotActive(account);
        cred.contributionUnits += additionalUnits;
        emit ContributionUnitsRecorded(account, additionalUnits, cred.contributionUnits);
    }

    /// @notice Revokes a single role badge from a credential holder.
    function revokeRoleBadge(address account, RoleBadge badge) external onlyRole(REGISTRAR_ROLE) {
        if (badge == RoleBadge.NONE) revert InvalidRoleBadge();
        Credential storage cred = _credentials[account];
        if (cred.tokenId == 0 || !cred.active) revert CredentialNotActive(account);

        cred.roleMask &= ~_badgeMask(badge);
        if (cred.roleMask == 0) {
            cred.active = false;
        }
        emit RoleBadgeRevoked(cred.tokenId, account, badge);
    }

    /// @notice Fully revokes and burns a holder's Soulbound credential.
    function revokeCredential(address account) external onlyRole(REGISTRAR_ROLE) {
        Credential storage cred = _credentials[account];
        uint256 tokenId = cred.tokenId;
        if (tokenId == 0) revert CredentialNotActive(account);

        cred.active = false;
        cred.roleMask = 0;
        cred.tokenId = 0;
        delete _owners[tokenId];
        _balances[account] = 0;

        emit Unlocked(tokenId);
        emit Transfer(account, address(0), tokenId);
        emit CredentialRevoked(tokenId, account);
    }

    /// @notice Returns true if `account` holds an active SBT with `badge`.
    function hasRoleBadge(address account, RoleBadge badge) public view override returns (bool) {
        if (badge == RoleBadge.NONE) return false;
        Credential storage cred = _credentials[account];
        return cred.active && (cred.roleMask & _badgeMask(badge)) != 0;
    }

    /// @notice Returns true if `account` holds an active Soulbound credential with at least one role badge.
    function isCredentialActive(address account) public view override returns (bool) {
        Credential storage cred = _credentials[account];
        return cred.active && cred.roleMask != 0;
    }

    /// @notice Computes capped quadratic voting weight: min(MAX_VOTING_WEIGHT, 1 + floor(sqrt(contributionUnits))).
    function getVotingWeight(address account) public view override returns (uint256) {
        Credential storage cred = _credentials[account];
        if (!cred.active || cred.roleMask == 0) {
            return 0;
        }
        uint256 rawWeight = BASE_VOTING_WEIGHT + _sqrt(cred.contributionUnits);
        return rawWeight > MAX_VOTING_WEIGHT ? MAX_VOTING_WEIGHT : rawWeight;
    }

    /// @notice Returns full credential metadata for `account`.
    function getCredential(
        address account
    )
        external
        view
        returns (
            uint256 tokenId,
            uint8 roleMask,
            uint256 contributionUnits,
            uint256 issuedAt,
            bool active,
            string memory metadataUri
        )
    {
        Credential storage cred = _credentials[account];
        return (cred.tokenId, cred.roleMask, cred.contributionUnits, cred.issuedAt, cred.active, cred.metadataUri);
    }

    /// @inheritdoc IERC5192
    function locked(uint256 tokenId) external view override returns (bool) {
        if (_owners[tokenId] == address(0)) revert CredentialDoesNotExist(tokenId);
        return true;
    }

    function balanceOf(address owner) external view returns (uint256) {
        if (owner == address(0)) revert ZeroAddress();
        return _balances[owner];
    }

    function ownerOf(uint256 tokenId) external view returns (address owner) {
        owner = _owners[tokenId];
        if (owner == address(0)) revert CredentialDoesNotExist(tokenId);
    }

    function tokenURI(uint256 tokenId) external view returns (string memory) {
        address owner = _owners[tokenId];
        if (owner == address(0)) revert CredentialDoesNotExist(tokenId);
        return _credentials[owner].metadataUri;
    }

    function getApproved(uint256 tokenId) external view returns (address) {
        if (_owners[tokenId] == address(0)) revert CredentialDoesNotExist(tokenId);
        return address(0);
    }

    function isApprovedForAll(address, address) external pure returns (bool) {
        return false;
    }

    function approve(address, uint256) external pure {
        revert SoulboundNonTransferable();
    }

    function setApprovalForAll(address, bool) external pure {
        revert SoulboundNonTransferable();
    }

    function transferFrom(address, address, uint256) external pure {
        revert SoulboundNonTransferable();
    }

    function safeTransferFrom(address, address, uint256) external pure {
        revert SoulboundNonTransferable();
    }

    function safeTransferFrom(address, address, uint256, bytes calldata) external pure {
        revert SoulboundNonTransferable();
    }

    function supportsInterface(bytes4 interfaceId) external pure override returns (bool) {
        return
            interfaceId == _INTERFACE_ID_ERC165 ||
            interfaceId == _INTERFACE_ID_ERC721 ||
            interfaceId == _INTERFACE_ID_ERC721_METADATA ||
            interfaceId == _INTERFACE_ID_ERC5192;
    }

    function _badgeMask(RoleBadge badge) private pure returns (uint8) {
        return uint8(1) << uint8(badge);
    }

    function _sqrt(uint256 x) private pure returns (uint256 y) {
        if (x == 0) return 0;
        uint256 z = (x >> 1) + 1;
        y = x;
        while (z < y) {
            y = z;
            z = (x / z + z) / 2;
        }
    }
}
