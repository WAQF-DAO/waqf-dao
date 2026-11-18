import React, { useMemo, useState } from 'react';
import {
  CheckCircle2,
  Coins,
  Layers,
  Lock,
  RefreshCw,
  Scale,
  ShieldAlert,
  ShieldCheck,
} from 'lucide-react';
import {
  EndowmentPool,
  GENESIS_POOLS,
  INSTITUTIONAL_ANCHORS,
  Lang,
  PSAK412_TRAJECTORY,
} from '../data/genesisData';
import { UI_COPY } from '../i18n/translations';
import { formatIdr, formatPct } from '../utils/formatters';

interface TabVaultsProps {
  lang: Lang;
}

export const TabVaults: React.FC<TabVaultsProps> = ({ lang }) => {
  const t = UI_COPY[lang].vaults;

  const [selectedPoolId, setSelectedPoolId] = useState<EndowmentPool['id']>('WPUD');
  const [contributionIdr, setContributionIdr] = useState<number>(10_000_000);
  const [waqfMode, setWaqfMode] = useState<'MUABBAD' | 'MUAQQAT'>('MUABBAD');
  const [termYears, setTermYears] = useState<number>(3);
  const [istibdalPct, setIstibdalPct] = useState<number>(108.4);

  const selectedPool = useMemo(
    () => GENESIS_POOLS.find((p) => p.id === selectedPoolId) ?? GENESIS_POOLS[0],
    [selectedPoolId],
  );

  const handleSelectPool = (pool: EndowmentPool) => {
    setSelectedPoolId(pool.id);
    setIstibdalPct(pool.istibdalAppraisalPct);
  };

  const simShares = Math.floor(Math.max(0, contributionIdr) / selectedPool.sharePriceIdr);
  const annualYieldIdr = (Math.max(0, contributionIdr) * selectedPool.annualYieldPct) / 100;
  const totalSocialImpactIdr = Math.max(0, contributionIdr) * selectedPool.sroi;
  const istibdalPasses = istibdalPct >= 100;

  return (
    <div className="stack">
      <div className="section-head">
        <h2>{t.heading}</h2>
        <p>{t.subheading}</p>
      </div>

      {/* PSAK 412 Trajectory Table */}
      <div className="parchment-card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Scale size={18} color="#108458" />
              {t.psakTitle}
            </h3>
            <p className="card-subtitle">{t.psakSubtitle}</p>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {INSTITUTIONAL_ANCHORS.kapAuditStreak.map((item) => (
              <span key={item} className="badge badge--emerald">
                <CheckCircle2 size={12} />
                {item}
              </span>
            ))}
          </div>
        </div>

        <div className="data-table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>{t.colYear}</th>
                <th>{t.colStatus}</th>
                <th className="num-right">{t.colAssets}</th>
                <th className="num-right">{t.colTempLiab}</th>
                <th className="num-right">{t.colNetAssets}</th>
                <th className="num-right">{t.colDiff}</th>
              </tr>
            </thead>
            <tbody>
              {PSAK412_TRAJECTORY.map((row) => (
                <tr key={row.year} className={row.year === '2026' ? 'highlight-row' : ''}>
                  <td className="mono">{row.year}</td>
                  <td>
                    <span>{row.status[lang]}</span>{' '}
                    <span className="badge badge--gold" style={{ marginLeft: 6 }}>
                      {row.auditOpinion}
                    </span>
                  </td>
                  <td className="num-right">{formatIdr(row.totalAssetsIdr)}</td>
                  <td className="num-right">{formatIdr(row.tempWaqfLiabilitiesIdr)}</td>
                  <td className="num-right">{formatIdr(row.netAssetsIdr)}</td>
                  <td className="num-right">
                    <span className="badge badge--emerald">{formatIdr(row.diffIdr)}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5 Genesis Endowment Pools */}
      <div className="dark-panel">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Layers size={18} color="#ecc774" />
              {t.poolsTitle}
            </h3>
            <p className="card-subtitle">{INSTITUTIONAL_ANCHORS.waqfFramework}</p>
          </div>
          <span className="badge badge--gold-dark">{selectedPool.waqfFrameworkPhase}</span>
        </div>

        <div className="pools-grid">
          {GENESIS_POOLS.map((pool) => {
            const isSelected = pool.id === selectedPoolId;
            return (
              <button
                key={pool.id}
                type="button"
                className={`pool-card ${isSelected ? 'selected' : ''}`}
                onClick={() => handleSelectPool(pool)}
              >
                <div className="pool-card__top">
                  <span className="pool-ticker">{pool.id}</span>
                  <span className="badge badge--emerald">{pool.sroi.toFixed(2)}× SROI</span>
                </div>
                <h4 className="pool-name">{pool.name[lang]}</h4>
                <div style={{ fontSize: '0.76rem', color: '#4b5e57', lineHeight: 1.35 }}>
                  {pool.contractModel[lang]}
                </div>
                <div className="pool-metrics">
                  <div>
                    <span className="pool-metric-label">{t.sharePrice}</span>
                    <span className="pool-metric-val">{formatIdr(pool.sharePriceIdr)}</span>
                  </div>
                  <div>
                    <span className="pool-metric-label">{t.yieldLabel}</span>
                    <span className="pool-metric-val">{formatPct(pool.annualYieldPct, 2)} p.a.</span>
                  </div>
                  <div style={{ gridColumn: '1 / -1' }}>
                    <span className="pool-metric-label">{t.principalLabel}</span>
                    <span className="pool-metric-val">{formatIdr(pool.allocatedPrincipalIdr)}</span>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Selected Pool Highlights */}
        <div
          style={{
            marginTop: 16,
            padding: '14px 16px',
            borderRadius: 12,
            background: 'rgba(6, 17, 14, 0.55)',
            border: '1px solid rgba(212, 168, 79, 0.24)',
          }}
        >
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'space-between',
              gap: 8,
              marginBottom: 8,
            }}
          >
            <strong style={{ color: '#ecc774' }}>{selectedPool.name[lang]}</strong>
            <span className="mono" style={{ fontSize: '0.78rem', color: '#a6bab3' }}>
              {selectedPool.beneficiaryMetric[lang]}
            </span>
          </div>
          <ul style={{ margin: 0, paddingLeft: 18, fontSize: '0.84rem', color: '#e6eee9', lineHeight: 1.55 }}>
            {selectedPool.highlights.map((h, i) => (
              <li key={i}>{h[lang]}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* Mu'abbad vs Mu'aqqat Simulator & Istibdal Guard */}
      <div className="grid-2">
        {/* Simulator */}
        <div className="parchment-card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <Coins size={18} color="#108458" />
                {t.simTitle}
              </h3>
              <p className="card-subtitle">{t.simSubtitle}</p>
            </div>
          </div>

          <div className="control-group">
            <label className="control-label" htmlFor="sim-pool-select">
              {t.simPoolLabel}
            </label>
            <select
              id="sim-pool-select"
              className="select-field"
              value={selectedPoolId}
              onChange={(e) => {
                const next = GENESIS_POOLS.find((p) => p.id === e.target.value);
                if (next) handleSelectPool(next);
              }}
            >
              {GENESIS_POOLS.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name[lang]} ({formatIdr(p.sharePriceIdr)}/share)
                </option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label className="control-label" htmlFor="sim-amount-input">
              <span>{t.simAmountLabel}</span>
              <span className="mono">{formatIdr(contributionIdr)}</span>
            </label>
            <input
              id="sim-amount-input"
              type="number"
              min={50_000}
              step={50_000}
              className="input-field mono"
              value={contributionIdr}
              onChange={(e) => setContributionIdr(Number(e.target.value) || 0)}
            />
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 4 }}>
              {[1_000_000, 10_000_000, 63_000_000, 100_000_000].map((preset) => (
                <button
                  key={preset}
                  type="button"
                  className="btn btn--ghost-light"
                  style={{ padding: '4px 9px', fontSize: '0.73rem' }}
                  onClick={() => setContributionIdr(preset)}
                >
                  {formatIdr(preset)}
                </button>
              ))}
            </div>
          </div>

          <div className="control-group">
            <span className="control-label">{t.simTypeLabel}</span>
            <div className="segmented-row">
              <button
                type="button"
                className={`seg-option ${waqfMode === 'MUABBAD' ? 'active' : ''}`}
                onClick={() => setWaqfMode('MUABBAD')}
              >
                <span className="seg-option__title">{t.muabbadLabel}</span>
                <span className="seg-option__desc">{t.muabbadDesc}</span>
              </button>
              <button
                type="button"
                className={`seg-option ${waqfMode === 'MUAQQAT' ? 'active' : ''}`}
                onClick={() => setWaqfMode('MUAQQAT')}
              >
                <span className="seg-option__title">{t.muaqqatLabel}</span>
                <span className="seg-option__desc">{t.muaqqatDesc}</span>
              </button>
            </div>
          </div>

          {waqfMode === 'MUAQQAT' && (
            <div className="control-group">
              <label className="control-label" htmlFor="sim-term-range">
                <span>{t.simTermLabel}</span>
                <span className="mono">{termYears} yr</span>
              </label>
              <input
                id="sim-term-range"
                type="range"
                min={1}
                max={5}
                step={1}
                className="range-slider"
                value={termYears}
                onChange={(e) => setTermYears(Number(e.target.value))}
              />
            </div>
          )}

          <div
            style={{
              background: '#f2ecdf',
              border: '1px solid #dfd6c3',
              borderRadius: 12,
              padding: 14,
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: 12,
            }}
          >
            <div>
              <div style={{ fontSize: '0.72rem', color: '#61746d', fontWeight: 700 }}>{t.simSharesOut}</div>
              <div className="mono" style={{ fontSize: '1.1rem', fontWeight: 700 }}>
                {simShares.toLocaleString('en-US')} {selectedPool.id}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#61746d', fontWeight: 700 }}>{t.simPsakBucket}</div>
              <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0b6643' }}>
                {waqfMode === 'MUABBAD'
                  ? lang === 'en'
                    ? 'Net Assets (Permanent Equity)'
                    : 'Aset Neto (Ekuitas Abadi)'
                  : lang === 'en'
                    ? 'Temp Waqf Liability (Mu’aqqat)'
                    : 'Liabilitas Wakaf Temporer'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#61746d', fontWeight: 700 }}>{t.simProjectedYield}</div>
              <div className="mono" style={{ fontSize: '1.05rem', fontWeight: 700 }}>
                {formatIdr(annualYieldIdr)} / yr
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.72rem', color: '#61746d', fontWeight: 700 }}>{t.simProjectedSroi}</div>
              <div className="mono" style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0b6643' }}>
                {formatIdr(totalSocialImpactIdr)}
              </div>
            </div>
            <div style={{ gridColumn: '1 / -1', borderTop: '1px dashed #cfc4ae', paddingTop: 8 }}>
              <span style={{ fontSize: '0.74rem', color: '#61746d', fontWeight: 700 }}>{t.simPrincipalReturn}: </span>
              <span className="mono" style={{ fontWeight: 700 }}>
                {waqfMode === 'MUABBAD'
                  ? lang === 'en'
                    ? 'Locked in Perpetuity (0% withdrawal)'
                    : 'Terkunci Abadi (0% penarikan)'
                  : `${formatIdr(contributionIdr)} (${termYears} yr maturity)`}
              </span>
            </div>
          </div>
        </div>

        {/* Istibdal Valuation Guard */}
        <div className="parchment-card parchment-card--alt" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div className="card-header">
              <div>
                <h3 className="card-title">
                  <RefreshCw size={18} color="#108458" />
                  {t.istibdalTitle}
                </h3>
                <p className="card-subtitle">{t.istibdalRule}</p>
              </div>
            </div>

            <div className="control-group" style={{ marginTop: 14 }}>
              <label className="control-label" htmlFor="istibdal-slider">
                <span>{t.istibdalReplacementLabel}</span>
                <span className="mono" style={{ fontWeight: 800, color: istibdalPasses ? '#0b6643' : '#9e1c22' }}>
                  {istibdalPct.toFixed(1)}%
                </span>
              </label>
              <input
                id="istibdal-slider"
                type="range"
                min={80}
                max={125}
                step={0.5}
                className={`range-slider ${istibdalPasses ? '' : 'range-slider--danger'}`}
                value={istibdalPct}
                onChange={(e) => setIstibdalPct(Number(e.target.value))}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#61746d' }}>
                <span>80% (Dilutive)</span>
                <span className="mono">100.0% Hard Floor</span>
                <span>125% (Accretive)</span>
              </div>
            </div>

            <div className={`callout ${istibdalPasses ? 'callout--emerald' : 'callout--crimson'}`} style={{ marginTop: 14 }}>
              {istibdalPasses ? <ShieldCheck size={20} /> : <ShieldAlert size={20} />}
              <div>
                <div style={{ fontWeight: 800 }}>{istibdalPasses ? t.istibdalPass : t.istibdalBlock}</div>
                <div style={{ fontSize: '0.8rem', marginTop: 4 }}>
                  {lang === 'en'
                    ? `Active Pool (${selectedPool.id}): Carrying Value ${formatIdr(selectedPool.allocatedPrincipalIdr)} → Replacement Appraisal ${formatIdr(
                        (selectedPool.allocatedPrincipalIdr * istibdalPct) / 100,
                      )}`
                    : `Kolam Aktif (${selectedPool.id}): Nilai Tercatat ${formatIdr(selectedPool.allocatedPrincipalIdr)} → Valuasi Pengganti ${formatIdr(
                        (selectedPool.allocatedPrincipalIdr * istibdalPct) / 100,
                      )}`}
                </div>
              </div>
            </div>
          </div>

          <div
            style={{
              marginTop: 16,
              padding: 12,
              borderRadius: 10,
              background: '#0c211b',
              color: '#e6eee9',
              fontSize: '0.78rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 10,
            }}
          >
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7 }}>
              <Lock size={14} color="#ecc774" />
              AAOIFI SS 60 Cl. 10/1/5 · BWI + SSB Dual Signature
            </span>
            <span className={`badge ${istibdalPasses ? 'badge--emerald-dark' : 'badge--crimson-dark'}`}>
              {istibdalPasses ? 'GUARD PASS' : 'TX REVERT'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
