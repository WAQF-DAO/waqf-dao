import React, { useEffect, useState } from 'react';
import {
  AlertTriangle,
  Binary,
  CheckCircle2,
  Database,
  FileCode2,
  RotateCcw,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import { CANONICAL_AUDIT_LEAVES, Lang } from '../data/genesisData';
import { UI_COPY } from '../i18n/translations';
import {
  computeLeafHash,
  computeMerkleRoot,
  generateInclusionProof,
  LeafVerificationResult,
  tracePayloadVerification,
} from '../utils/merkleVerify';

interface TabMerkleVerifierProps {
  lang: Lang;
}

interface GenesisTreeState {
  anchoredRoot: string;
  leafHashes: string[];
  proofs: string[][];
}

export const TabMerkleVerifier: React.FC<TabMerkleVerifierProps> = ({ lang }) => {
  const t = UI_COPY[lang].merkle;

  const [selectedIdx, setSelectedIdx] = useState<number>(0);
  const [editedPayload, setEditedPayload] = useState<string>(CANONICAL_AUDIT_LEAVES[0].payload);
  const [treeState, setTreeState] = useState<GenesisTreeState | null>(null);
  const [trace, setTrace] = useState<LeafVerificationResult | null>(null);

  // Build the canonical 5-leaf Merkle tree on mount using native WebCrypto SHA-256
  useEffect(() => {
    let active = true;
    (async () => {
      const leafHashes = await Promise.all(
        CANONICAL_AUDIT_LEAVES.map((item) => computeLeafHash(item.payload)),
      );
      const anchoredRoot = await computeMerkleRoot(leafHashes);
      const proofs = await Promise.all(
        leafHashes.map((_, idx) => generateInclusionProof(leafHashes, idx)),
      );
      if (active) {
        setTreeState({ anchoredRoot, leafHashes, proofs });
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  // Recompute WebCrypto SHA-256 verification trace whenever selected leaf or edited payload changes
  useEffect(() => {
    if (!treeState) return;
    let active = true;
    const proof = treeState.proofs[selectedIdx] ?? [];
    (async () => {
      const result = await tracePayloadVerification(
        treeState.anchoredRoot,
        editedPayload,
        proof,
      );
      if (active) {
        setTrace(result);
      }
    })();
    return () => {
      active = false;
    };
  }, [treeState, selectedIdx, editedPayload]);

  const selectedLeaf = CANONICAL_AUDIT_LEAVES[selectedIdx];
  const currentProof = treeState?.proofs[selectedIdx] ?? [];

  const handleSelectLeaf = (idx: number) => {
    setSelectedIdx(idx);
    setEditedPayload(CANONICAL_AUDIT_LEAVES[idx].payload);
  };

  const handleInjectTamper = () => {
    // Flip a single numeric character or append a space to simulate subtle tampering
    const digitMatch = editedPayload.match(/[0-8]/);
    if (digitMatch && digitMatch.index !== undefined) {
      const i = digitMatch.index;
      const nextDigit = String(Number(editedPayload[i]) + 1);
      setEditedPayload(editedPayload.slice(0, i) + nextDigit + editedPayload.slice(i + 1));
    } else {
      setEditedPayload(`${editedPayload} `);
    }
  };

  const handleRestore = () => {
    setEditedPayload(selectedLeaf.payload);
  };

  const verified = trace?.verified ?? false;

  return (
    <div className="stack">
      <div className="section-head">
        <h2>{t.heading}</h2>
        <p>{t.subheading}</p>
      </div>

      {/* Leaf Selector Strip */}
      <div className="parchment-card">
        <div className="card-header">
          <h3 className="card-title">
            <Database size={18} color="#108458" />
            {t.selectLeafTitle}
          </h3>
          {treeState && (
            <span className="badge badge--gold mono">
              5 Leaves · Root {treeState.anchoredRoot.slice(0, 12)}...{treeState.anchoredRoot.slice(-6)}
            </span>
          )}
        </div>

        <div className="pools-grid">
          {CANONICAL_AUDIT_LEAVES.map((leaf, idx) => {
            const active = idx === selectedIdx;
            return (
              <button
                key={leaf.id}
                type="button"
                className={`pool-card ${active ? 'selected' : ''}`}
                onClick={() => handleSelectLeaf(idx)}
              >
                <div className="pool-card__top">
                  <span className="pool-ticker">#{idx} · {leaf.id}</span>
                  <span className="badge badge--emerald">{leaf.docType}</span>
                </div>
                <h4 className="pool-name">{leaf.title[lang]}</h4>
                <div className="mono" style={{ fontSize: '0.72rem', color: '#4b5e57' }}>
                  {leaf.odooModel}
                </div>
                <div className="mono" style={{ fontSize: '0.7rem', color: '#61746d' }}>
                  {leaf.erpReference}
                </div>
              </button>
            );
          })}
        </div>

        <div className="callout callout--gold" style={{ marginTop: 14 }}>
          <Binary size={18} style={{ flexShrink: 0 }} />
          <div style={{ fontSize: '0.8rem' }}>{t.oddNodeNote}</div>
        </div>
      </div>

      {/* Interactive Verifier Grid */}
      <div className="grid-2">
        {/* Left: Canonical Payload Editor */}
        <div className="dark-panel">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <FileCode2 size={18} color="#ecc774" />
                {t.payloadTitle}
              </h3>
              <p className="card-subtitle mono">{selectedLeaf.erpReference}</p>
            </div>
            <span className={`badge ${verified ? 'badge--emerald-dark' : 'badge--crimson-dark'}`}>
              {verified ? (
                <>
                  <CheckCircle2 size={13} />
                  {t.verifiedBadge}
                </>
              ) : (
                <>
                  <AlertTriangle size={13} />
                  {t.tamperBadge}
                </>
              )}
            </span>
          </div>

          <textarea
            aria-label={t.payloadTitle}
            className="textarea-field"
            rows={7}
            value={editedPayload}
            onChange={(e) => setEditedPayload(e.target.value)}
          />

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginTop: 12 }}>
            <button type="button" className="btn btn--danger" onClick={handleInjectTamper}>
              <Zap size={14} />
              {t.tamperBtn}
            </button>
            <button type="button" className="btn btn--gold" onClick={handleRestore}>
              <RotateCcw size={14} />
              {t.resetPayloadBtn}
            </button>
          </div>

          <div style={{ marginTop: 16 }}>
            <div style={{ fontSize: '0.76rem', color: '#a6bab3', fontWeight: 700, marginBottom: 6 }}>
              {t.proofArrayLabel} ({currentProof.length} {currentProof.length === 1 ? 'sibling' : 'siblings'})
            </div>
            {currentProof.length === 0 ? (
              <div className="hash-box">[] (single-node tree)</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {currentProof.map((sib, idx) => (
                  <div key={idx} className="hash-box" style={{ fontSize: '0.73rem' }}>
                    <span style={{ color: '#ecc774' }}>proof[{idx}]:</span> {sib}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: Cryptographic Verification Output & Step Trace */}
        <div className="parchment-card">
          <div className="card-header">
            <h3 className="card-title">
              <ShieldCheck size={18} color={verified ? '#108458' : '#c2333a'} />
              WebCrypto SHA-256 Digest &amp; Proof Trace
            </h3>
            <span className={`badge ${verified ? 'badge--emerald' : 'badge--crimson'}`}>
              {verified ? t.verifiedBadge : t.tamperBadge}
            </span>
          </div>

          {trace && (
            <div className="stack" style={{ gap: 10 }}>
              <div>
                <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#3b4f48', marginBottom: 4 }}>
                  {t.innerHashLabel}
                </div>
                <div className="hash-box">{trace.innerHash}</div>
              </div>

              <div>
                <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#3b4f48', marginBottom: 4 }}>
                  {t.leafHashLabel}
                </div>
                <div className={`hash-box ${verified ? '' : 'hash-box--mismatch'}`}>{trace.leafHash}</div>
              </div>

              <div>
                <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#3b4f48', marginBottom: 4 }}>
                  {t.anchoredRootLabel}
                </div>
                <div className="hash-box">{trace.expectedRoot}</div>
              </div>

              <div>
                <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#3b4f48', marginBottom: 4 }}>
                  {t.computedRootLabel}
                </div>
                <div className={`hash-box ${verified ? '' : 'hash-box--mismatch'}`}>
                  {trace.computedRoot}
                </div>
              </div>

              <div style={{ marginTop: 6 }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#11221d', marginBottom: 6 }}>
                  {t.stepTraceTitle}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {trace.steps.map((st) => (
                    <div
                      key={st.step}
                      style={{
                        padding: '9px 11px',
                        borderRadius: 8,
                        background: '#f2ecdf',
                        border: '1px solid #dfd6c3',
                        fontSize: '0.74rem',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700 }}>
                        <span>Level Pair Step #{st.step}</span>
                        <span className="mono" style={{ color: '#61746d' }}>
                          {st.swapped ? 'lex sort: sibling <= current' : 'lex sort: current <= sibling'}
                        </span>
                      </div>
                      <div className="mono" style={{ marginTop: 4, color: '#3b4f48', wordBreak: 'break-all' }}>
                        sha256(0x01 || {st.leftHex.slice(0, 12)}.. || {st.rightHex.slice(0, 12)}..) →{' '}
                        <strong style={{ color: '#0b6643' }}>{st.outputHex}</strong>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
