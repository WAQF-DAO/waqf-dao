import React, { useState } from 'react';
import {
  Activity,
  Award,
  Droplets,
  GitBranch,
  Landmark,
  Layers,
  Palette,
  Scale,
  ShieldCheck,
  Vote,
} from 'lucide-react';
import { Lang } from './data/genesisData';
import { UI_COPY } from './i18n/translations';
import { WaqfLogoMark } from './components/WaqfLogoMark';
import { TabVaults } from './components/TabVaults';
import { TabWaterfall } from './components/TabWaterfall';
import { TabHisbah } from './components/TabHisbah';
import { TabMerkleVerifier } from './components/TabMerkleVerifier';
import { TabForensicConsole } from './components/TabForensicConsole';
import { TabBrandKit } from './components/TabBrandKit';

type ActiveTab = 'vaults' | 'waterfall' | 'hisbah' | 'merkle' | 'forensic' | 'brand';

export const App: React.FC = () => {
  const [lang, setLang] = useState<Lang>('en');
  const [activeTab, setActiveTab] = useState<ActiveTab>('vaults');

  const copy = UI_COPY[lang];

  const tabs: Array<{ id: ActiveTab; label: string; icon: React.ReactNode }> = [
    { id: 'vaults', label: copy.tabs.vaults, icon: <Landmark size={16} /> },
    { id: 'waterfall', label: copy.tabs.waterfall, icon: <Scale size={16} /> },
    { id: 'hisbah', label: copy.tabs.hisbah, icon: <Vote size={16} /> },
    { id: 'merkle', label: copy.tabs.merkle, icon: <GitBranch size={16} /> },
    { id: 'forensic', label: copy.tabs.forensic, icon: <Activity size={16} /> },
    { id: 'brand', label: copy.tabs.brand, icon: <Palette size={16} /> },
  ];

  return (
    <div className="app-shell">
      {/* Top Institutional Header */}
      <header className="top-header">
        <div className="brand-cluster">
          <div className="brand-seal">
            <WaqfLogoMark size={46} />
          </div>
          <div>
            <h1 className="brand-title">{copy.portalTitle}</h1>
            <p className="brand-subtitle">{copy.brandSubtitle}</p>
          </div>
        </div>

        <div className="header-right">
          <span className="header-pill header-pill--gold">
            <Award size={14} />
            {copy.nazhirBadge}
          </span>
          <span className="header-pill header-pill--emerald">
            <ShieldCheck size={14} />
            {copy.auditBadge}
          </span>

          <div className="lang-switch" role="group" aria-label="Language switcher">
            <button
              type="button"
              className={`lang-btn ${lang === 'en' ? 'active' : ''}`}
              onClick={() => setLang('en')}
            >
              EN
            </button>
            <button
              type="button"
              className={`lang-btn ${lang === 'id' ? 'active' : ''}`}
              onClick={() => setLang('id')}
            >
              ID
            </button>
          </div>
        </div>
      </header>

      {/* Overview KPI Ribbon */}
      <section className="kpi-ribbon" aria-label="Institutional KPI Summary">
        <div className="kpi-tile">
          <div className="kpi-tile__top">
            <span>{copy.kpis.principalLabel}</span>
            <ShieldCheck size={15} color="#ecc774" />
          </div>
          <div className="kpi-tile__value">{copy.kpis.principalValue}</div>
          <div className="kpi-tile__sub">{copy.kpis.principalSub}</div>
        </div>

        <div className="kpi-tile">
          <div className="kpi-tile__top">
            <span>{copy.kpis.poolsLabel}</span>
            <Layers size={15} color="#ecc774" />
          </div>
          <div className="kpi-tile__value">{copy.kpis.poolsValue}</div>
          <div className="kpi-tile__sub">{copy.kpis.poolsSub}</div>
        </div>

        <div className="kpi-tile">
          <div className="kpi-tile__top">
            <span>{copy.kpis.auditLabel}</span>
            <Award size={15} color="#ecc774" />
          </div>
          <div className="kpi-tile__value">{copy.kpis.auditValue}</div>
          <div className="kpi-tile__sub">{copy.kpis.auditSub}</div>
        </div>

        <div className="kpi-tile">
          <div className="kpi-tile__top">
            <span>{copy.kpis.waterLabel}</span>
            <Droplets size={15} color="#ecc774" />
          </div>
          <div className="kpi-tile__value">{copy.kpis.waterValue}</div>
          <div className="kpi-tile__sub">{copy.kpis.waterSub}</div>
        </div>
      </section>

      {/* 5-Tab Navigation */}
      <nav className="tab-nav" aria-label="Explorer sections">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Active Tab Content */}
      <main>
        {activeTab === 'vaults' && <TabVaults lang={lang} />}
        {activeTab === 'waterfall' && <TabWaterfall lang={lang} />}
        {activeTab === 'hisbah' && <TabHisbah lang={lang} />}
        {activeTab === 'merkle' && <TabMerkleVerifier lang={lang} />}
        {activeTab === 'forensic' && <TabForensicConsole lang={lang} />}
        {activeTab === 'brand' && <TabBrandKit lang={lang} />}
      </main>

      {/* Institutional Footer */}
      <footer className="app-footer">
        <div>{copy.footer.disclaimer}</div>
        <div>{copy.footer.partners}</div>
      </footer>
    </div>
  );
};

export default App;
