=====================================
WAQF DAO PSAK 412 Merkle Oracle (Odoo)
=====================================

Odoo 20.0 (and 19.0) federated ERP bridge for **Yayasan Amal Produktif Indonesia (STBPN BWI 3.3.00386)**, **PT Produktif Indonesia Berdaya (PT PIB)**, **Forum Wakaf Produktif (FWP)**, and **Asosiasi Nazhir Indonesia (ANI)**.

This module builds UU PDP-compliant privacy-shielded canonical JSON leaves from PSAK 412 waqf ledgers, computes deterministic SHA-256 Merkle roots and inclusion proofs matching ``packages/oracle-bridge`` bit-for-bit, and generates ABI-ready payloads for ``WaqfAuditRegistry.sol``.

Dependencies
============

* ``base``
* ``mail``
* ``waqf_core``
* ``l10n_id_waqf_psak112``

Installation inside ``npo-odoo-docker``
=======================================

1. Mount the ``odoo-addons/waqf_dao_oracle`` directory into your ``npo-odoo-docker`` container extra-addons path (for example ``/mnt/extra-addons/waqf_dao_oracle``) in ``docker-compose.yml``:

   .. code-block:: yaml

      services:
        odoo:
          volumes:
            - ./odoo-addons/waqf_dao_oracle:/mnt/extra-addons/waqf_dao_oracle:ro
          environment:
            - WAQF_ORACLE_PDP_SALT=${WAQF_ORACLE_PDP_SALT}

2. Ensure ``/mnt/extra-addons`` is listed in ``addons_path`` inside ``odoo.conf``.

3. Install or upgrade the module inside ``npo-odoo-docker``:

   .. code-block:: bash

      docker compose exec odoo odoo \
        -d waqf_prod \
        --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons \
        -i waqf_dao_oracle \
        --stop-after-init

4. Restart the Odoo service and open **WAQF DAO Oracle -> PSAK 412 Notarizations**.

Workflow
========

1. Create or review the monthly **PSAK 412 Notarization** record (automatically drafted by ``ir.cron`` on a monthly interval).
2. Verify PSAK 412 invariants:

   * ``total_assets_idr == temp_waqf_liabilities_idr + net_assets_idr``
   * ``reconciliation_diff_idr == 0``
   * ``nazhir_cash_fee_ratio <= 0.10`` (Law No. 41/2004 cap)
   * ``mauquf_alaih_ratio >= 0.50``

3. Click **Generate Merkle Bundle** (``action_generate_merkle_bundle``) to produce the UU PDP privacy-shielded leaf manifest, Merkle root, per-leaf inclusion proofs, and ``WaqfAuditRegistry.sol`` ABI payload.
4. Submit the transaction to your target Ethereum L2 (e.g., Base Sepolia ``84532`` or Base Mainnet ``8453``), record ``l2_tx_hash``, and click **Mark On-Chain Notarized** followed by **Verify Merkle Bundle**.

License
=======

LGPL-3
