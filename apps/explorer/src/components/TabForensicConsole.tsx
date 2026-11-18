import React, { useState } from 'react';
import {
  Activity,
  AlertOctagon,
  CheckCircle2,
  Filter,
  ShieldAlert,
  ShieldCheck,
} from 'lucide-react';
import { FORENSIC_9_CHECKS, Lang } from '../data/genesisData';
import { UI_COPY } from '../i18n/translations';

interface TabForensicConsoleProps {
  lang: Lang;
}

export const TabForensicConsole: React.FC<TabForensicConsoleProps> = ({ lang }) => {
  const t = UI_COPY[lang].forensic;
  const [filterMode, setFilterMode] = useState<'ALL' | 'CRITICAL'>('ALL');

  const visibleChecks =
    filterMode === 'CRITICAL'
      ? FORENSIC_9_CHECKS.filter((c) => c.bioflocStatus === 'CRITICAL_FAIL')
      : FORENSIC_9_CHECKS;

  return (
    <div className="stack">
      <div className="section-head">
        <h2>{t.heading}</h2>
        <p>{t.subheading}</p>
      </div>

      {/* Side-by-side Verdict Cards */}
      <div className="grid-2">
        {/* Approved Benchmark */}
        <div className="parchment-card" style={{ borderColor: '#108458', borderWidth: 2 }}>
          <div className="card-header">
            <h3 className="card-title" style={{ color: '#0b6643' }}>
              <ShieldCheck size={20} color="#108458" />
              {t.approvedTitle}
            </h3>
            <span className="badge badge--emerald" style={{ fontSize: '0.82rem', padding: '5px 12px' }}>
              <CheckCircle2 size={14} />
              {t.approvedVerdict}
            </span>
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'baseline',
              justifyContent: 'space-between',
              padding: '12px 14px',
              borderRadius: 10,
              background: 'rgba(16, 132, 88, 0.1)',
              marginBottom: 12,
            }}
          >
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0b5d3e' }}>
              {t.riskScoreLabel}
            </span>
            <span className="mono" style={{ fontSize: '1.55rem', fontWeight: 800, color: '#0b6643' }}>
              14 / 100
            </span>
          </div>

          <div style={{ fontSize: '0.84rem', color: '#3b4f48', lineHeight: 1.55 }}>
            {lang === 'en'
              ? 'Hybrid Ijarah (Rp 532.4M) + Qardh Hasan (Rp 300M) ring-fences waqf principal against biological failure while generating 18.02% p.a. audited net cash yield and 3.85× SROI.'
              : 'Struktur Hibrida Ijarah (Rp 532,4 Jt) + Qardh Hasan (Rp 300 Jt) memagari pokok wakaf dari risiko biologis sambil menghasilkan imbal hasil kas bersih 18,02% p.a. dan SROI 3,85×.'}
          </div>
        </div>

        {/* Rejected External Biofloc Proposal */}
        <div className="parchment-card" style={{ borderColor: '#c2333a', borderWidth: 2 }}>
          <div className="card-header">
            <h3 className="card-title" style={{ color: '#9e1c22' }}>
              <ShieldAlert size={20} color="#c2333a" />
              {t.rejectedTitle}
            </h3>
            <span className="badge badge--crimson" style={{ fontSize: '0.82rem', padding: '5px 12px' }}>
              <AlertOctagon size={14} />
              {t.rejectedVerdict}
            </span>
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'baseline',
              justifyContent: 'space-between',
              padding: '12px 14px',
              borderRadius: 10,
              background: 'rgba(194, 51, 58, 0.12)',
              marginBottom: 12,
            }}
          >
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#8f1a20' }}>
              {t.riskScoreLabel}
            </span>
            <span className="mono" style={{ fontSize: '1.55rem', fontWeight: 800, color: '#9e1c22' }}>
              92 / 100
            </span>
          </div>

          <div style={{ fontSize: '0.84rem', color: '#3b4f48', lineHeight: 1.55 }}>
            {lang === 'en'
              ? 'Hard-rejected across 6 critical gates: 0.56 FCR impossibility, +83.6% CAPEX inflation, highland cold stress (<21°C), RRR 6.83:1 downside skew, uncertified land, and invalid Mudharabah risk transfer.'
              : 'Ditolak keras di 6 gerbang kritis: FCR mustahil 0,56, mark-up CAPEX +83,6%, stres dingin dataran tinggi (<21°C), asimetri RRR 6,83:1, lahan tanpa sertifikat, dan akad Mudharabah cacat.'}
          </div>
        </div>
      </div>

      {/* 9-Check Matrix */}
      <div className="parchment-card">
        <div className="card-header">
          <h3 className="card-title">
            <Activity size={18} color="#108458" />
            {t.matrixTitle} ({visibleChecks.length} / {FORENSIC_9_CHECKS.length})
          </h3>

          <div style={{ display: 'flex', gap: 8 }}>
            <button
              type="button"
              className={`btn ${filterMode === 'ALL' ? 'btn--primary' : 'btn--ghost-light'}`}
              onClick={() => setFilterMode('ALL')}
            >
              <Filter size={13} />
              {lang === 'en' ? 'All 9 Checks' : 'Semua 9 Uji'}
            </button>
            <button
              type="button"
              className={`btn ${filterMode === 'CRITICAL' ? 'btn--danger' : 'btn--ghost-light'}`}
              onClick={() => setFilterMode('CRITICAL')}
            >
              <AlertOctagon size={13} />
              {lang === 'en' ? 'Critical Failures (6)' : 'Kegagalan Kritis (6)'}
            </button>
          </div>
        </div>

        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: '22%' }}>{t.colDimension}</th>
                <th style={{ width: '16%' }}>{t.colRule}</th>
                <th style={{ width: '31%' }}>{t.colBenchmark}</th>
                <th style={{ width: '31%' }}>{t.colRejected}</th>
              </tr>
            </thead>
            <tbody>
              {visibleChecks.map((row) => (
                <tr key={row.id}>
                  <td>
                    <div style={{ fontWeight: 700, color: '#11221d' }}>{row.dimension[lang]}</div>
                    <div className="mono" style={{ fontSize: '0.72rem', color: '#61746d', marginTop: 4 }}>
                      Risk Weight: {row.weightPts} pts
                    </div>
                  </td>
                  <td>
                    <span className="badge badge--gold mono">{row.thresholdRule[lang]}</span>
                  </td>
                  <td>
                    <span className="badge badge--emerald" style={{ marginBottom: 6 }}>
                      PASS
                    </span>
                    <div style={{ fontSize: '0.82rem', color: '#11221d', lineHeight: 1.45 }}>
                      {row.benchmarkNautera[lang]}
                    </div>
                  </td>
                  <td>
                    <span className="badge badge--crimson" style={{ marginBottom: 6 }}>
                      {row.bioflocStatus}
                    </span>
                    <div style={{ fontSize: '0.82rem', color: '#8f1a20', lineHeight: 1.45 }}>
                      {row.rejectedBiofloc[lang]}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
