// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface Vm {
    function warp(uint256 newTimestamp) external;
    function getBlockTimestamp() external view returns (uint256);
    function prank(address msgSender) external;
    function startPrank(address msgSender) external;
    function stopPrank() external;
    function expectRevert() external;
    function expectRevert(bytes4 revertData) external;
    function expectRevert(bytes calldata revertData) external;
    function assume(bool condition) external pure;
    function addr(uint256 privateKey) external pure returns (address);
    function deal(address account, uint256 newBalance) external;
}

/// @title TestBase
/// @notice Minimal self-contained Foundry test harness with zero external submodule dependencies.
abstract contract TestBase {
    Vm internal constant vm = Vm(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    error AssertionFailed(string message);

    function fail(string memory message) internal pure {
        revert AssertionFailed(message);
    }

    function assertTrue(bool condition) internal pure {
        if (!condition) revert AssertionFailed("assertTrue failed");
    }

    function assertTrue(bool condition, string memory message) internal pure {
        if (!condition) revert AssertionFailed(message);
    }

    function assertFalse(bool condition) internal pure {
        if (condition) revert AssertionFailed("assertFalse failed");
    }

    function assertFalse(bool condition, string memory message) internal pure {
        if (condition) revert AssertionFailed(message);
    }

    function assertEq(uint256 a, uint256 b) internal pure {
        if (a != b) revert AssertionFailed("assertEq(uint256) failed");
    }

    function assertEq(uint256 a, uint256 b, string memory message) internal pure {
        if (a != b) revert AssertionFailed(message);
    }

    function assertEq(address a, address b) internal pure {
        if (a != b) revert AssertionFailed("assertEq(address) failed");
    }

    function assertEq(address a, address b, string memory message) internal pure {
        if (a != b) revert AssertionFailed(message);
    }

    function assertEq(bytes32 a, bytes32 b) internal pure {
        if (a != b) revert AssertionFailed("assertEq(bytes32) failed");
    }

    function assertEq(bytes32 a, bytes32 b, string memory message) internal pure {
        if (a != b) revert AssertionFailed(message);
    }

    function assertEq(bool a, bool b) internal pure {
        if (a != b) revert AssertionFailed("assertEq(bool) failed");
    }

    function assertEq(string memory a, string memory b) internal pure {
        if (keccak256(bytes(a)) != keccak256(bytes(b))) {
            revert AssertionFailed("assertEq(string) failed");
        }
    }

    function assertGe(uint256 a, uint256 b) internal pure {
        if (a < b) revert AssertionFailed("assertGe failed");
    }

    function assertLe(uint256 a, uint256 b) internal pure {
        if (a > b) revert AssertionFailed("assertLe failed");
    }

    function assertGt(uint256 a, uint256 b) internal pure {
        if (a <= b) revert AssertionFailed("assertGt failed");
    }

    function assertLt(uint256 a, uint256 b) internal pure {
        if (a >= b) revert AssertionFailed("assertLt failed");
    }

    function makeAddr(string memory label) internal pure returns (address) {
        return address(uint160(uint256(keccak256(bytes(label)))));
    }
}
