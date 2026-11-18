// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "../../src/libraries/IERC20.sol";

/// @title MockYieldAdapter
/// @notice Minimal RWA/yield adapter contract approving WaqfPrincipalVault to recall principal.
contract MockYieldAdapter {
    IERC20 public immutable reserveAsset;
    address public immutable vault;

    constructor(address reserveAssetAddress, address vaultAddress) {
        reserveAsset = IERC20(reserveAssetAddress);
        vault = vaultAddress;
    }

    function approveVaultRecall(uint256 amount) external {
        require(reserveAsset.approve(vault, amount), "Approve failed");
    }
}
