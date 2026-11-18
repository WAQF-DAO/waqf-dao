"""Deterministic SHA-256 Merkle tree matching WAQF DAO cross-language specification.

Specification:
1. Leaf hash from canonical UTF-8 payload bytes:
   inner = sha256(payload_bytes)
   leaf  = sha256(0x00 || inner)
2. Internal node hash for two 32-byte child digests (a, b):
   Sort lexicographically by raw 32-byte unsigned byte order:
   (left, right) = (a, b) if a <= b else (b, a)
   parent = sha256(0x01 || left || right)
3. Odd node count at any tree level (length 2k + 1):
   Pair indices (0, 1), (2, 3), ..., (2k - 2, 2k - 1).
   Carry the odd unpaired node at index 2k UNCHANGED to the next level.
   Emit NO sibling in the inclusion proof when a node is carried unchanged.
4. Proof verification:
   Fold leaf with each sibling in sorted order via sha256(0x01 || left || right)
   and check equality with root.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Sequence

LEAF_DOMAIN: bytes = b"\x00"
NODE_DOMAIN: bytes = b"\x01"
DIGEST_BYTES: int = 32


def to_hex(digest: bytes) -> str:
    """Format a 32-byte digest as a lowercase 0x-prefixed 64-character hex string."""
    if not isinstance(digest, (bytes, bytearray)) or len(digest) != DIGEST_BYTES:
        raise ValueError(f"Expected {DIGEST_BYTES}-byte digest, got {type(digest).__name__}")
    return "0x" + bytes(digest).hex()


def from_hex(hex_str: str) -> bytes:
    """Parse a 32-byte digest from a hex string (with or without 0x prefix)."""
    if not isinstance(hex_str, str):
        raise TypeError(f"Expected str hex digest, got {type(hex_str).__name__}")
    cleaned = hex_str[2:] if hex_str.startswith(("0x", "0X")) else hex_str
    if len(cleaned) != DIGEST_BYTES * 2:
        raise ValueError(f"Expected 64 hex characters, got {len(cleaned)}")
    try:
        raw = bytes.fromhex(cleaned)
    except ValueError as exc:
        raise ValueError(f"Invalid hex digest: {hex_str}") from exc
    if len(raw) != DIGEST_BYTES:
        raise ValueError(f"Expected {DIGEST_BYTES} decoded bytes, got {len(raw)}")
    return raw


def _coerce_payload_bytes(payload: bytes | str) -> bytes:
    if isinstance(payload, str):
        return payload.encode("utf-8")
    if isinstance(payload, (bytes, bytearray, memoryview)):
        return bytes(payload)
    raise TypeError(f"Payload must be bytes or str, got {type(payload).__name__}")


def leaf_hash(payload: bytes | str) -> bytes:
    """Compute leaf = sha256(0x00 || sha256(payload_bytes))."""
    payload_bytes = _coerce_payload_bytes(payload)
    inner = hashlib.sha256(payload_bytes).digest()
    return hashlib.sha256(LEAF_DOMAIN + inner).digest()


def leaf_hash_hex(payload: bytes | str) -> str:
    """Compute 0x-prefixed hex leaf hash."""
    return to_hex(leaf_hash(payload))


def node_hash(left: bytes, right: bytes) -> bytes:
    """Compute sorted-pair internal node hash sha256(0x01 || min(a,b) || max(a,b))."""
    if not isinstance(left, (bytes, bytearray)) or len(left) != DIGEST_BYTES:
        raise ValueError("left child must be a 32-byte digest")
    if not isinstance(right, (bytes, bytearray)) or len(right) != DIGEST_BYTES:
        raise ValueError("right child must be a 32-byte digest")
    a = bytes(left)
    b = bytes(right)
    ordered_left, ordered_right = (a, b) if a <= b else (b, a)
    return hashlib.sha256(NODE_DOMAIN + ordered_left + ordered_right).digest()


@dataclass(frozen=True)
class MerkleTree:
    """Immutable deterministic Merkle tree supporting inclusion proof generation."""

    payloads: tuple[bytes, ...]
    leaves: tuple[bytes, ...]
    levels: tuple[tuple[bytes, ...], ...]

    @classmethod
    def from_payloads(cls, payloads: Sequence[str | bytes]) -> "MerkleTree":
        """Build a MerkleTree from one or more canonical UTF-8 / raw byte payloads."""
        if not payloads:
            raise ValueError("Cannot build Merkle tree from empty payloads")
        raw_payloads = tuple(_coerce_payload_bytes(p) for p in payloads)
        leaves = tuple(leaf_hash(p) for p in raw_payloads)
        return cls._build_from_leaves(raw_payloads, leaves)

    @classmethod
    def from_leaf_digests(cls, leaves: Sequence[bytes]) -> "MerkleTree":
        """Build a MerkleTree directly from pre-hashed 32-byte leaf digests."""
        if not leaves:
            raise ValueError("Cannot build Merkle tree from empty leaves")
        validated = tuple(bytes(leaf) for leaf in leaves)
        for leaf in validated:
            if len(leaf) != DIGEST_BYTES:
                raise ValueError(f"Every leaf digest must be {DIGEST_BYTES} bytes")
        return cls._build_from_leaves((), validated)

    @classmethod
    def _build_from_leaves(
        cls,
        raw_payloads: tuple[bytes, ...],
        leaves: tuple[bytes, ...],
    ) -> "MerkleTree":
        levels: list[tuple[bytes, ...]] = [leaves]
        current = leaves
        while len(current) > 1:
            next_level: list[bytes] = []
            limit = len(current) - (len(current) % 2)
            for idx in range(0, limit, 2):
                next_level.append(node_hash(current[idx], current[idx + 1]))
            if len(current) % 2 == 1:
                # Odd unpaired node at index 2k is promoted unchanged without hashing.
                next_level.append(current[-1])
            current = tuple(next_level)
            levels.append(current)
        return cls(payloads=raw_payloads, leaves=leaves, levels=tuple(levels))

    @property
    def root(self) -> bytes:
        """Return the 32-byte Merkle root digest."""
        return self.levels[-1][0]

    @property
    def root_hex(self) -> str:
        """Return the 0x-prefixed hex Merkle root."""
        return to_hex(self.root)

    @property
    def leaves_hex(self) -> list[str]:
        """Return 0x-prefixed hex strings for all leaves in index order."""
        return [to_hex(leaf) for leaf in self.leaves]

    @property
    def leaf_count(self) -> int:
        """Return number of leaves in the tree."""
        return len(self.leaves)

    def get_proof(self, index: int) -> list[str]:
        """Generate the 0x-prefixed hex inclusion proof for leaf at `index`."""
        if index < 0 or index >= len(self.leaves):
            raise IndexError(f"Leaf index {index} out of range [0, {len(self.leaves) - 1}]")
        proof: list[str] = []
        cursor = index
        # Iterate through all levels below the root level.
        for level in self.levels[:-1]:
            level_len = len(level)
            if cursor % 2 == 0:
                if cursor + 1 < level_len:
                    proof.append(to_hex(level[cursor + 1]))
                # Else: unpaired odd node at index 2k, carried unchanged -> emit NO sibling.
            else:
                proof.append(to_hex(level[cursor - 1]))
            cursor //= 2
        return proof

    def get_all_proofs(self) -> list[list[str]]:
        """Return inclusion proofs for every leaf in index order."""
        return [self.get_proof(idx) for idx in range(len(self.leaves))]

    def verify_leaf(self, index: int, payload: bytes | str) -> bool:
        """Verify that `payload` at `index` matches the tree root via its inclusion proof."""
        if index < 0 or index >= len(self.leaves):
            return False
        return verify_proof(self.root_hex, leaf_hash_hex(payload), self.get_proof(index))

    def to_dict(self) -> dict[str, Any]:
        """Serialize tree root, leaves, and proofs for JSON export."""
        return {
            "merkle_root": self.root_hex,
            "leaf_count": self.leaf_count,
            "leaves": self.leaves_hex,
            "proofs": self.get_all_proofs(),
        }


def build_tree(payloads: Sequence[str | bytes]) -> MerkleTree:
    """Build a deterministic MerkleTree from canonical UTF-8 strings or bytes."""
    return MerkleTree.from_payloads(payloads)


def get_proof(tree_or_payloads: MerkleTree | Sequence[str | bytes], index: int) -> list[str]:
    """Return inclusion proof (hex 0x...) for `index` from a MerkleTree or payload list."""
    tree = tree_or_payloads if isinstance(tree_or_payloads, MerkleTree) else build_tree(tree_or_payloads)
    return tree.get_proof(index)


def verify_proof(root_hex: str, leaf_hex: str, proof: Sequence[str]) -> bool:
    """Verify a Merkle inclusion proof against `root_hex` and `leaf_hex`."""
    try:
        expected_root = from_hex(root_hex)
        computed = from_hex(leaf_hex)
        siblings = [from_hex(sibling) for sibling in proof]
    except (TypeError, ValueError):
        return False

    for sibling in siblings:
        computed = node_hash(computed, sibling)
    return computed == expected_root
