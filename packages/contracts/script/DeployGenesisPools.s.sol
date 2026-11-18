// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IVmScript, LocalHalalReserveToken} from "./LocalHalalReserveToken.sol";
import {WaqfIdentitySBT} from "../src/identity/WaqfIdentitySBT.sol";
import {ShariahOracle} from "../src/oracle/ShariahOracle.sol";
import {WaqfAuditRegistry} from "../src/oracle/WaqfAuditRegistry.sol";
import {PSAK412WaterfallSplitter} from "../src/vaults/PSAK412WaterfallSplitter.sol";
import {WaqfPrincipalVault} from "../src/vaults/WaqfPrincipalVault.sol";
import {DigitalHisbahGovernor} from "../src/governance/DigitalHisbahGovernor.sol";

/// @title ProtocolDeployer
/// @notice Reusable internal library for deploying and configuring the WAQF DAO stack and 5 Genesis Pools.
library ProtocolDeployer {
    struct ProtocolDeployment {
        address reserveAsset;
        WaqfIdentitySBT identitySBT;
        ShariahOracle shariahOracle;
        WaqfAuditRegistry auditRegistry;
        PSAK412WaterfallSplitter waterfallSplitter;
        WaqfPrincipalVault principalVault;
        DigitalHisbahGovernor governor;
    }

    function deployAndConfigure(
        address admin,
        address reserveAssetAddress,
        address ssbMultisig,
        address sinkingFundReserve,
        address nazhirTreasury,
        address notarizer
    ) internal returns (ProtocolDeployment memory d) {
        if (reserveAssetAddress == address(0)) {
            LocalHalalReserveToken token = new LocalHalalReserveToken(admin, 1_000_000_000e6);
            reserveAssetAddress = address(token);
        }

        d.reserveAsset = reserveAssetAddress;
        d.identitySBT = new WaqfIdentitySBT(admin, "WAQF DAO Institutional Credential", "WAQFSBT");
        d.shariahOracle = new ShariahOracle(admin, ssbMultisig);
        d.auditRegistry = new WaqfAuditRegistry(admin, notarizer);
        d.waterfallSplitter = new PSAK412WaterfallSplitter(
            admin,
            reserveAssetAddress,
            sinkingFundReserve,
            nazhirTreasury,
            4_000, // 40.0% Sinking Fund Reserve
            5_050, // 50.5% Mauquf 'Alaih Escrow
            950    //  9.5% Nazhir Fee (strictly <= 10.0% statutory cap)
        );
        d.principalVault = new WaqfPrincipalVault(
            admin,
            reserveAssetAddress,
            address(d.shariahOracle),
            address(d.waterfallSplitter)
        );
        d.governor = new DigitalHisbahGovernor(
            admin,
            ssbMultisig,
            address(d.identitySBT),
            address(d.principalVault),
            7 days,
            1_000e6,
            10
        );

        d.principalVault.grantRole(d.principalVault.GOVERNOR_ROLE(), address(d.governor));
        configureGenesisPools(d.principalVault);
    }

    function configureGenesisPools(WaqfPrincipalVault vault) internal {
        vault.configurePool(
            vault.POOL_WPUD(),
            "WPUD - Wakaf Produktif Usaha & Dagang",
            keccak256("GENESIS-ASSET-WPUD"),
            address(0),
            0,
            0
        );
        vault.configurePool(
            vault.POOL_WPUM(),
            "WPUM - Wakaf Produktif UMKM Nusantara",
            keccak256("GENESIS-ASSET-WPUM"),
            address(0),
            0,
            0
        );
        vault.configurePool(
            vault.POOL_WPAIR(),
            "WPAIR - Wakaf Produktif Air Bersih & Sanitasi",
            keccak256("GENESIS-ASSET-WPAIR"),
            address(0),
            0,
            0
        );
        vault.configurePool(
            vault.POOL_WPPAL(),
            "WPPAL - Wakaf Produktif Pangan & Agrikultur",
            keccak256("GENESIS-ASSET-WPPAL"),
            address(0),
            0,
            0
        );
        vault.configurePool(
            vault.POOL_WPMAS(),
            "WPMAS - Wakaf Produktif Masjid & Pemberdayaan Sosial",
            keccak256("GENESIS-ASSET-WPMAS"),
            address(0),
            0,
            0
        );
    }
}

/// @title DeployGenesisPools
/// @notice Foundry deployment script for WAQF DAO core contracts and the 5 Genesis Pools (WPUD, WPUM, WPAIR, WPPAL, WPMAS).
contract DeployGenesisPools {
    IVmScript internal constant VM = IVmScript(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function run() external returns (ProtocolDeployer.ProtocolDeployment memory deployment) {
        uint256 deployerKey = VM.envOr("PRIVATE_KEY", uint256(0));
        address configuredReserve = VM.envOr("RESERVE_ASSET_ADDRESS", address(0));
        address deployer = deployerKey != 0 ? VM.addr(deployerKey) : msg.sender;
        address ssbMultisig = VM.envOr("SSB_MULTISIG_ADDRESS", deployer);
        address sinkingFundReserve = VM.envOr("SINKING_FUND_ADDRESS", deployer);
        address nazhirTreasury = VM.envOr("NAZHIR_TREASURY_ADDRESS", deployer);
        address notarizer = VM.envOr("ORACLE_NOTARIZER_ADDRESS", deployer);

        if (deployerKey != 0) {
            VM.startBroadcast(deployerKey);
        } else {
            VM.startBroadcast();
        }

        deployment = ProtocolDeployer.deployAndConfigure(
            deployer,
            configuredReserve,
            ssbMultisig,
            sinkingFundReserve,
            nazhirTreasury,
            notarizer
        );

        VM.stopBroadcast();
    }
}
