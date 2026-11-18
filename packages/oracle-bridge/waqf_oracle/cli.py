"""CLI entrypoints for WAQF DAO ERP Merkle Oracle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from .relayer import (
    DEFAULT_L2_CHAIN_ID,
    ZERO_ADDRESS,
    build_genesis_snapshot,
    build_notarization_payload,
    verify_fixture_dict,
    write_genesis_fixture,
)

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FIXTURE_PATH = PACKAGE_ROOT / "fixtures" / "genesis_epoch_2026_11.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="waqf-oracle",
        description="WAQF DAO PSAK 412 Merkle Oracle & UU PDP Privacy Shield CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser(
        "generate-genesis-fixture",
        help="Generate canonical Genesis Epoch 2026-11 PSAK 412 Merkle fixture JSON",
    )
    gen_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_FIXTURE_PATH,
        help=f"Output JSON file path (default: {DEFAULT_FIXTURE_PATH})",
    )

    ver_parser = subparsers.add_parser(
        "verify-fixture",
        help="Verify PSAK 412 invariants, Merkle root, and all inclusion proofs in a fixture",
    )
    ver_parser.add_argument(
        "--fixture",
        type=Path,
        default=DEFAULT_FIXTURE_PATH,
        help=f"Path to fixture JSON file (default: {DEFAULT_FIXTURE_PATH})",
    )

    prev_parser = subparsers.add_parser(
        "notarize-preview",
        help="Print deterministic WaqfAuditRegistry.sol notarization calldata preview",
    )
    prev_parser.add_argument(
        "--fixture",
        type=Path,
        default=None,
        help="Optional fixture path; if omitted, builds from Genesis Epoch snapshot",
    )
    prev_parser.add_argument(
        "--chain-id",
        type=int,
        default=DEFAULT_L2_CHAIN_ID,
        help=f"Target EVM L2 chain ID (default: {DEFAULT_L2_CHAIN_ID})",
    )
    prev_parser.add_argument(
        "--registry-address",
        type=str,
        default=ZERO_ADDRESS,
        help="Target WaqfAuditRegistry contract address",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate-genesis-fixture":
        written = write_genesis_fixture(args.output)
        fixture = json.loads(written.read_text(encoding="utf-8"))
        ok, errors = verify_fixture_dict(fixture)
        if not ok:
            print(f"ERROR: Generated fixture failed verification: {errors}", file=sys.stderr)
            return 1
        print(
            json.dumps(
                {
                    "status": "generated",
                    "output": str(written),
                    "epoch_code": fixture["epoch_code"],
                    "leaf_count": fixture["leaf_count"],
                    "merkle_root": fixture["merkle_root"],
                },
                indent=2,
            )
        )
        return 0

    if args.command == "verify-fixture":
        if not args.fixture.exists():
            print(f"ERROR: Fixture file not found: {args.fixture}", file=sys.stderr)
            return 1
        fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
        ok, errors = verify_fixture_dict(fixture)
        result = {
            "status": "verified" if ok else "failed",
            "fixture": str(args.fixture),
            "epoch_code": fixture.get("epoch_code"),
            "leaf_count": fixture.get("leaf_count"),
            "merkle_root": fixture.get("merkle_root"),
            "errors": errors,
        }
        print(json.dumps(result, indent=2))
        return 0 if ok else 1

    if args.command == "notarize-preview":
        if args.fixture is not None:
            fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
            payload = fixture["notarization_payload"]
            payload["merkle_root"] = fixture["merkle_root"]
            payload["leaf_count"] = fixture["leaf_count"]
        else:
            snapshot = build_genesis_snapshot()
            bundle = build_notarization_payload(
                snapshot,
                chain_id=args.chain_id,
                registry_address=args.registry_address,
                salt="waqf-dao-genesis-epoch-2026-11",
            )
            payload = {
                "epoch_code": bundle["epoch_code"],
                "epoch_id": bundle["epoch_id"],
                "chain_id": bundle["chain_id"],
                "registry_address": bundle["registry_address"],
                "contract_method": bundle["contract_method"],
                "merkle_root": bundle["merkle_root"],
                "leaf_count": bundle["leaf_count"],
                "metadata_hash": bundle["metadata_hash"],
                "abi_arguments": bundle["abi_arguments"],
                "abi_encoded_args_hex": bundle["abi_encoded_args_hex"],
                "cast_args": bundle["cast_args"],
            }
        print(json.dumps(payload, indent=2))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
