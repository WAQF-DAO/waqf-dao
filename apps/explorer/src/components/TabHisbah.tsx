import React, { useEffect, useMemo, useState } from 'react';
import {
  Clock,
  Flame,
  Gavel,
  RotateCcw,
  ShieldCheck,
  ShieldX,
  UserCheck,
  Vote,
} from 'lucide-react';
import {
  CHAMBER1_VOTERS,
  HISBAH_PROPOSALS,
  HisbahProposal,
  Lang,
} from '../data/genesisData';
import { UI_COPY } from '../i18n/translations';
import { formatIdr } from '../utils/formatters';

interface TabHisbahProps {
  lang: Lang;
}

export const TabHisbah: React.FC<TabHisbahProps> = ({ lang }) => {
  const t = UI_COPY[lang].hisbah;

  const [proposals, setProposals] = useState<HisbahProposal[]>(HISBAH_PROPOSALS);
  const [selectedId, setSelectedId] = useState<string>('HIP-01');
  const [extraWakifVotes, setExtraWakifVotes] = useState<number>(0);
  const [tickSec, setTickSec] = useState<number>(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setTickSec((s) => (s + 1) % 86400);
    }, 1000);
    return () => window.clearInterval(timer);
  }, []);

  const selectedProposal = useMemo(
    () => proposals.find((p) => p.id === selectedId) ?? proposals[0],
    [proposals, selectedId],
  );

  const totalCapturedPrincipalIdr = useMemo(
    () =>
      proposals
        .filter((p) => p.depositCapturedToPrincipal)
        .reduce((acc, p) => acc + p.bondIdr, 0),
    [proposals],
  );

  const formatCountdown = (days: number) => {
    if (days <= 0) return '00d 00h 00m 00s';
    const totalRemaining = days * 86400 - tickSec;
    const d = Math.floor(totalRemaining / 86400);
    const h = Math.floor((totalRemaining % 86400) / 3600);
    const m = Math.floor((totalRemaining % 3600) / 60);
    const s = totalRemaining % 60;
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${pad(d)}d ${pad(h)}h ${pad(m)}m ${pad(s)}s`;
  };

  const handleWakifVote = () => {
    setExtraWakifVotes((v) => v + 15);
    setProposals((prev) =>
      prev.map((p) =>
        p.id === selectedId && p.status === 'ACTIVE_SSB_REVIEW'
          ? {
              ...p,
              chamber1ForPct: Math.min(99.9, Number((p.chamber1ForPct + 0.2).toFixed(1))),
              chamber1AgainstPct: Math.max(0.1, Number((p.chamber1AgainstPct - 0.2).toFixed(1))),
            }
          : p,
      ),
    );
  };

  const handleSsbApprove = () => {
    setProposals((prev) =>
      prev.map((p) => {
        if (p.id !== selectedId || p.ssbVetoed) return p;
        const nextApp = Math.min(p.ssbRequired, p.ssbApprovals + 1);
        return {
          ...p,
          ssbApprovals: nextApp,
          status: nextApp >= p.ssbRequired ? 'PASSED_EXECUTED' : p.status,
          daysRemaining: nextApp >= p.ssbRequired ? 0 : p.daysRemaining,
        };
      }),
    );
  };

  const handleSsbVeto = () => {
    setProposals((prev) =>
      prev.map((p) =>
        p.id === selectedId
          ? {
              ...p,
              ssbVetoed: true,
              status: 'VETOED_CAPTURED',
              daysRemaining: 0,
              depositCapturedToPrincipal: true,
            }
          : p,
      ),
    );
  };

  const handleReset = () => {
    setProposals(HISBAH_PROPOSALS);
    setExtraWakifVotes(0);
  };

  const dynamicVoters = CHAMBER1_VOTERS.map((v) =>
    v.role === 'WAKIF'
      ? { ...v, effectiveQuadraticWeight: v.effectiveQuadraticWeight + extraWakifVotes }
      : v,
  );
  const totalForWeight = dynamicVoters
    .filter((v) => v.vote === 'FOR')
    .reduce((sum, v) => sum + v.effectiveQuadraticWeight, 0);
  const totalAgainstWeight = dynamicVoters
    .filter((v) => v.vote === 'AGAINST')
    .reduce((sum, v) => sum + v.effectiveQuadraticWeight, 0);

  return (
    <div className="stack">
      <div className="section-head">
        <h2>{t.heading}</h2>
        <p>{t.subheading}</p>
      </div>

      {/* Proposals Selector + Detail */}
      <div className="parchment-card">
        <div className="card-header">
          <h3 className="card-title">
            <Gavel size={18} color="#108458" />
            {t.proposalsTitle}
          </h3>
          <button type="button" className="btn btn--ghost-light" onClick={handleReset}>
            <RotateCcw size={14} />
            {t.resetGovernanceBtn}
          </button>
        </div>

        <div className="grid-2">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {proposals.map((prop) => {
              const active = prop.id === selectedId;
              const statusBadge =
                prop.status === 'PASSED_EXECUTED'
                  ? 'badge--emerald'
                  : prop.status === 'VETOED_CAPTURED'
                    ? 'badge--crimson'
                    : 'badge--gold';

              return (
                <button
                  key={prop.id}
                  type="button"
                  onClick={() => setSelectedId(prop.id)}
                  style={{
                    textAlign: 'left',
                    padding: '12px 14px',
                    borderRadius: 12,
                    border: active ? '2px solid #108458' : '1px solid #dfd6c3',
                    background: active ? '#ffffff' : '#f2ecdf',
                    cursor: 'pointer',
                    fontFamily: 'inherit',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                    <span className="mono" style={{ fontWeight: 800, fontSize: '0.8rem', color: '#11221d' }}>
                      {prop.id} · {prop.pool}
                    </span>
                    <span className={`badge ${statusBadge}`}>{prop.status}</span>
                  </div>
                  <div style={{ fontWeight: 700, fontSize: '0.9rem', marginTop: 6, color: '#11221d' }}>
                    {prop.title[lang]}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#61746d', marginTop: 4 }}>
                    Chamber 1: {prop.chamber1ForPct}% FOR · SSB {prop.ssbApprovals}/{prop.ssbRequired}
                    {prop.depositCapturedToPrincipal ? ` · ${t.capturedBadge}` : ''}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Selected Proposal Action Card */}
          <div
            style={{
              background: '#0c211b',
              color: '#f4f1ea',
              borderRadius: 14,
              padding: 18,
              border: '1px solid rgba(212, 168, 79, 0.3)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: 14,
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                <span className="pool-ticker">{selectedProposal.id}</span>
                <span className="badge badge--gold-dark">
                  Bond: {formatIdr(selectedProposal.bondIdr)}
                </span>
              </div>
              <h4 style={{ margin: '10px 0 6px', fontSize: '1.05rem', color: '#ecc774' }}>
                {selectedProposal.title[lang]}
              </h4>
              <p style={{ margin: 0, fontSize: '0.84rem', color: '#cfe0d9', lineHeight: 1.5 }}>
                {selectedProposal.summary[lang]}
              </p>

              <div
                style={{
                  marginTop: 14,
                  padding: 12,
                  borderRadius: 10,
                  background: 'rgba(255,255,255,0.04)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', color: '#a6bab3' }}>
                  <Clock size={15} color="#ecc774" />
                  {t.countdownLabel}
                </span>
                <span className="mono" style={{ fontWeight: 700, color: '#ecc774' }}>
                  {formatCountdown(selectedProposal.daysRemaining)}
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              <button
                type="button"
                className="btn btn--gold"
                onClick={handleWakifVote}
                disabled={selectedProposal.status !== 'ACTIVE_SSB_REVIEW'}
              >
                <Vote size={14} />
                {t.simulateVoteBtn}
              </button>
              <button
                type="button"
                className="btn btn--primary"
                onClick={handleSsbApprove}
                disabled={selectedProposal.status !== 'ACTIVE_SSB_REVIEW'}
              >
                <ShieldCheck size={14} />
                {t.ssbSignBtn} ({selectedProposal.ssbApprovals}/{selectedProposal.ssbRequired})
              </button>
              <button
                type="button"
                className="btn btn--danger"
                onClick={handleSsbVeto}
                disabled={selectedProposal.ssbVetoed}
              >
                <ShieldX size={14} />
                {t.ssbVetoBtn}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Chamber 1 vs Chamber 2 */}
      <div className="grid-2">
        {/* Chamber 1: Quadratic Soulbound DID Tally */}
        <div className="parchment-card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <UserCheck size={18} color="#108458" />
                {t.chamber1Title}
              </h3>
              <p className="card-subtitle">{t.chamber1Sub}</p>
            </div>
          </div>

          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Voter / Entity</th>
                  <th className="num-right">{t.rawTokensCol}</th>
                  <th className="num-right">{t.didCol}</th>
                  <th className="num-right">{t.effectiveWeightCol}</th>
                  <th>{t.voteCol}</th>
                </tr>
              </thead>
              <tbody>
                {dynamicVoters.map((v) => (
                  <tr key={v.id} className={v.role === 'WHALE' ? '' : 'highlight-row'}>
                    <td>
                      <div style={{ fontWeight: 700, fontSize: '0.82rem' }}>{v.label[lang]}</div>
                      <div className="mono" style={{ fontSize: '0.7rem', color: '#61746d' }}>
                        {v.id}
                      </div>
                    </td>
                    <td className="num-right">{v.rawTokens.toLocaleString('en-US')}</td>
                    <td className="num-right">
                      {v.didVerified ? (
                        <span className="badge badge--emerald">DID · {v.reputationScore}</span>
                      ) : (
                        <span className="badge badge--crimson">NO DID · {v.reputationScore}</span>
                      )}
                    </td>
                    <td className="num-right" style={{ fontWeight: 800 }}>
                      {v.effectiveQuadraticWeight}
                    </td>
                    <td>
                      <span className={`badge ${v.vote === 'FOR' ? 'badge--emerald' : 'badge--crimson'}`}>
                        {v.vote}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="callout callout--gold" style={{ marginTop: 12 }}>
            <ShieldCheck size={18} style={{ flexShrink: 0 }} />
            <div style={{ fontSize: '0.8rem' }}>
              <strong>{t.whaleAlert}:</strong>{' '}
              <span className="mono">
                FOR={totalForWeight} vs AGAINST={totalAgainstWeight} (
                {((totalForWeight / (totalForWeight + totalAgainstWeight)) * 100).toFixed(1)}% Quorum)
              </span>
            </div>
          </div>
        </div>

        {/* Chamber 2: SSB Veto Gate & Zero-Burn Deposit Capture */}
        <div className="dark-panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: 14 }}>
          <div>
            <div className="card-header">
              <div>
                <h3 className="card-title">
                  <ShieldCheck size={18} color="#ecc774" />
                  {t.chamber2Title}
                </h3>
                <p className="card-subtitle">{t.chamber2Sub}</p>
              </div>
            </div>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: 10,
                marginTop: 10,
              }}
            >
              {[1, 2, 3].map((slot) => {
                const signed = selectedProposal.ssbApprovals >= slot && !selectedProposal.ssbVetoed;
                return (
                  <div
                    key={slot}
                    style={{
                      padding: 12,
                      borderRadius: 10,
                      background: selectedProposal.ssbVetoed
                        ? 'rgba(194, 51, 58, 0.16)'
                        : signed
                          ? 'rgba(30, 185, 128, 0.16)'
                          : 'rgba(255, 255, 255, 0.04)',
                      border: `1px solid ${
                        selectedProposal.ssbVetoed
                          ? 'rgba(240, 90, 98, 0.4)'
                          : signed
                            ? 'rgba(30, 185, 128, 0.4)'
                            : 'rgba(255, 255, 255, 0.1)'
                      }`,
                    }}
                  >
                    <div className="mono" style={{ fontSize: '0.72rem', color: '#a6bab3' }}>
                      SSB SIGNER #{slot}
                    </div>
                    <div style={{ fontWeight: 700, fontSize: '0.84rem', marginTop: 4 }}>
                      {selectedProposal.ssbVetoed
                        ? 'VETOED'
                        : signed
                          ? 'APPROVED'
                          : 'PENDING REVIEW'}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div
            style={{
              padding: 16,
              borderRadius: 12,
              background: 'rgba(212, 168, 79, 0.12)',
              border: '1px solid rgba(212, 168, 79, 0.35)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10 }}>
              <strong style={{ display: 'inline-flex', alignItems: 'center', gap: 7, color: '#ecc774' }}>
                <Flame size={17} />
                {t.zeroBurnTitle}
              </strong>
              <span className="badge badge--emerald-dark">0% BURNED</span>
            </div>
            <p style={{ margin: '8px 0 12px', fontSize: '0.82rem', color: '#e6eee9', lineHeight: 1.5 }}>
              {t.zeroBurnDesc}
            </p>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                paddingTop: 10,
                borderTop: '1px dashed rgba(212, 168, 79, 0.35)',
              }}
            >
              <span style={{ fontSize: '0.78rem', color: '#a6bab3' }}>
                {lang === 'en' ? 'Captured to Mu’abbad Principal Vault:' : 'Dialirkan ke Brankas Pokok Mu’abbad:'}
              </span>
              <span className="mono" style={{ fontSize: '1.08rem', fontWeight: 800, color: '#6ee7b7' }}>
                {formatIdr(totalCapturedPrincipalIdr)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
