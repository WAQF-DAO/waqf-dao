// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IERC20} from "../src/libraries/IERC20.sol";

interface IVmScript {
    function startBroadcast() external;
    function startBroadcast(uint256 privateKey) external;
    function stopBroadcast() external;
    function addr(uint256 privateKey) external pure returns (address);
    function envOr(string calldata name, address defaultValue) external view returns (address);
    function envOr(string calldata name, uint256 defaultValue) external view returns (uint256);
}

/// @title LocalHalalReserveToken
/// @notice Minimal ERC-20 halal stablecoin used ONLY when deploying to a local sandbox without an existing reserve token.
contract LocalHalalReserveToken is IERC20 {
    string public constant name = "Indonesian Rupiah Halal Reserve";
    string public constant symbol = "IDRX";
    uint8 public constant decimals = 6;

    uint256 public override totalSupply;
    mapping(address account => uint256 balance) public override balanceOf;
    mapping(address owner => mapping(address spender => uint256 amount)) public override allowance;

    constructor(address initialHolder, uint256 initialSupply) {
        totalSupply = initialSupply;
        balanceOf[initialHolder] = initialSupply;
        emit Transfer(address(0), initialHolder, initialSupply);
    }

    function transfer(address to, uint256 value) external override returns (bool) {
        require(balanceOf[msg.sender] >= value, "Insufficient balance");
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }

    function approve(address spender, uint256 value) external override returns (bool) {
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }

    function transferFrom(address from, address to, uint256 value) external override returns (bool) {
        require(balanceOf[from] >= value, "Insufficient balance");
        uint256 allowed = allowance[from][msg.sender];
        if (allowed != type(uint256).max) {
            require(allowed >= value, "Insufficient allowance");
            allowance[from][msg.sender] = allowed - value;
        }
        balanceOf[from] -= value;
        balanceOf[to] += value;
        emit Transfer(from, to, value);
        return true;
    }
}
