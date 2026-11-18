SHELL := /bin/bash
export PATH := /root/.foundry/bin:/home/amalproduktif/.nvm/versions/node/v22.23.4/bin:/root/.local/bin:$(PATH)

.PHONY: test test-contracts test-oracle test-sentinel test-odoo build-explorer audit-hygiene

test: test-contracts test-oracle test-sentinel test-odoo build-explorer audit-hygiene

test-contracts:
	cd packages/contracts && forge test -vv

test-oracle:
	cd packages/oracle-bridge && python3 -m unittest discover -s tests -v

test-sentinel:
	cd packages/ai-cio-sentinel && python3 -m unittest discover -s tests -v

test-odoo:
	python3 -m compileall -q odoo-addons/waqf_dao_oracle

build-explorer:
	cd apps/explorer && npm run typecheck && npm run test:merkle && npm run build

audit-hygiene:
	python3 scripts/audit_hygiene.py
