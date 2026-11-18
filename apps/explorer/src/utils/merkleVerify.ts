/**
 * Cross-Language Domain-Separated SHA-256 Merkle Tree Verifier
 *
 * Strictly implements the WAQF DAO specification using native WebCrypto:
 *  1. Leaf:     sha256(0x00 || sha256(utf8Bytes(payload)))
 *  2. Internal: sha256(0x01 || min(a, b) || max(a, b))  [raw unsigned byte order]
 *  3. Odd node: unpaired node at index 2k promoted UNCHANGED (no self-hash, no sibling emitted)
 *  4. Verify:   fold proof siblings via sorted hashPair and compare against expected root
 */

export interface ProofStepTrace {
  step: number;
  currentHex: string;
  siblingHex: string;
  leftHex: string;
  rightHex: string;
  swapped: boolean;
  outputHex: string;
}

export interface LeafVerificationResult {
  innerHash: string;
  leafHash: string;
  computedRoot: string;
  expectedRoot: string;
  verified: boolean;
  steps: ProofStepTrace[];
}

const textEncoder = new TextEncoder();

function getSubtleCrypto(): SubtleCrypto {
  const subtle = globalThis.crypto?.subtle;
  if (!subtle) {
    throw new Error('WebCrypto subtle.digest is unavailable in this environment.');
  }
  return subtle;
}

export function normalizeHex(hex: string): string {
  const clean = hex.trim().toLowerCase().replace(/^0x/, '');
  if (clean.length !== 64 || !/^[0-9a-f]{64}$/.test(clean)) {
    throw new Error(`Invalid 32-byte hex digest: "${hex}"`);
  }
  return `0x${clean}`;
}

export function hexToBytes(hex: string): Uint8Array<ArrayBuffer> {
  const normalized = normalizeHex(hex).slice(2);
  const buffer = new ArrayBuffer(32);
  const bytes = new Uint8Array(buffer);
  for (let i = 0; i < 32; i++) {
    bytes[i] = parseInt(normalized.slice(i * 2, i * 2 + 2), 16);
  }
  return bytes;
}

export function bytesToHex(bytes: Uint8Array): string {
  let out = '0x';
  for (let i = 0; i < bytes.length; i++) {
    out += bytes[i].toString(16).padStart(2, '0');
  }
  return out;
}

export function compareBytesLex(a: Uint8Array, b: Uint8Array): number {
  const len = Math.min(a.length, b.length);
  for (let i = 0; i < len; i++) {
    if (a[i] < b[i]) return -1;
    if (a[i] > b[i]) return 1;
  }
  return a.length - b.length;
}

export async function sha256Bytes(data: Uint8Array<ArrayBuffer>): Promise<Uint8Array<ArrayBuffer>> {
  const digest = await getSubtleCrypto().digest('SHA-256', data);
  return new Uint8Array(digest);
}

export async function computeInnerHash(payload: string): Promise<string> {
  const encoded = textEncoder.encode(payload);
  const buffer = new ArrayBuffer(encoded.byteLength);
  const payloadBytes = new Uint8Array(buffer);
  payloadBytes.set(encoded);
  const inner = await sha256Bytes(payloadBytes);
  return bytesToHex(inner);
}

/**
 * Leaf hash from canonical UTF-8 payload string:
 *   inner = sha256(payload_bytes)
 *   leaf  = sha256(0x00 || inner)
 */
export async function computeLeafHash(payload: string): Promise<string> {
  const innerHex = await computeInnerHash(payload);
  const innerBytes = hexToBytes(innerHex);

  const buffer = new ArrayBuffer(33);
  const prefixed = new Uint8Array(buffer);
  prefixed[0] = 0x00;
  prefixed.set(innerBytes, 1);

  const leaf = await sha256Bytes(prefixed);
  return bytesToHex(leaf);
}

/**
 * Internal node hash for two 32-byte child digests:
 *   Sort lexicographically by raw 32-byte unsigned byte order,
 *   then compute sha256(0x01 || left || right).
 */
export async function hashPair(aHex: string, bHex: string): Promise<string> {
  const aBytes = hexToBytes(aHex);
  const bBytes = hexToBytes(bHex);

  const aFirst = compareBytesLex(aBytes, bBytes) <= 0;
  const left = aFirst ? aBytes : bBytes;
  const right = aFirst ? bBytes : aBytes;

  const buffer = new ArrayBuffer(65);
  const prefixed = new Uint8Array(buffer);
  prefixed[0] = 0x01;
  prefixed.set(left, 1);
  prefixed.set(right, 33);

  const parent = await sha256Bytes(prefixed);
  return bytesToHex(parent);
}

/**
 * Compute Merkle root over 32-byte 0x-prefixed leaf digests.
 * Odd unpaired node at index 2k is promoted UNCHANGED without hashing.
 */
export async function computeMerkleRoot(leavesHex: string[]): Promise<string> {
  if (leavesHex.length === 0) {
    return `0x${'0'.repeat(64)}`;
  }
  let level = leavesHex.map(normalizeHex);

  while (level.length > 1) {
    const nextLevel: string[] = [];
    for (let i = 0; i + 1 < level.length; i += 2) {
      nextLevel.push(await hashPair(level[i], level[i + 1]));
    }
    if (level.length % 2 === 1) {
      nextLevel.push(level[level.length - 1]);
    }
    level = nextLevel;
  }

  return level[0];
}

/**
 * Generate inclusion proof for leaf at `index`.
 * Emits sibling hashes ONLY at levels where the node had a pair;
 * skips emitting a sibling when the node is the unpaired odd node at index 2k.
 */
export async function generateInclusionProof(
  leavesHex: string[],
  index: number,
): Promise<string[]> {
  if (leavesHex.length === 0) {
    throw new Error('Cannot generate inclusion proof for an empty Merkle tree.');
  }
  if (!Number.isInteger(index) || index < 0 || index >= leavesHex.length) {
    throw new Error(`Leaf index ${index} out of bounds [0, ${leavesHex.length - 1}].`);
  }

  let level = leavesHex.map(normalizeHex);
  let idx = index;
  const proof: string[] = [];

  while (level.length > 1) {
    const nextLevel: string[] = [];
    for (let i = 0; i + 1 < level.length; i += 2) {
      nextLevel.push(await hashPair(level[i], level[i + 1]));
    }

    const isOddUnpaired = level.length % 2 === 1 && idx === level.length - 1;
    if (level.length % 2 === 1) {
      nextLevel.push(level[level.length - 1]);
    }

    if (!isOddUnpaired) {
      const siblingIdx = idx % 2 === 0 ? idx + 1 : idx - 1;
      proof.push(level[siblingIdx]);
    }

    idx = Math.floor(idx / 2);
    level = nextLevel;
  }

  return proof;
}

/**
 * Verify a Merkle inclusion proof against an expected root.
 */
export async function verifyInclusionProof(
  rootHex: string,
  leafHex: string,
  proofHex: string[],
): Promise<boolean> {
  const expected = normalizeHex(rootHex);
  let computed = normalizeHex(leafHex);

  for (const sibling of proofHex) {
    computed = await hashPair(computed, normalizeHex(sibling));
  }

  return computed === expected;
}

/**
 * Detailed trace helper for the Odoo 20.0 ERP Merkle Audit Verifier UI.
 */
export async function tracePayloadVerification(
  expectedRootHex: string,
  payload: string,
  proofHex: string[],
): Promise<LeafVerificationResult> {
  const expectedRoot = normalizeHex(expectedRootHex);
  const innerHash = await computeInnerHash(payload);
  const leafHash = await computeLeafHash(payload);

  let computed = leafHash;
  const steps: ProofStepTrace[] = [];

  for (let i = 0; i < proofHex.length; i++) {
    const siblingHex = normalizeHex(proofHex[i]);
    const currentBytes = hexToBytes(computed);
    const siblingBytes = hexToBytes(siblingHex);
    const currentFirst = compareBytesLex(currentBytes, siblingBytes) <= 0;

    const leftHex = currentFirst ? computed : siblingHex;
    const rightHex = currentFirst ? siblingHex : computed;
    const outputHex = await hashPair(computed, siblingHex);

    steps.push({
      step: i + 1,
      currentHex: computed,
      siblingHex,
      leftHex,
      rightHex,
      swapped: !currentFirst,
      outputHex,
    });

    computed = outputHex;
  }

  return {
    innerHash,
    leafHash,
    computedRoot: computed,
    expectedRoot,
    verified: computed === expectedRoot,
    steps,
  };
}
