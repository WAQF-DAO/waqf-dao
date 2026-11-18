import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import test from 'node:test';
import {
  computeLeafHash,
  computeMerkleRoot,
  generateInclusionProof,
  hashPair,
  tracePayloadVerification,
  verifyInclusionProof,
} from '../src/utils/merkleVerify.ts';

function refSha256(buf: Buffer): Buffer {
  return createHash('sha256').update(buf).digest();
}

function refLeaf(payload: string): string {
  const inner = refSha256(Buffer.from(payload, 'utf8'));
  const leaf = refSha256(Buffer.concat([Buffer.from([0x00]), inner]));
  return `0x${leaf.toString('hex')}`;
}

function refHashPair(aHex: string, bHex: string): string {
  const a = Buffer.from(aHex.replace(/^0x/, ''), 'hex');
  const b = Buffer.from(bHex.replace(/^0x/, ''), 'hex');
  const [left, right] = Buffer.compare(a, b) <= 0 ? [a, b] : [b, a];
  const parent = refSha256(Buffer.concat([Buffer.from([0x01]), left, right]));
  return `0x${parent.toString('hex')}`;
}

test('computeLeafHash matches domain-separated 0x00 || sha256(utf8)', async () => {
  const payloads = [
    '{"doc":"AIW-YAPI-2026-001","amount_idr":532400000}',
    'unicode-wakaf-produktif-✓',
    '',
  ];
  for (const p of payloads) {
    assert.equal(await computeLeafHash(p), refLeaf(p));
  }
});

test('hashPair sorts raw 32-byte digests lexicographically with 0x01 prefix', async () => {
  const a = await computeLeafHash('alpha');
  const b = await computeLeafHash('beta');
  assert.equal(await hashPair(a, b), refHashPair(a, b));
  assert.equal(await hashPair(b, a), refHashPair(a, b));
  assert.equal(await hashPair(a, b), await hashPair(b, a));
});

test('5-leaf odd-node Merkle tree promotes unpaired node unchanged and verifies all indices', async () => {
  const payloads = ['leaf-0', 'leaf-1', 'leaf-2', 'leaf-3', 'leaf-4'];
  const leaves = await Promise.all(payloads.map((p) => computeLeafHash(p)));

  // Manual reference for 5 leaves:
  // Level 0: [L0, L1, L2, L3, L4]
  // Level 1: [H(L0, L1), H(L2, L3), L4]  (L4 promoted unchanged)
  // Level 2: [H(H(L0, L1), H(L2, L3)), L4] (L4 promoted unchanged again)
  // Level 3: [H(H(H(L0, L1), H(L2, L3)), L4)]
  const h01 = refHashPair(leaves[0], leaves[1]);
  const h23 = refHashPair(leaves[2], leaves[3]);
  const h0123 = refHashPair(h01, h23);
  const expectedRoot = refHashPair(h0123, leaves[4]);

  const root = await computeMerkleRoot(leaves);
  assert.equal(root, expectedRoot);

  // Leaf 4 should have proof of length 1: [h0123] (skipping 2 unpaired levels!)
  const proof4 = await generateInclusionProof(leaves, 4);
  assert.deepEqual(proof4, [h0123]);

  for (let i = 0; i < leaves.length; i++) {
    const proof = await generateInclusionProof(leaves, i);
    const ok = await verifyInclusionProof(root, leaves[i], proof);
    assert.equal(ok, true, `Expected leaf ${i} to verify`);

    const tamperedLeaf = await computeLeafHash(`${payloads[i]}!`);
    const bad = await verifyInclusionProof(root, tamperedLeaf, proof);
    assert.equal(bad, false, `Expected tampered leaf ${i} to fail`);
  }
});

test('all tree sizes 1..9 verify every leaf and reject tampering', async () => {
  for (let n = 1; n <= 9; n++) {
    const payloads = Array.from({ length: n }, (_, i) => `record-${n}-${i}`);
    const leaves = await Promise.all(payloads.map((p) => computeLeafHash(p)));
    const root = await computeMerkleRoot(leaves);

    for (let i = 0; i < n; i++) {
      const proof = await generateInclusionProof(leaves, i);
      assert.equal(await verifyInclusionProof(root, leaves[i], proof), true);

      const trace = await tracePayloadVerification(root, payloads[i], proof);
      assert.equal(trace.verified, true);
      assert.equal(trace.computedRoot, root);
    }
  }
});
