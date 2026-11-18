import React, { useState } from 'react';
import {
  AlertOctagon,
  BookOpenCheck,
  CheckCircle2,
  FileCheck2,
  Lock,
  ShieldAlert,
  Sliders,
} from 'lucide-react';
import { Lang } from '../data/genesisData';
import { UI_COPY } from '../i18n/translations';
import { formatIdr } from '../utils/formatters';

interface TabWaterfallProps {
  lang: Lang;
}

export const TabWaterfall: React.FC<TabWaterfallProps> = ({ lang }) => {
  const t = UI_COPY[lang].waterfall;

  const [grossYieldIdr, setGrossYieldIdr] = useState<number>(150_000_000);
  const [sinkingPct, setSinkingPct] = useState<number>(20);
  const [nazhirPct, setNazhirPct] = useState<number>(10);
  const [bastSigned, setBastSigned] = useState<boolean>(true);

  const mauqufPct = Math.max(0, 100 - sinkingPct - nazhirPct);
  const nazhirCapViolated = nazhirPct > 10.0;
  const mauqufFloorViolated = mauqufPct < 50.0;
  const isReverted = nazhirCapViolated || mauqufFloorViolated;

  const sinkingIdr = (grossYieldIdr * sinkingPct) / 100;
  const nazhirIdr = (grossYieldIdr * nazhirPct) / 100;
  const mauqufIdr = (grossYieldIdr * mauqufPct) / 100;

  return (
    <div className="stack">
      <div className="section-head">
        <h2>{t.heading}</h2>
        <p>{t.subheading}</p>
      </div>

      <div className="grid-2">
        {/* Controls & Invariants */}
        <div className="parchment-card">
          <div className="card-header">
            <h3 className="card-title">
              <Sliders size={18} color="#108458" />
              AAOIFI SS 60 & UU 41/2004 Parameters
            </h3>
            <span className={`badge ${isReverted ? 'badge--crimson' : 'badge--emerald'}`}>
              {isReverted ? 'REVERTED' : 'VALID'}
            </span>
          </div>

          <div className="control-group">
            <label className="control-label" htmlFor="gross-yield-slider">
              <span>{t.grossYieldLabel}</span>
              <span className="mono">{formatIdr(grossYieldIdr)}</span>
            </label>
            <input
              id="gross-yield-slider"
              type="range"
              min={10_000_000}
              max={500_000_000}
              step={5_000_000}
              className="range-slider"
              value={grossYieldIdr}
              onChange={(e) => setGrossYieldIdr(Number(e.target.value))}
            />
          </div>

          <div className="control-group">
            <label className="control-label" htmlFor="sinking-slider">
              <span>{t.sinkingLabel}</span>
              <span className="mono">{sinkingPct.toFixed(1)}% ({formatIdr(sinkingIdr)})</span>
            </label>
            <input
              id="sinking-slider"
              type="range"
              min={10}
              max={40}
              step={1}
              className="range-slider"
              value={sinkingPct}
              onChange={(e) => setSinkingPct(Number(e.target.value))}
            />
          </div>

          <div className="control-group">
            <label className="control-label" htmlFor="nazhir-slider">
              <span>{t.nazhirLabel}</span>
              <span
                className="mono"
                style={{ color: nazhirCapViolated ? '#c2333a' : '#0b6643', fontWeight: 800 }}
              >
                {nazhirPct.toFixed(1)}% ({formatIdr(nazhirIdr)})
              </span>
            </label>
            <input
              id="nazhir-slider"
              type="range"
              min={0}
              max={15}
              step={0.5}
              className={`range-slider ${nazhirCapViolated ? 'range-slider--danger' : ''}`}
              value={nazhirPct}
              onChange={(e) => setNazhirPct(Number(e.target.value))}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#61746d' }}>
              <span>0%</span>
              <span className="mono" style={{ fontWeight: 700, color: '#0b6643' }}>
                10.0% Statutory Cap (UU 41/2004)
              </span>
              <span style={{ color: '#c2333a' }}>15% (Revert Zone)</span>
            </div>
          </div>

          <div className="control-group">
            <div className="control-label">
              <span>{t.mauqufLabel}</span>
              <span
                className="mono"
                style={{ color: mauqufFloorViolated ? '#c2333a' : '#0b6643', fontWeight: 800 }}
              >
                {mauqufPct.toFixed(1)}% ({formatIdr(mauqufIdr)})
              </span>
            </div>
          </div>

          {/* Visual Waterfall Bar */}
          <div className="waterfall-bar" aria-label="Yield distribution waterfall">
            <div className="wf-seg wf-seg--sinking" style={{ width: `${sinkingPct}%` }}>
              {sinkingPct}%
            </div>
            <div
              className={`wf-seg ${nazhirCapViolated ? 'wf-seg--nazhir-over' : 'wf-seg--nazhir'}`}
              style={{ width: `${nazhirPct}%` }}
            >
              {nazhirPct}%
            </div>
            <div className="wf-seg wf-seg--mauquf" style={{ width: `${mauqufPct}%` }}>
              {mauqufPct}%
            </div>
          </div>

          {/* BAST Oracle Gate Toggle */}
          <div
            style={{
              marginTop: 14,
              padding: 12,
              borderRadius: 10,
              background: '#f2ecdf',
              border: '1px solid #dfd6c3',
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 10,
            }}
          >
            <div>
              <div style={{ fontSize: '0.78rem', fontWeight: 800 }}>{t.bastGateLabel}</div>
              <div style={{ fontSize: '0.74rem', color: '#4b5e57' }}>
                {bastSigned ? t.bastSigned : t.bastPending}
              </div>
            </div>
            <button
              type="button"
              className={`btn ${bastSigned ? 'btn--primary' : 'btn--gold'}`}
              onClick={() => setBastSigned((v) => !v)}
            >
              <FileCheck2 size={15} />
              {bastSigned ? 'BAST: SIGNED' : 'BAST: PENDING'}
            </button>
          </div>
        </div>

        {/* Invariant Status + PSAK 412 Double-Entry Journal */}
        <div className="stack">
          {isReverted ? (
            <div className="parchment-card" style={{ borderColor: '#c2333a', borderWidth: 2 }}>
              <div className="callout callout--crimson">
                <AlertOctagon size={24} style={{ flexShrink: 0 }} />
                <div>
                  <div style={{ fontWeight: 800, fontSize: '0.96rem' }}>{t.invariantLockTitle}</div>
                  <p style={{ margin: '6px 0 10px' }}>{t.invariantLockDesc}</p>
                  <div className="mono" style={{ fontSize: '0.76rem', marginBottom: 12 }}>
                    {nazhirCapViolated &&
                      `revert NazhirCapExceeded(requestedBps=${Math.round(nazhirPct * 100)}, maxBps=1000); `}
                    {mauqufFloorViolated &&
                      `revert MauqufFloorViolation(computedBps=${Math.round(mauqufPct * 100)}, minBps=5000);`}
                  </div>
                  <button
                    type="button"
                    className="btn btn--danger"
                    onClick={() => {
                      if (nazhirPct > 10) setNazhirPct(10);
                      if (100 - sinkingPct - Math.min(nazhirPct, 10) < 50) {
                        setSinkingPct(40);
                      }
                    }}
                  >
                    <Lock size={14} />
                    {t.clampButton}
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="parchment-card">
              <div className="callout callout--emerald">
                <CheckCircle2 size={22} style={{ flexShrink: 0 }} />
                <div>
                  <div style={{ fontWeight: 800 }}>{t.invariantOk}</div>
                  <div style={{ fontSize: '0.8rem', marginTop: 4 }}>
                    <span className="mono">
                      sinking={sinkingPct}% (10–40%) · nazhir={nazhirPct}% (&lt;=10%) · mauquf={mauqufPct}% (&gt;=50%)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* PSAK 412 Journal Entry */}
          <div className="parchment-card">
            <div className="card-header">
              <h3 className="card-title">
                <BookOpenCheck size={18} color="#108458" />
                {t.journalTitle}
              </h3>
              <span className={`badge ${bastSigned ? 'badge--emerald' : 'badge--gold'}`}>
                {bastSigned ? t.released : t.escrowHeld}
              </span>
            </div>

            <div className="data-table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>PSAK 412 Account</th>
                    <th>Dr / Cr</th>
                    <th className="num-right">Amount (IDR)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>
                      <strong>1101 · Cash / Bank Wakaf Realized Yield</strong>
                    </td>
                    <td className="mono">DR</td>
                    <td className="num-right">{isReverted ? 'LOCKED' : formatIdr(grossYieldIdr)}</td>
                  </tr>
                  <tr>
                    <td>
                      <strong>3201 · AAOIFI SS 60 Sinking &amp; Maintenance Reserve</strong>
                      <div style={{ fontSize: '0.73rem', color: '#61746d' }}>
                        {sinkingPct.toFixed(1)}% upfront asset preservation
                      </div>
                    </td>
                    <td className="mono">CR</td>
                    <td className="num-right">{isReverted ? '—' : formatIdr(sinkingIdr)}</td>
                  </tr>
                  <tr>
                    <td>
                      <strong>2104 · Nazhir Operational Ujrah Payable</strong>
                      <div style={{ fontSize: '0.73rem', color: nazhirCapViolated ? '#c2333a' : '#61746d' }}>
                        {nazhirPct.toFixed(1)}% {nazhirCapViolated ? '(REJECTED >10%)' : '(UU 41/2004 Compliant)'}
                      </div>
                    </td>
                    <td className="mono">CR</td>
                    <td className="num-right">{isReverted ? 'REJECTED' : formatIdr(nazhirIdr)}</td>
                  </tr>
                  <tr className="highlight-row">
                    <td>
                      <strong>
                        {bastSigned
                          ? '5101 · Mauquf ‘Alaih Beneficiary Disbursement'
                          : '2209 · Mauquf ‘Alaih BAST-Gated Escrow'}
                      </strong>
                      <div style={{ fontSize: '0.73rem', color: '#4b5e57' }}>
                        {bastSigned ? 'BAST-WPAIR-CL41-2026 verified' : 'Awaiting signed field BAST'}
                      </div>
                    </td>
                    <td className="mono">CR</td>
                    <td className="num-right">{isReverted ? '—' : formatIdr(mauqufIdr)}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {isReverted && (
              <div style={{ marginTop: 10, fontSize: '0.78rem', color: '#9e1c22', display: 'flex', alignItems: 'center', gap: 6 }}>
                <ShieldAlert size={14} />
                {lang === 'en'
                  ? 'Journal posting blocked until Nazhir Fee <= 10.0% and Mauquf ‘Alaih >= 50.0%.'
                  : 'Pencatatan jurnal diblokir hingga Fee Nazhir <= 10,0% dan Mauquf ‘Alaih >= 50,0%.'}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
