import React, { useState } from 'react';
import { Check, Copy, Download, ExternalLink, Palette, ShieldCheck, Sparkles, Type } from 'lucide-react';
import { Lang } from '../data/genesisData';
import { UI_COPY } from '../i18n/translations';

interface TabBrandKitProps {
  lang: Lang;
}

const COLOR_TOKENS = [
  { name: 'Medina Obsidian', hex: '#06110E', roleEn: 'Primary Canvas', roleId: 'Kanvas Utama Gelap' },
  { name: 'Deep Emerald Vault', hex: '#0B1D18', roleEn: 'Navigation & Vaults', roleId: 'Navigasi & Dasar Brankas' },
  { name: 'Sovereign Dinar Gold', hex: '#D4A84F', roleEn: 'Rub el Hizb & Governance', roleId: 'Bingkai Rub el Hizb & Emas' },
  { name: 'Bright Gold Highlight', hex: '#ECC774', roleEn: 'Hero Metrics & Highlights', roleId: 'Angka KPI & Sorotan' },
  { name: 'Productive Emerald', hex: '#108458', roleEn: 'Verified Shariah & CTAs', roleId: 'Status Patuh & Tombol Aksi' },
  { name: 'Usufruct Emerald', hex: '#1EB980', roleEn: "Mauquf 'Alaih Stream", roleId: "Aliran Mauquf 'Alaih" },
  { name: 'Manuscript Parchment', hex: '#FAF7F0', roleEn: 'Reports & High-Contrast Cards', roleId: 'Kertas Laporan & Kartu' },
  { name: 'Hisbah Veto Crimson', hex: '#C2333A', roleEn: 'SSB Veto & Cap Breach', roleId: 'Veto DPS & Pelanggaran Batas' },
];

const LOGO_ASSETS = [
  {
    id: 'mark',
    titleEn: 'Primary Medina Hisbah Seal',
    titleId: 'Segel Utama Medina Hisbah (Dark)',
    path: '/brand/logos/waqf-dao-mark.svg',
    pngPath: '/brand/logos/waqf-dao-mark-1024.png',
    bgClass: 'dark-surface',
    format: '512×512 SVG · 1024px PNG',
  },
  {
    id: 'horiz-dark',
    titleEn: 'Horizontal Institutional Lockup (Dark)',
    titleId: 'Lockup Horizontal Institusional (Gelap)',
    path: '/brand/logos/waqf-dao-horizontal-dark.svg',
    bgClass: 'dark-surface',
    format: '1200×340 SVG',
  },
  {
    id: 'horiz-light',
    titleEn: 'Horizontal Parchment Lockup (Print / KAP)',
    titleId: 'Lockup Horizontal Perkamen (Cetak / KAP)',
    path: '/brand/logos/waqf-dao-horizontal-light.svg',
    bgClass: 'light-surface',
    format: '1200×340 SVG',
  },
  {
    id: 'stacked',
    titleEn: 'Stacked Sovereign Crest',
    titleId: 'Lambang Bertumpuk (Podium / Laporan)',
    path: '/brand/logos/waqf-dao-stacked.svg',
    bgClass: 'dark-surface',
    format: '800×800 SVG',
  },
  {
    id: 'mono-gold',
    titleEn: 'Monochrome Gold Foil Mark',
    titleId: 'Tanda Monokrom Emas (Foil / Plakat)',
    path: '/brand/logos/waqf-dao-mono-gold.svg',
    bgClass: 'dark-surface',
    format: '512×512 SVG',
  },
  {
    id: 'mono-ink',
    titleEn: 'Monochrome Deep Ink Stamp',
    titleId: 'Stempel Monokrom Tinta Gelap',
    path: '/brand/logos/waqf-dao-mono-ink.svg',
    bgClass: 'light-surface',
    format: '512×512 SVG',
  },
];

const POOL_BADGES = [
  { ticker: 'WPUD', file: '/brand/pools/pool-wpud.svg' },
  { ticker: 'WPUM', file: '/brand/pools/pool-wpum.svg' },
  { ticker: 'WPAIR', file: '/brand/pools/pool-wpair.svg' },
  { ticker: 'WPPAL', file: '/brand/pools/pool-wppal.svg' },
  { ticker: 'WPMAS', file: '/brand/pools/pool-wpmas.svg' },
];

export const TabBrandKit: React.FC<TabBrandKitProps> = ({ lang }) => {
  const copy = UI_COPY[lang].brand;
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (id: string, value: string) => {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(value).catch(() => undefined);
    }
    setCopiedId(id);
    setTimeout(() => {
      setCopiedId((curr) => (curr === id ? null : curr));
    }, 1800);
  };

  return (
    <div className="stack">
      <div className="section-head">
        <h2>{copy.heading}</h2>
        <p>{copy.subheading}</p>
      </div>

      {/* Semiotics & Seal Philosophy */}
      <div className="dark-panel">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Sparkles size={18} color="#ecc774" />
              {copy.semioticsTitle}
            </h3>
            <p className="card-subtitle">{copy.semioticsSubtitle}</p>
          </div>
          <span className="badge badge--gold-dark">WAQF Framework · Rub el Hizb · PSAK 412</span>
        </div>
        <div className="grid-3">
          <div className="callout callout--gold" style={{ background: 'rgba(212,168,79,0.1)', color: '#f4f1ea' }}>
            <div>
              <strong style={{ color: '#ecc774' }}>{copy.pillar1Title}</strong>
              <p style={{ margin: '6px 0 0', color: '#a6bab3' }}>{copy.pillar1Desc}</p>
            </div>
          </div>
          <div className="callout callout--emerald" style={{ background: 'rgba(30,185,128,0.1)', color: '#f4f1ea' }}>
            <div>
              <strong style={{ color: '#6ee7b7' }}>{copy.pillar2Title}</strong>
              <p style={{ margin: '6px 0 0', color: '#a6bab3' }}>{copy.pillar2Desc}</p>
            </div>
          </div>
          <div className="callout callout--gold" style={{ background: 'rgba(212,168,79,0.1)', color: '#f4f1ea' }}>
            <div>
              <strong style={{ color: '#ecc774' }}>{copy.pillar3Title}</strong>
              <p style={{ margin: '6px 0 0', color: '#a6bab3' }}>{copy.pillar3Desc}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Logo Suite Grid */}
      <div className="parchment-card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <ShieldCheck size={18} color="#108458" />
              {copy.logosTitle}
            </h3>
            <p className="card-subtitle">{copy.logosSubtitle}</p>
          </div>
          <a
            className="btn btn--gold"
            href="/brand/social/og-banner.png"
            download="waqf-dao-og-banner.png"
          >
            <Download size={15} />
            {copy.downloadOgBtn}
          </a>
        </div>

        <div className="brand-asset-grid">
          {LOGO_ASSETS.map((asset) => (
            <div key={asset.id} className="brand-asset-card">
              <div className={`brand-asset-preview ${asset.bgClass}`}>
                <img
                  src={asset.path}
                  alt={lang === 'id' ? asset.titleId : asset.titleEn}
                  loading="lazy"
                />
              </div>
              <div className="brand-asset-meta">
                <div>
                  <div className="brand-asset-title">
                    {lang === 'id' ? asset.titleId : asset.titleEn}
                  </div>
                  <div className="brand-asset-format mono">{asset.format}</div>
                </div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  <a className="btn btn--primary" href={asset.path} download>
                    <Download size={13} />
                    SVG
                  </a>
                  {asset.pngPath && (
                    <a className="btn btn--ghost-light" href={asset.pngPath} download>
                      <Download size={13} />
                      PNG
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 5 Genesis Pool Emblems */}
      <div className="parchment-card parchment-card--alt">
        <div className="card-header">
          <div>
            <h3 className="card-title">{copy.poolsTitle}</h3>
            <p className="card-subtitle">{copy.poolsSubtitle}</p>
          </div>
        </div>
        <div className="brand-pool-grid">
          {POOL_BADGES.map((pool) => (
            <div key={pool.ticker} className="brand-pool-item">
              <img src={pool.file} alt={`${pool.ticker} Endowment Pool Emblem`} loading="lazy" />
              <a className="btn btn--ghost-light" href={pool.file} download style={{ width: '100%' }}>
                <Download size={13} />
                {pool.ticker}.svg
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* Color Swatches & Typography */}
      <div className="grid-2">
        <div className="parchment-card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <Palette size={18} color="#108458" />
                {copy.paletteTitle}
              </h3>
              <p className="card-subtitle">{copy.paletteSubtitle}</p>
            </div>
          </div>
          <div className="swatch-grid">
            {COLOR_TOKENS.map((swatch) => {
              const isCopied = copiedId === swatch.hex;
              return (
                <button
                  key={swatch.hex}
                  type="button"
                  className="swatch-btn"
                  onClick={() => handleCopy(swatch.hex, swatch.hex)}
                >
                  <span className="swatch-chip" style={{ backgroundColor: swatch.hex }} />
                  <span className="swatch-info">
                    <strong>{swatch.name}</strong>
                    <span className="mono">{isCopied ? copy.copiedLabel : swatch.hex}</span>
                    <small>{lang === 'id' ? swatch.roleId : swatch.roleEn}</small>
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="parchment-card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <Type size={18} color="#108458" />
                {copy.typographyTitle}
              </h3>
              <p className="card-subtitle">{copy.typographySubtitle}</p>
            </div>
          </div>
          <div className="stack" style={{ gap: '12px' }}>
            <div className="type-specimen">
              <div className="type-meta mono">Instrument Serif · Display &amp; Headlines</div>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: '1.9rem', lineHeight: 1.15 }}>
                Tahbisul Ashli wa Tasbilul Manfa&apos;ah
              </div>
            </div>
            <div className="type-specimen">
              <div className="type-meta mono">Plus Jakarta Sans · Institutional Body &amp; UI</div>
              <div style={{ fontFamily: 'var(--font-sans)', fontSize: '0.96rem', fontWeight: 600 }}>
                4× Opini KAP WTP (2022–2025) · Brankas Nir-Pemilik AAOIFI SS 60
              </div>
            </div>
            <div className="type-specimen">
              <div className="type-meta mono">JetBrains Mono · SHA-256 Proofs &amp; PSAK 412 Ledgers</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.84rem', color: '#0b6643' }}>
                STBPN BWI 3.3.00386 · Rp 1.404.880.000 · diff = Rp 0
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Print Collateral & Copy-Ready Boilerplates */}
      <div className="dark-panel">
        <div className="card-header">
          <div>
            <h3 className="card-title">{copy.collateralTitle}</h3>
            <p className="card-subtitle">{copy.collateralSubtitle}</p>
          </div>
        </div>

        <div className="grid-3" style={{ marginBottom: '18px' }}>
          <a
            className="btn btn--gold"
            href="/brand/collateral/executive-one-pager-id.html"
            target="_blank"
            rel="noreferrer"
          >
            <ExternalLink size={15} />
            {copy.onePagerIdBtn}
          </a>
          <a
            className="btn btn--primary"
            href="/brand/collateral/executive-one-pager-en.html"
            target="_blank"
            rel="noreferrer"
          >
            <ExternalLink size={15} />
            {copy.onePagerEnBtn}
          </a>
          <a
            className="btn btn--ghost"
            href="/brand/collateral/wakif-certificate-template.html"
            target="_blank"
            rel="noreferrer"
          >
            <ExternalLink size={15} />
            {copy.certTemplateBtn}
          </a>
        </div>

        <div className="grid-2">
          <div className="boilerplate-box">
            <div className="boilerplate-head">
              <span>{copy.boilerplateTitle}</span>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={() => handleCopy('boilerplate', copy.boilerplateText)}
              >
                {copiedId === 'boilerplate' ? <Check size={13} /> : <Copy size={13} />}
                {copiedId === 'boilerplate' ? copy.copiedLabel : copy.copyBtn}
              </button>
            </div>
            <p>{copy.boilerplateText}</p>
          </div>

          <div className="boilerplate-box">
            <div className="boilerplate-head">
              <span>{copy.pitchTitle}</span>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={() => handleCopy('pitch', copy.pitchText)}
              >
                {copiedId === 'pitch' ? <Check size={13} /> : <Copy size={13} />}
                {copiedId === 'pitch' ? copy.copiedLabel : copy.copyBtn}
              </button>
            </div>
            <p>{copy.pitchText}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
