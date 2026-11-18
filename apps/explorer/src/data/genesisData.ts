export type Lang = 'en' | 'id';

export interface BilingualText {
  en: string;
  id: string;
}

export interface Psak412YearRow {
  year: string;
  status: BilingualText;
  totalAssetsIdr: number;
  tempWaqfLiabilitiesIdr: number;
  netAssetsIdr: number;
  diffIdr: number;
  auditOpinion: string;
}

export interface EndowmentPool {
  id: 'WPUD' | 'WPUM' | 'WPAIR' | 'WPPAL' | 'WPMAS';
  name: BilingualText;
  sector: BilingualText;
  sharePriceIdr: number;
  sroi: number;
  annualYieldPct: number;
  allocatedPrincipalIdr: number;
  contractModel: BilingualText;
  beneficiaryMetric: BilingualText;
  istibdalAppraisalPct: number;
  waqfFrameworkPhase: string;
  highlights: BilingualText[];
}

export interface CanonicalAuditLeaf {
  id: string;
  docType: string;
  title: BilingualText;
  odooModel: string;
  erpReference: string;
  payload: string;
}

export interface Chamber1Voter {
  id: string;
  label: BilingualText;
  role: 'WHALE' | 'NAZHIR' | 'WAKIF' | 'OBSERVER';
  rawTokens: number;
  didVerified: boolean;
  reputationScore: number; // 0 - 100
  effectiveQuadraticWeight: number;
  vote: 'FOR' | 'AGAINST';
}

export interface HisbahProposal {
  id: string;
  title: BilingualText;
  pool: string;
  proposer: string;
  bondIdr: number;
  status: 'ACTIVE_SSB_REVIEW' | 'PASSED_EXECUTED' | 'VETOED_CAPTURED';
  chamber1ForPct: number;
  chamber1AgainstPct: number;
  ssbApprovals: number;
  ssbRequired: number;
  ssbVetoed: boolean;
  daysRemaining: number;
  depositCapturedToPrincipal: boolean;
  summary: BilingualText;
}

export interface ForensicCheck {
  id: number;
  dimension: BilingualText;
  benchmarkNautera: BilingualText;
  rejectedBiofloc: BilingualText;
  thresholdRule: BilingualText;
  nauteraStatus: 'PASS' | 'WARN';
  bioflocStatus: 'CRITICAL_FAIL' | 'HIGH_RISK';
  weightPts: number;
}

export const INSTITUTIONAL_ANCHORS = {
  nazhirName: 'Yayasan Amal Produktif Indonesia',
  bwiLicense: 'STBPN BWI 3.3.00386',
  spvOperator: 'PT Produktif Indonesia Berdaya (PT PIB)',
  ecosystemPartners: ['Forum Wakaf Produktif (FWP)', 'Asosiasi Nazhir Indonesia (ANI)'],
  waqfFramework: "WAQF Framework (Wijhah · 'Azam · Qiyam · Fahs)",
  kapAuditStreak: ['FY 2022 WTP', 'FY 2023 WTP', 'FY 2024 WTP', 'FY 2025 WTP'],
};

export const PSAK412_TRAJECTORY: Psak412YearRow[] = [
  {
    year: '2024',
    status: { en: 'Audited (KAP Unqualified)', id: 'Teraudit (KAP WTP)' },
    totalAssetsIdr: 1_011_600_000,
    tempWaqfLiabilitiesIdr: 25_000_000,
    netAssetsIdr: 986_600_000,
    diffIdr: 0,
    auditOpinion: 'WTP',
  },
  {
    year: '2025',
    status: { en: 'Audited (KAP Unqualified)', id: 'Teraudit (KAP WTP)' },
    totalAssetsIdr: 1_114_360_000,
    tempWaqfLiabilitiesIdr: 50_000_000,
    netAssetsIdr: 1_064_360_000,
    diffIdr: 0,
    auditOpinion: 'WTP',
  },
  {
    year: '2026',
    status: { en: '2026 Full-Year Projection', id: 'Proyeksi Penuh Tahun 2026' },
    totalAssetsIdr: 1_404_880_000,
    tempWaqfLiabilitiesIdr: 63_000_000,
    netAssetsIdr: 1_341_880_000,
    diffIdr: 0,
    auditOpinion: 'PSAK 412 Balanced',
  },
];

export const GENESIS_POOLS: EndowmentPool[] = [
  {
    id: 'WPUD',
    name: {
      en: 'WPUD — Vannamei Aquaculture RWA',
      id: 'WPUD — RWA Akuakultur Udang Vaname',
    },
    sector: {
      en: 'Productive Marine & Aquaculture Real-World Asset',
      id: 'Aset Riil Produktif Kelautan & Akuakultur',
    },
    sharePriceIdr: 100_000,
    sroi: 3.85,
    annualYieldPct: 18.02,
    allocatedPrincipalIdr: 532_400_000,
    contractModel: {
      en: 'Hybrid Ijarah Rp 532.4M + Qardh Hasan Rp 300M Working Capital',
      id: 'Hibrida Ijarah Rp 532,4 Jt + Qardh Hasan Modal Kerja Rp 300 Jt',
    },
    beneficiaryMetric: {
      en: '18.02% p.a. net cash yield to foundation; coastal pond workers & scholarships',
      id: 'Imbal hasil kas bersih 18,02% p.a. ke yayasan; pekerja tambak pesisir & beasiswa',
    },
    istibdalAppraisalPct: 108.4,
    waqfFrameworkPhase: 'Qiyam & Fahs',
    highlights: [
      {
        en: 'Principal asset ring-fenced via Ijarah asset lease (zero Mudharabah principal erosion)',
        id: 'Pokok aset dipagari kontrak sewa Ijarah (nol risiko erosi pokok Mudharabah)',
      },
      {
        en: 'Managed operationally with PT Produktif Indonesia Berdaya (PT PIB) coastal SOP',
        id: 'Dikelola operasional bersama PT Produktif Indonesia Berdaya (PT PIB) SOP pesisir',
      },
      {
        en: 'AI CIO Benchmark PASS (Risk Score 14/100) with verified cold-chain off-taker',
        id: 'Lolos Benchmark AI CIO (Skor Risiko 14/100) dengan off-taker rantai dingin terverifikasi',
      },
    ],
  },
  {
    id: 'WPUM',
    name: {
      en: 'WPUM — Multi-Sector Productive & Sovereign Sukuk CWLS',
      id: 'WPUM — Wakaf Produktif Multisektor & Sukuk Negara CWLS',
    },
    sector: {
      en: 'Sovereign Cash Waqf Linked Sukuk (CWLS) & MSME Murabahah',
      id: 'Sukuk Wakaf Negara (CWLS) & Pembiayaan Produktif UMKM',
    },
    sharePriceIdr: 100_000,
    sroi: 5.04,
    annualYieldPct: 6.75,
    allocatedPrincipalIdr: 315_000_000,
    contractModel: {
      en: 'Sovereign CWLS SWR Series + Collateralized MSME Working Capital',
      id: 'Seri CWLS Negara SWR + Modal Kerja UMKM Terjamin',
    },
    beneficiaryMetric: {
      en: '5.04x SROI multiplier across micro-enterprise empowerment & health clinics',
      id: 'Pengganda SROI 5,04x di pemberdayaan usaha mikro & klinik kesehatan',
    },
    istibdalAppraisalPct: 102.0,
    waqfFrameworkPhase: "Wijhah & 'Azam",
    highlights: [
      {
        en: '100% sovereign principal floor via Bank Indonesia / Kemenkeu CWLS registry',
        id: 'Lantai pokok 100% dijamin negara melalui registrasi CWLS Kemenkeu / BI',
      },
      {
        en: 'Supports both Mu’abbad perpetual shares and Mu’aqqat temporary certificates',
        id: 'Mendukung sertifikat abadi Mu’abbad maupun wakaf berjangka Mu’aqqat',
      },
    ],
  },
  {
    id: 'WPAIR',
    name: {
      en: 'WPAIR — Clean Water Infrastructure',
      id: 'WPAIR — Infrastruktur Air Bersih',
    },
    sector: {
      en: 'Community Boreholes, Gravity Filtration & Solar Pumping',
      id: 'Sumur Bor Komunal, Filtrasi Gravitasi & Pompa Tenaga Surya',
    },
    sharePriceIdr: 50_000,
    sroi: 4.11,
    annualYieldPct: 9.4,
    allocatedPrincipalIdr: 268_480_000,
    contractModel: {
      en: 'Istisna’ Infrastructure Build + Community O&M Sinking Reserve',
      id: 'Pembangunan Aset Istisna’ + Dana Cadangan Pemeliharaan Komunal',
    },
    beneficiaryMetric: {
      en: '41 Active Clusters • 26,357 verified beneficiaries • SROI 4.11x',
      id: '41 Klaster Aktif • 26.357 penerima manfaat terverifikasi • SROI 4,11x',
    },
    istibdalAppraisalPct: 112.5,
    waqfFrameworkPhase: 'Qiyam',
    highlights: [
      {
        en: 'Every distribution tranche requires signed BAST cluster telemetry before release',
        id: 'Setiap pencairan wajib menyertakan telemetri BAST klaster sebelum rilis dana',
      },
      {
        en: 'Independently verified SROI 4.11x health & time-saving social return',
        id: 'Terverifikasi independen SROI 4,11x dari efisiensi waktu & kesehatan warga',
      },
    ],
  },
  {
    id: 'WPPAL',
    name: {
      en: 'WPPAL — Humanitarian Perpetual Endowment',
      id: 'WPPAL — Dana Abadi Kemanusiaan',
    },
    sector: {
      en: 'Perpetual Relief Yield & Orphan Education Endowment',
      id: 'Imbal Hasil Kemanusiaan Abadi & Beasiswa Anak Yatim',
    },
    sharePriceIdr: 50_000,
    sroi: 4.25,
    annualYieldPct: 7.2,
    allocatedPrincipalIdr: 154_000_000,
    contractModel: {
      en: 'Perpetual Ring-Fenced Principal + Restricted Yield Mandate',
      id: 'Pokok Terpagar Abadi + Mandat Penyaluran Hasil Terikat',
    },
    beneficiaryMetric: {
      en: 'SROI 4.25x across emergency nutrition, medical aid & orphan tuition',
      id: 'SROI 4,25x untuk gizi darurat, bantuan medis & pendidikan yatim',
    },
    istibdalAppraisalPct: 101.8,
    waqfFrameworkPhase: 'Wijhah',
    highlights: [
      {
        en: 'Principal never spent on consumable aid — only verified net yield is disbursed',
        id: 'Pokok wakaf tidak pernah dikonsumsi — hanya imbal hasil bersih yang disalurkan',
      },
    ],
  },
  {
    id: 'WPMAS',
    name: {
      en: 'WPMAS — Mosque, Madrasah & Qur’anic Education',
      id: 'WPMAS — Masjid, Madrasah & Pendidikan Al-Qur’an',
    },
    sector: {
      en: 'Sacred Infrastructure, Solar Microgrids & Teacher Waqf',
      id: 'Infrastruktur Masjid, Mikrogrid Surya & Wakaf Guru Ngaji',
    },
    sharePriceIdr: 50_000,
    sroi: 3.9,
    annualYieldPct: 8.1,
    allocatedPrincipalIdr: 135_000_000,
    contractModel: {
      en: 'Ijarah Solar Roof + Productive Madrasah Asset Endowment',
      id: 'Ijarah Atap Surya + Wakaf Aset Produktif Madrasah',
    },
    beneficiaryMetric: {
      en: 'SROI 3.90x reducing mosque electricity OPEX & funding Qur’anic teachers',
      id: 'SROI 3,90x menekan biaya listrik masjid & mendanai kafalah pengajar Al-Qur’an',
    },
    istibdalAppraisalPct: 105.2,
    waqfFrameworkPhase: 'Fahs',
    highlights: [
      {
        en: 'Generates measurable kWh savings converted directly into teacher stipends',
        id: 'Menghasilkan penghematan kWh terukur yang dikonversi menjadi kafalah pengajar',
      },
    ],
  },
];

/**
 * Deterministic canonical JSON payloads for the Odoo 20.0 ERP Merkle Audit Verifier.
 * Count = 5 (odd leaf count intentionally exercises the spec's odd-node promotion rule).
 */
export const CANONICAL_AUDIT_LEAVES: CanonicalAuditLeaf[] = [
  {
    id: 'AIW-001',
    docType: 'AIW Certificate',
    title: {
      en: 'AIW Waqf Deed — STBPN BWI 3.3.00386',
      id: 'Akta Ikrar Wakaf (AIW) — STBPN BWI 3.3.00386',
    },
    odooModel: 'waqf.certificate.aiw',
    erpReference: 'ODOO-20/AIW-YAPI-2026-001',
    payload:
      '{"bwi_stbpn":"3.3.00386","doc_id":"AIW-YAPI-2026-001","framework":"WAQF-Wijhah-Azam-Qiyam-Fahs","nazhir":"Yayasan Amal Produktif Indonesia","perpetuity":"MUABBAD","principal_idr":532400000,"psak_class":"NET_ASSETS_UNRESTRICTED","schema":"waqf.aiw.v1"}',
  },
  {
    id: 'IJR-WPUD',
    docType: 'Ijarah + Qardh Contract',
    title: {
      en: 'Nautera Vannamei Ijarah + Qardh Hasan Contract',
      id: 'Akad Ijarah + Qardh Hasan Vaname Nautera',
    },
    odooModel: 'waqf.contract.ijarah',
    erpReference: 'ODOO-20/IJR-NAUTERA-WPUD-2026',
    payload:
      '{"annual_net_yield_pct":18.02,"cio_verdict":"PASS","contract_id":"IJR-NAUTERA-WPUD-2026","ijarah_principal_idr":532400000,"operator":"PT Produktif Indonesia Berdaya","pool":"WPUD","qardh_working_cap_idr":300000000,"risk_score":14,"sroi":3.85}',
  },
  {
    id: 'BAST-WPAIR',
    docType: 'BAST Cluster Oracle',
    title: {
      en: 'Clean Water SROI 4.11x — 41 Active Clusters BAST',
      id: 'BAST Air Bersih SROI 4,11x — 41 Klaster Aktif',
    },
    odooModel: 'waqf.distribution.bast',
    erpReference: 'ODOO-20/BAST-WPAIR-CL41-2026',
    payload:
      '{"active_clusters":41,"bast_status":"SIGNED_VERIFIED","beneficiaries":26357,"doc_id":"BAST-WPAIR-CL41-2026","mauquf_alaih_pct":70,"nazhir_fee_pct":10,"pool":"WPAIR","sinking_fund_pct":20,"sroi":4.11}',
  },
  {
    id: 'PSAK412-FY26',
    docType: 'PSAK 412 Trial Balance',
    title: {
      en: 'PSAK 412 Balance Sheet Projection (FY 2026)',
      id: 'Neraca Proyeksi PSAK 412 (Tahun Buku 2026)',
    },
    odooModel: 'account.waqf.psak412',
    erpReference: 'ODOO-20/PSAK412-TB-2026-FY',
    payload:
      '{"audit_streak":"2022-2025_KAP_WTP","balance_diff_idr":0,"fiscal_year":2026,"net_assets_idr":1341880000,"standard":"PSAK_412","temp_waqf_liabilities_idr":63000000,"total_assets_idr":1404880000}',
  },
  {
    id: 'CWLS-WPUM',
    docType: 'CWLS Sukuk Custody',
    title: {
      en: 'WPUM Sovereign CWLS & Productive Pool Custody',
      id: 'Kustodi CWLS Negara & Kolam Produktif WPUM',
    },
    odooModel: 'waqf.custody.cwls',
    erpReference: 'ODOO-20/CWLS-WPUM-SWR-2026',
    payload:
      '{"custodian":"BWI_Kemenkeu_Registry","doc_id":"CWLS-WPUM-SWR-2026","istibdal_appraisal_pct":102.0,"pool":"WPUM","principal_idr":315000000,"share_price_idr":100000,"sroi":5.04}',
  },
];

export const CHAMBER1_VOTERS: Chamber1Voter[] = [
  {
    id: 'did:waqf:whale-speculator',
    label: {
      en: 'Unverified 10M-Token Whale Wallet',
      id: 'Dompet Whale 10 Juta Token (Tanpa DID)',
    },
    role: 'WHALE',
    rawTokens: 10_000_000,
    didVerified: false,
    reputationScore: 5,
    effectiveQuadraticWeight: 10, // Capped by Soulbound DID & Reputation ceiling!
    vote: 'AGAINST',
  },
  {
    id: 'did:waqf:nazhir-yapi',
    label: {
      en: 'Yayasan Amal Produktif Indonesia (Licensed Nazhir)',
      id: 'Yayasan Amal Produktif Indonesia (Nazhir Resmi)',
    },
    role: 'NAZHIR',
    rawTokens: 120_000,
    didVerified: true,
    reputationScore: 98,
    effectiveQuadraticWeight: 346,
    vote: 'FOR',
  },
  {
    id: 'did:waqf:ani-fwp-council',
    label: {
      en: 'ANI & FWP Peer Nazhir Verifier Guild',
      id: 'Dewan Verifikator Nazhir ANI & FWP',
    },
    role: 'OBSERVER',
    rawTokens: 85_000,
    didVerified: true,
    reputationScore: 94,
    effectiveQuadraticWeight: 292,
    vote: 'FOR',
  },
  {
    id: 'did:waqf:wakif-cohort-41',
    label: {
      en: 'Verified Wakif Cohort (412 Soulbound IDs)',
      id: 'Kohort Wakif Terverifikasi (412 ID Soulbound)',
    },
    role: 'WAKIF',
    rawTokens: 210_000,
    didVerified: true,
    reputationScore: 89,
    effectiveQuadraticWeight: 458,
    vote: 'FOR',
  },
];

export const HISBAH_PROPOSALS: HisbahProposal[] = [
  {
    id: 'HIP-01',
    title: {
      en: 'WPUD Nautera Phase-2 Coastal Pond Expansion (Ijarah Tranche B)',
      id: 'Ekspansi Tambak Pesisir Nautera Fase-2 WPUD (Tranche Ijarah B)',
    },
    pool: 'WPUD',
    proposer: 'did:waqf:nazhir-yapi',
    bondIdr: 10_000_000,
    status: 'ACTIVE_SSB_REVIEW',
    chamber1ForPct: 99.1,
    chamber1AgainstPct: 0.9,
    ssbApprovals: 2,
    ssbRequired: 3,
    ssbVetoed: false,
    daysRemaining: 6,
    depositCapturedToPrincipal: false,
    summary: {
      en: 'Deploys Rp 180M into 4 additional coastal HDPE ponds under existing PT PIB Ijarah + Qardh Hasan ring-fence (18.02% net yield target).',
      id: 'Menyalurkan Rp 180 Jt ke 4 petak tambak HDPE pesisir tambahan di bawah pagar Ijarah + Qardh Hasan PT PIB (target hasil bersih 18,02%).',
    },
  },
  {
    id: 'HIP-02',
    title: {
      en: 'WPAIR Clusters 42–45 Solar Filtration Rollout',
      id: 'Pembangunan Klaster Air Bersih Surya WPAIR 42–45',
    },
    pool: 'WPAIR',
    proposer: 'did:waqf:wakif-cohort-41',
    bondIdr: 10_000_000,
    status: 'PASSED_EXECUTED',
    chamber1ForPct: 97.4,
    chamber1AgainstPct: 2.6,
    ssbApprovals: 3,
    ssbRequired: 3,
    ssbVetoed: false,
    daysRemaining: 0,
    depositCapturedToPrincipal: false,
    summary: {
      en: 'Expands WPAIR clean water infrastructure to 4 drought-prone villages (+2,400 beneficiaries) with mandatory BAST oracle gating.',
      id: 'Memperluas infrastruktur air bersih WPAIR ke 4 desa rawan kekeringan (+2.400 penerima manfaat) dengan gerbang oracle BAST wajib.',
    },
  },
  {
    id: 'HIP-03',
    title: {
      en: 'Highland Biofloc Allocation + 18% Nazhir Fee Override',
      id: 'Alokasi Bioflok Dataran Tinggi + Kenaikan Fee Nazhir 18%',
    },
    pool: 'WPUD',
    proposer: '0x9fA4...31C8 (External Speculator)',
    bondIdr: 10_000_000,
    status: 'VETOED_CAPTURED',
    chamber1ForPct: 8.2,
    chamber1AgainstPct: 91.8,
    ssbApprovals: 0,
    ssbRequired: 3,
    ssbVetoed: true,
    daysRemaining: 0,
    depositCapturedToPrincipal: true,
    summary: {
      en: 'Violated UU 41/2004 10% Nazhir cap & failed AI CIO (92/100 Risk). SSB exercised Shariah veto; Rp 10M bond captured into Mu’abbad Principal (Zero-Burn).',
      id: 'Melanggar batas 10% UU 41/2004 & gagal AI CIO (Risiko 92/100). DPS memveto; jaminan Rp 10 Jt dialihkan ke Pokok Mu’abbad (Zero-Burn).',
    },
  },
  {
    id: 'HIP-04',
    title: {
      en: 'Istibdal Appraisal Ratio Guard Update (AAOIFI SS 60 Cl. 10/1/5)',
      id: 'Pembaruan Penjaga Rasio Penilaian Istibdal (AAOIFI SS 60 Cl. 10/1/5)',
    },
    pool: 'WPUM',
    proposer: 'did:waqf:ani-fwp-council',
    bondIdr: 10_000_000,
    status: 'ACTIVE_SSB_REVIEW',
    chamber1ForPct: 96.0,
    chamber1AgainstPct: 4.0,
    ssbApprovals: 2,
    ssbRequired: 3,
    ssbVetoed: false,
    daysRemaining: 14,
    depositCapturedToPrincipal: false,
    summary: {
      en: 'Enforces minimum 102% independent KJPP appraisal buffer before any Istibdal asset substitution can execute on-chain.',
      id: 'Mewajibkan penyangga penilaian KJPP independen minimal 102% sebelum substitusi aset Istibdal dapat dieksekusi on-chain.',
    },
  },
];

export const FORENSIC_9_CHECKS: ForensicCheck[] = [
  {
    id: 1,
    dimension: {
      en: '1. Feed Conversion Ratio (FCR) Thermodynamics',
      id: '1. Termodinamika Rasio Konversi Pakan (FCR)',
    },
    benchmarkNautera: {
      en: 'FCR 1.38 (Realistic coastal intensive Vannamei range 1.35–1.55)',
      id: 'FCR 1,38 (Rentang realistis budidaya Vaname pesisir 1,35–1,55)',
    },
    rejectedBiofloc: {
      en: 'Claims FCR 0.56 — biologically impossible (1 kg dry feed cannot yield 1.78 kg shrimp dry-matter)',
      id: 'Mengklaim FCR 0,56 — mustahil secara biologis (1 kg pakan tak mungkin menghasilkan 1,78 kg biomassa)',
    },
    thresholdRule: { en: '1.20 <= FCR <= 1.80', id: '1,20 <= FCR <= 1,80' },
    nauteraStatus: 'PASS',
    bioflocStatus: 'CRITICAL_FAIL',
    weightPts: 16,
  },
  {
    id: 2,
    dimension: {
      en: '2. CAPEX Unit Cost Benchmarking',
      id: '2. Tolok Ukur Biaya Satuan CAPEX',
    },
    benchmarkNautera: {
      en: 'Rp 532.4M verified BOM across coastal HDPE ponds, paddlewheels & generators (+2.1% market parity)',
      id: 'Rp 532,4 Jt RAB terverifikasi untuk kolam HDPE pesisir, kincir & genset (+2,1% paritas pasar)',
    },
    rejectedBiofloc: {
      en: '+83.6% CAPEX markup vs verified regional aquaculture engineering benchmark',
      id: 'Mark-up CAPEX +83,6% di atas tolok ukur teknik akuakultur regional terverifikasi',
    },
    thresholdRule: { en: 'CAPEX Variance <= +15%', id: 'Varians CAPEX <= +15%' },
    nauteraStatus: 'PASS',
    bioflocStatus: 'CRITICAL_FAIL',
    weightPts: 14,
  },
  {
    id: 3,
    dimension: {
      en: '3. Thermal & Altitude Biological Regime',
      id: '3. Rezim Termal & Ketinggian Biologis',
    },
    benchmarkNautera: {
      en: 'Coastal brackish water 28.5°C–30.5°C, salinity 18–25 ppt (optimal L. vannamei growth)',
      id: 'Air payau pesisir 28,5°C–30,5°C, salinitas 18–25 ppt (pertumbuhan optimal L. vannamei)',
    },
    rejectedBiofloc: {
      en: 'Highland site (cold night water < 21°C) induces severe cold stress, immune collapse & stunting',
      id: 'Lokasi dataran tinggi (suhu malam < 21°C) memicu stres dingin, gagal imun & kerdil',
    },
    thresholdRule: { en: 'Water Temp >= 26.0°C', id: 'Suhu Air >= 26,0°C' },
    nauteraStatus: 'PASS',
    bioflocStatus: 'CRITICAL_FAIL',
    weightPts: 12,
  },
  {
    id: 4,
    dimension: {
      en: '4. Risk-Reward Ratio (RRR) Asymmetry',
      id: '4. Asimetri Rasio Risiko-Imbal Hasil (RRR)',
    },
    benchmarkNautera: {
      en: 'RRR 0.42:1 — Ijarah lease floor protects waqf principal while delivering 18.02% p.a. cash yield',
      id: 'RRR 0,42:1 — Lantai sewa Ijarah melindungi pokok wakaf dengan imbal hasil kas 18,02% p.a.',
    },
    rejectedBiofloc: {
      en: 'RRR 6.83:1 — Waqf absorbs 100% catastrophic biological downside with unverified upside claims',
      id: 'RRR 6,83:1 — Wakaf menanggung 100% risiko gagal panen biologis tanpa jaminan pengembalian',
    },
    thresholdRule: { en: 'RRR <= 1.50:1', id: 'RRR <= 1,50:1' },
    nauteraStatus: 'PASS',
    bioflocStatus: 'CRITICAL_FAIL',
    weightPts: 14,
  },
  {
    id: 5,
    dimension: {
      en: '5. Land Title & Waqf Legal Custody',
      id: '5. Sertifikat Lahan & Kustodi Hukum Wakaf',
    },
    benchmarkNautera: {
      en: 'Verified AIW / long-term registered lease deed under Yayasan Amal Produktif Indonesia (STBPN BWI 3.3.00386)',
      id: 'AIW terverifikasi / akta sewa jangka panjang atas nama Yayasan Amal Produktif Indonesia (STBPN BWI 3.3.00386)',
    },
    rejectedBiofloc: {
      en: 'Uncertified land parcel (Girik/unregistered claim) — fails BWI & Istibdal custody guard',
      id: 'Lahan belum bersertifikat (klaim tidak terdaftar) — gagal penjaga kustodi BWI & Istibdal',
    },
    thresholdRule: { en: 'SHM / AIW / Registered Lease', id: 'SHM / AIW / Sewa Terdaftar' },
    nauteraStatus: 'PASS',
    bioflocStatus: 'CRITICAL_FAIL',
    weightPts: 10,
  },
  {
    id: 6,
    dimension: {
      en: '6. Shariah Contract Integrity (AAOIFI SS 60)',
      id: '6. Integritas Akad Syariah (AAOIFI SS 60)',
    },
    benchmarkNautera: {
      en: 'Clean Hybrid Ijarah (asset rental) + Qardh Hasan (working capital) — zero gharar/riba',
      id: 'Hibrida Ijarah (sewa aset) + Qardh Hasan (modal kerja) — bebas gharar & riba',
    },
    rejectedBiofloc: {
      en: 'Defective Mudharabah with illegal fixed capital guarantee + unpermitted principal risk transfer',
      id: 'Mudharabah cacat akad dengan jaminan modal tetap terlarang + transfer risiko pokok ilegal',
    },
    thresholdRule: { en: 'SSB + AAOIFI SS 60 Compliant', id: 'Patuh DPS & AAOIFI SS 60' },
    nauteraStatus: 'PASS',
    bioflocStatus: 'CRITICAL_FAIL',
    weightPts: 10,
  },
  {
    id: 7,
    dimension: {
      en: '7. Yield Realism & Cashflow Stress Test',
      id: '7. Realisme Imbal Hasil & Uji Stres Arus Kas',
    },
    benchmarkNautera: {
      en: '18.02% p.a. net cash yield verified under -20% shrimp price stress & 80% survival rate',
      id: 'Imbal hasil kas bersih 18,02% p.a. teruji pada stres harga -20% & survival rate 80%',
    },
    rejectedBiofloc: {
      en: 'Unrealistic >45% IRR projection reliant on impossible 0.56 FCR and zero pond downtime',
      id: 'Proyeksi IRR >45% tidak realistis bergantung pada FCR mustahil 0,56 & nol jeda siklus',
    },
    thresholdRule: { en: 'DSCR >= 1.35x under stress', id: 'DSCR >= 1,35x saat stres' },
    nauteraStatus: 'PASS',
    bioflocStatus: 'HIGH_RISK',
    weightPts: 6,
  },
  {
    id: 8,
    dimension: {
      en: '8. Biosecurity & Sinking Fund Reserve',
      id: '8. Biosekuriti & Dana Cadangan (Sinking Fund)',
    },
    benchmarkNautera: {
      en: 'Mandatory 20% upfront Sinking Fund + closed-water biosecurity & EMS/WSSV PCR screening',
      id: 'Cadangan Sinking Fund wajib 20% + biosekuriti air tertutup & skrining PCR EMS/WSSV',
    },
    rejectedBiofloc: {
      en: '0% biological mortality reserve; single aeration outage wipes out entire biofloc colony in < 2 hrs',
      id: 'Cadangan mortalitas 0%; mati listrik aerasi < 2 jam memusnahkan seluruh koloni bioflok',
    },
    thresholdRule: { en: 'Sinking Fund >= 10%', id: 'Sinking Fund >= 10%' },
    nauteraStatus: 'PASS',
    bioflocStatus: 'HIGH_RISK',
    weightPts: 5,
  },
  {
    id: 9,
    dimension: {
      en: '9. Off-Taker Liquidity & ERP Traceability',
      id: '9. Likuiditas Off-Taker & Ketertelusuran ERP',
    },
    benchmarkNautera: {
      en: 'Signed B2B cold-storage off-taker + Odoo 20.0 ERP invoice & BAST Merkle anchoring',
      id: 'Off-taker cold-storage B2B terikat + faktur Odoo 20.0 ERP & penjangkaran Merkle BAST',
    },
    rejectedBiofloc: {
      en: 'No written off-taker LOI; relies on speculative spot retail sale far from processing plants',
      id: 'Tanpa LOI off-taker tertulis; bergantung penjualan eceran spekulatif jauh dari pabrik olah',
    },
    thresholdRule: { en: 'Verified B2B Off-Taker + ERP', id: 'Off-Taker B2B + ERP Terverifikasi' },
    nauteraStatus: 'PASS',
    bioflocStatus: 'HIGH_RISK',
    weightPts: 5,
  },
];
