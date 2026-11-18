# -*- coding: utf-8 -*-
{
    "name": "WAQF DAO PSAK 412 Merkle Oracle",
    "version": "20.0.1.0.0",
    "category": "Accounting/Waqf",
    "summary": (
        "Publish deterministic PSAK 412 Merkle roots and UU PDP privacy-shielded "
        "audit bundles from Odoo 20.0 to Ethereum L2"
    ),
    "author": "Yayasan Amal Produktif Indonesia, PT Produktif Indonesia Berdaya",
    "website": "https://github.com/waqf-dao",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "waqf_core",
        "l10n_id_waqf_psak112",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "views/waqf_dao_notarization_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
