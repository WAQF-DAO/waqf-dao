# WAQF DAO

> **Institutional On-Chain Endowment Protocol under AAOIFI Shariah Standard No. 60, PSAK 412, and Dual-Chamber Digital Hisbah Governance.**

`WAQF DAO` bridges **1,400-year Islamic endowment jurisprudence** (*Tahbisul Ashli wa Tasbilul Manfa'ah*) with **audited real-world productive infrastructure** — connecting **Odoo 20.0 NPO/Waqf ERP** ledgers, **AI CIO forensic due diligence**, and **Ethereum Layer-2 programmable vaults** under statutory-ready governance.

Initiated from the production stack of **Yayasan Amal Produktif Indonesia (`STBPN BWI 3.3.00386`)**, **PT Produktif Indonesia Berdaya (`PT PIB`)**, and open-source Nazhir ecosystem initiatives (**Forum Wakaf Produktif / FWP** & **Asosiasi Nazhir Indonesia / ANI**).

## Monorepo Architecture

- `packages/contracts/` — Foundry Solidity smart contracts (`WaqfPrincipalVault`, `PSAK412WaterfallSplitter`, `DigitalHisbahGovernor`, `WaqfIdentitySBT`, `ShariahOracle`, `WaqfAuditRegistry`)
- `packages/oracle-bridge/` — Deterministic SHA-256 Merkle oracle, UU PDP privacy shield, and PSAK 412 snapshot relayer
- `packages/ai-cio-sentinel/` — 9-point AI CIO Forensic Due Diligence & Shariah Screening engine + mutation pool triage
- `odoo-addons/waqf_dao_oracle/` — Federated Odoo 20.0/19.0 addon for publishing PSAK 412 Merkle roots from `npo-odoo-docker`
- `apps/explorer/` — Institutional Web3 Explorer, PSAK 412 Waterfall Simulator, Digital Hisbah UI & WebCrypto Merkle Verifier
- `docs/` — Bilingual Institutional Whitepapers (`EN` & `ID`), `Fiqh of Code` audit matrix, `RAK DAO / ADGM` Dual-Nexus legal blueprint, and Federated Nazhir onboarding guide
