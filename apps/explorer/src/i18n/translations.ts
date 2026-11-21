import { Lang } from '../data/genesisData';

export const UI_COPY: Record<
  Lang,
  {
    brandSubtitle: string;
    portalTitle: string;
    nazhirBadge: string;
    auditBadge: string;
    tabs: {
      vaults: string;
      waterfall: string;
      hisbah: string;
      merkle: string;
      forensic: string;
      brand: string;
    };
    kpis: {
      principalLabel: string;
      principalValue: string;
      principalSub: string;
      poolsLabel: string;
      poolsValue: string;
      poolsSub: string;
      auditLabel: string;
      auditValue: string;
      auditSub: string;
      waterLabel: string;
      waterValue: string;
      waterSub: string;
    };
    vaults: {
      heading: string;
      subheading: string;
      psakTitle: string;
      psakSubtitle: string;
      colYear: string;
      colStatus: string;
      colAssets: string;
      colTempLiab: string;
      colNetAssets: string;
      colDiff: string;
      poolsTitle: string;
      sharePrice: string;
      sroiLabel: string;
      yieldLabel: string;
      principalLabel: string;
      simTitle: string;
      simSubtitle: string;
      simPoolLabel: string;
      simAmountLabel: string;
      simTypeLabel: string;
      muabbadLabel: string;
      muabbadDesc: string;
      muaqqatLabel: string;
      muaqqatDesc: string;
      simTermLabel: string;
      simSharesOut: string;
      simPsakBucket: string;
      simProjectedYield: string;
      simProjectedSroi: string;
      simPrincipalReturn: string;
      istibdalTitle: string;
      istibdalRule: string;
      istibdalReplacementLabel: string;
      istibdalPass: string;
      istibdalBlock: string;
    };
    waterfall: {
      heading: string;
      subheading: string;
      grossYieldLabel: string;
      sinkingLabel: string;
      nazhirLabel: string;
      mauqufLabel: string;
      bastGateLabel: string;
      bastSigned: string;
      bastPending: string;
      invariantLockTitle: string;
      invariantLockDesc: string;
      clampButton: string;
      invariantOk: string;
      journalTitle: string;
      escrowHeld: string;
      released: string;
    };
    hisbah: {
      heading: string;
      subheading: string;
      chamber1Title: string;
      chamber1Sub: string;
      whaleAlert: string;
      chamber2Title: string;
      chamber2Sub: string;
      countdownLabel: string;
      zeroBurnTitle: string;
      zeroBurnDesc: string;
      proposalsTitle: string;
      simulateVoteBtn: string;
      ssbSignBtn: string;
      ssbVetoBtn: string;
      resetGovernanceBtn: string;
      rawTokensCol: string;
      didCol: string;
      effectiveWeightCol: string;
      voteCol: string;
      capturedBadge: string;
    };
    merkle: {
      heading: string;
      subheading: string;
      selectLeafTitle: string;
      payloadTitle: string;
      resetPayloadBtn: string;
      tamperBtn: string;
      verifiedBadge: string;
      tamperBadge: string;
      innerHashLabel: string;
      leafHashLabel: string;
      anchoredRootLabel: string;
      computedRootLabel: string;
      proofArrayLabel: string;
      stepTraceTitle: string;
      oddNodeNote: string;
    };
    forensic: {
      heading: string;
      subheading: string;
      approvedTitle: string;
      approvedVerdict: string;
      rejectedTitle: string;
      rejectedVerdict: string;
      riskScoreLabel: string;
      matrixTitle: string;
      colDimension: string;
      colBenchmark: string;
      colRejected: string;
      colRule: string;
    };
    brand: {
      heading: string;
      subheading: string;
      semioticsTitle: string;
      semioticsSubtitle: string;
      pillar1Title: string;
      pillar1Desc: string;
      pillar2Title: string;
      pillar2Desc: string;
      pillar3Title: string;
      pillar3Desc: string;
      logosTitle: string;
      logosSubtitle: string;
      downloadOgBtn: string;
      poolsTitle: string;
      poolsSubtitle: string;
      paletteTitle: string;
      paletteSubtitle: string;
      typographyTitle: string;
      typographySubtitle: string;
      collateralTitle: string;
      collateralSubtitle: string;
      onePagerIdBtn: string;
      onePagerEnBtn: string;
      certTemplateBtn: string;
      boilerplateTitle: string;
      boilerplateText: string;
      pitchTitle: string;
      pitchText: string;
      copyBtn: string;
      copiedLabel: string;
    };
    footer: {
      disclaimer: string;
      partners: string;
    };
  }
> = {
  en: {
    brandSubtitle: 'Institutional Explorer & Digital Hisbah Portal',
    portalTitle: 'WAQF DAO',
    nazhirBadge: 'Yayasan Amal Produktif Indonesia • STBPN BWI 3.3.00386',
    auditBadge: '4× KAP WTP (2022–2025) • PSAK 412 Balanced',
    tabs: {
      vaults: 'Endowment Vaults',
      waterfall: 'PSAK 412 Waterfall',
      hisbah: 'Digital Hisbah DAO',
      merkle: 'Odoo Merkle Verifier',
      forensic: 'AI CIO Forensics',
      brand: 'Brand & Media Kit',
    },
    kpis: {
      principalLabel: 'Principal Preservation',
      principalValue: '100% Intact',
      principalSub: 'Total Assets Rp 1,404,880,000 • Diff Rp 0',
      poolsLabel: 'Genesis Endowment Pools',
      poolsValue: '5 Active Vaults',
      poolsSub: 'WPUD · WPUM · WPAIR · WPPAL · WPMAS',
      auditLabel: 'External Audit Streak',
      auditValue: '4× KAP WTP',
      auditSub: 'Unqualified Opinions FY 2022–2025',
      waterLabel: 'WPAIR Clean Water Impact',
      waterValue: '4.11× SROI',
      waterSub: '41 Active Clusters • 26,357 Beneficiaries',
    },
    vaults: {
      heading: 'Endowment Vaults (Mu’abbad & Mu’aqqat)',
      subheading:
        'Ring-fenced productive waqf portfolios under PSAK 412 accounting and AAOIFI Shariah Standard 60 asset preservation.',
      psakTitle: 'PSAK 412 Financial Trajectory (2024–2026 Projection)',
      psakSubtitle: 'Strict balance sheet equality: Assets = Temporary Waqf Liabilities + Net Assets (Diff = Rp 0)',
      colYear: 'Fiscal Year',
      colStatus: 'Audit / Projection Status',
      colAssets: 'Total Assets',
      colTempLiab: 'Temp Waqf Liabilities (Mu’aqqat)',
      colNetAssets: 'Net Assets (Mu’abbad)',
      colDiff: 'Diff',
      poolsTitle: '5 Genesis Endowment Pools',
      sharePrice: 'Share Unit',
      sroiLabel: 'Verified SROI',
      yieldLabel: 'Est. Net Cash Yield',
      principalLabel: 'Allocated Principal',
      simTitle: 'Mu’abbad vs Mu’aqqat Endowment Simulator',
      simSubtitle:
        'Model how perpetual equity (Mu’abbad) and refundable term waqf (Mu’aqqat) map onto the PSAK 412 ledger.',
      simPoolLabel: 'Target Genesis Pool',
      simAmountLabel: 'Contribution Amount (IDR)',
      simTypeLabel: 'Endowment Perpetuity Mode',
      muabbadLabel: 'Mu’abbad (Perpetual)',
      muabbadDesc: 'Permanent PSAK 412 Net Assets; 100% principal locked forever.',
      muaqqatLabel: 'Mu’aqqat (Temporary Term)',
      muaqqatDesc: 'PSAK 412 Temporary Waqf Liability; principal refunded at maturity.',
      simTermLabel: 'Term Duration (Years)',
      simSharesOut: 'Issued Waqf Shares',
      simPsakBucket: 'PSAK 412 Classification',
      simProjectedYield: 'Annual Net Yield Generated',
      simProjectedSroi: 'Projected Social Value (SROI)',
      simPrincipalReturn: 'Principal at Maturity',
      istibdalTitle: 'Istibdal Valuation Guard (AAOIFI SS 60 Cl. 10/1/5)',
      istibdalRule:
        'Asset substitution (Istibdal) is blocked on-chain unless independent KJPP appraisal >= 100% of carrying waqf value with dual BWI & SSB approval.',
      istibdalReplacementLabel: 'Simulated Replacement Asset Appraisal (% of Carrying Value)',
      istibdalPass: 'ISTIBDAL ELIGIBLE — Value Preserved (>= 100%)',
      istibdalBlock: 'ISTIBDAL REJECTED — Value-Dilutive Swap Blocked',
    },
    waterfall: {
      heading: 'PSAK 412 & AAOIFI SS 60 Yield Waterfall',
      subheading:
        'Real-time smart-contract invariant simulator enforcing the UU 41/2004 Art. 12 10% Nazhir cap, upfront Sinking Fund, and BAST-gated Mauquf ‘Alaih.',
      grossYieldLabel: 'Gross Realized Yield (IDR / Period)',
      sinkingLabel: '1. Upfront Sinking Fund (10%–40%)',
      nazhirLabel: '2. Nazhir Operational Fee (UU 41/2004 Cap <= 10.0%)',
      mauqufLabel: '3. Mauquf ‘Alaih Distribution (Enforced >= 50.0%)',
      bastGateLabel: 'Field BAST Oracle Attestation Gate',
      bastSigned: 'BAST Signed & Anchored — Mauquf ‘Alaih Released',
      bastPending: 'BAST Pending — Mauquf ‘Alaih Held in Restricted Escrow',
      invariantLockTitle: 'SMART CONTRACT INVARIANT REVERT: NazhirCapExceeded',
      invariantLockDesc:
        'Requested Nazhir Fee exceeds the statutory 10.0% ceiling under Indonesian Waqf Law UU No. 41/2004 Art. 12. Execution is strictly locked on-chain.',
      clampButton: 'Clamp to 10.0% Statutory Cap',
      invariantOk: 'ALL STATUTORY & SHARIAH INVARIANTS SATISFIED (Execution Ready)',
      journalTitle: 'Live PSAK 412 Double-Entry Journal Preview',
      escrowHeld: 'HELD IN BAST ESCROW',
      released: 'DISBURSED TO BENEFICIARIES',
    },
    hisbah: {
      heading: 'Dual-Chamber Digital Hisbah Governance',
      subheading:
        'Anti-plutocracy Soulbound Quadratic Voting paired with an independent Shariah Supervisory Board (SSB) 21-day veto gate and Zero-Burn deposit capture.',
      chamber1Title: 'Chamber 1: Soulbound DID & Quadratic Reputation Tally',
      chamber1Sub:
        'Demonstrating anti-whale resilience: an unverified 10,000,000-token whale is capped to 10 effective votes, outweighed 109:1 by verified Nazhir & Wakif DIDs.',
      whaleAlert: '10M Token Whale Capped (No Soulbound DID)',
      chamber2Title: 'Chamber 2: SSB Multisig Veto Gate & 21-Day Review',
      chamber2Sub:
        'Shariah Supervisory Board retains absolute veto authority during the 21-day Hisbah cooling window before capital movement.',
      countdownLabel: '21-Day SSB Window Remaining',
      zeroBurnTitle: 'Zero-Burn Deposit Capture (Hifz al-Mal)',
      zeroBurnDesc:
        'Spam or Shariah-vetoed proposal bonds are NEVER burned. 100% of forfeited deposits are automatically routed into the Mu’abbad Principal Vault.',
      proposalsTitle: 'Active & Historical Hisbah Proposals',
      simulateVoteBtn: '+1 Verified Wakif Vote',
      ssbSignBtn: 'Record SSB Approval',
      ssbVetoBtn: 'Trigger SSB Veto & Capture Bond',
      resetGovernanceBtn: 'Reset Simulation',
      rawTokensCol: 'Raw Token Balance',
      didCol: 'DID / Rep',
      effectiveWeightCol: 'Effective Weight',
      voteCol: 'Stance',
      capturedBadge: 'CAPTURED TO PRINCIPAL',
    },
    merkle: {
      heading: 'Odoo 20.0 ERP Merkle Audit Verifier',
      subheading:
        'Browser-native WebCrypto SHA-256 verification matching cross-language domain separation (0x00 leaf, 0x01 sorted pair, odd node promoted unchanged).',
      selectLeafTitle: 'Select Anchored Odoo 20.0 ERP Record',
      payloadTitle: 'Canonical UTF-8 JSON Payload (Editable Tamper Sandbox)',
      resetPayloadBtn: 'Restore Canonical Payload',
      tamperBtn: 'Simulate 1-Char Tamper',
      verifiedBadge: 'VERIFIED ON-CHAIN MATCH',
      tamperBadge: 'TAMPER DETECTED — ROOT MISMATCH',
      innerHashLabel: '1. Inner Digest: sha256(utf8Bytes(payload))',
      leafHashLabel: '2. Domain-Separated Leaf: sha256(0x00 || inner)',
      anchoredRootLabel: '3. Anchored On-Chain Merkle Root (5-Leaf Genesis Batch)',
      computedRootLabel: '4. Recomputed Root from Candidate Leaf + Proof',
      proofArrayLabel: 'Inclusion Proof Siblings',
      stepTraceTitle: 'Step-by-Step Lexicographical Pair Hashing (0x01 || min || max)',
      oddNodeNote:
        '5-leaf tree exercises odd-node promotion: leaf index 4 (CWLS-WPUM) skips sibling emission at level 0 and level 1 because it is promoted unchanged.',
    },
    forensic: {
      heading: 'AI CIO Forensic Screening Console',
      subheading:
        '9-point thermodynamic, agronomic, financial, and Shariah due-diligence gate preventing capital loss before capital deployment.',
      approvedTitle: 'Approved Benchmark: Nautera Vannamei Ijarah + Qardh Hasan',
      approvedVerdict: 'PASS',
      rejectedTitle: 'Rejected External Proposal: Highland Biofloc Scheme',
      rejectedVerdict: 'REJECT_NO_GO',
      riskScoreLabel: 'Composite AI CIO Risk Score',
      matrixTitle: '9-Check Forensic Comparison Matrix',
      colDimension: 'Forensic Check',
      colBenchmark: 'Nautera Benchmark (WPUD)',
      colRejected: 'External Biofloc Proposal',
      colRule: 'Hard Gate Threshold',
    },
    brand: {
      heading: 'WAQF DAO Brand Identity & Media Kit',
      subheading:
        'Official Medina Hisbah Vault Seal vector lockups, 5 Genesis pool emblems, color tokens, and print-ready institutional press collateral.',
      semioticsTitle: 'Seal Semiotics — The Medina Hisbah Vault',
      semioticsSubtitle:
        'Every line of the WAQF DAO seal encodes Tahbisul Ashli wa Tasbilul Manfa’ah into geometric architecture.',
      pillar1Title: '1. Rub el Hizb Octagon (Principal Lock)',
      pillar1Desc:
        'Interlocked 0° and 45° squares bind the 4 WAQF Framework stages with AAOIFI SS 60, PSAK 412, Law 41/2004, and UU PDP.',
      pillar2Title: '2. Medina Arch & 0x01 Merkle Keystone',
      pillar2Desc:
        'Pointed arch sanctuary encloses the diamond SHA-256 Merkle root anchored from Odoo 20.0 ERP zero-diff ledgers.',
      pillar3Title: '3. Three-Channel PSAK 412 Waterfall',
      pillar3Desc:
        'Flows cleanly into 40% Sinking Fund, 50.5% Mauquf ‘Alaih (BAST-gated), and <=10% statutory Nazhir governance.',
      logosTitle: 'Master Vector Logo Suite (SVG & PNG)',
      logosSubtitle:
        'Font-independent custom vector paths suitable for GitHub, Odoo ERP, KAP audit books, and institutional media.',
      downloadOgBtn: 'Download 1200×630 OpenGraph PNG',
      poolsTitle: '5 Genesis Endowment Pool Emblems',
      poolsSubtitle: 'Dedicated sector crests for WPUD, WPUM, WPAIR, WPPAL, and WPMAS deployments.',
      paletteTitle: 'Canonical Color Tokens',
      paletteSubtitle: 'Click any swatch to copy its exact HEX code from theme.css.',
      typographyTitle: 'Institutional Typography System',
      typographySubtitle: 'Editorial authority paired with tabular-numeral cryptographic clarity.',
      collateralTitle: 'Print Collateral & Press Boilerplates',
      collateralSubtitle:
        'Open print-ready A4 PDF templates or copy verified institutional descriptions.',
      onePagerIdBtn: 'Executive One-Pager (ID · A4)',
      onePagerEnBtn: 'Executive Fact Sheet (EN · A4)',
      certTemplateBtn: 'Wakif AIW Certificate (A4)',
      boilerplateTitle: 'Official Press Boilerplate (EN)',
      boilerplateText:
        'WAQF DAO is an institutional, asset-backed Islamic endowment protocol initiated from Yayasan Amal Produktif Indonesia (STBPN BWI 3.3.00386) and PT Produktif Indonesia Berdaya (PT PIB), aligned with FWP and ANI. Bridging Odoo 20.0 PSAK 412 ledgers (4x KAP WTP, FY 2022-2025) with AAOIFI SS 60 ownerless smart vaults, Digital Hisbah governance, and 9-point AI CIO forensics.',
      pitchTitle: '60-Second Executive Narrative (EN)',
      pitchText:
        'Unlike speculative crypto tokens or opaque legacy bookkeeping, WAQF DAO locks permanent Mu’abbad principal inside ownerless smart vaults, enforces Law 41/2004 10% Nazhir caps, gates Mauquf ‘Alaih releases behind BAST proofs, and backs 5 pools totaling Rp 1.404B (diff = Rp 0), including 18.02% p.a. Nautera RWA and 4.11x SROI WPAIR clean water.',
      copyBtn: 'Copy',
      copiedLabel: 'Copied!',
    },
    footer: {
      disclaimer:
        'Public Institutional Transparency Portal • Governed by WAQF Framework (Wijhah · ’Azam · Qiyam · Fahs) • PSAK 412 & AAOIFI SS 60 Compliant.',
      partners:
        'Ecosystem Anchors: Yayasan Amal Produktif Indonesia (STBPN BWI 3.3.00386) · PT Produktif Indonesia Berdaya (PT PIB) · Forum Wakaf Produktif (FWP) · Asosiasi Nazhir Indonesia (ANI)',
    },
  },
  id: {
    brandSubtitle: 'Penjelajah Institusional & Portal Hisbah Digital',
    portalTitle: 'WAQF DAO',
    nazhirBadge: 'Yayasan Amal Produktif Indonesia • STBPN BWI 3.3.00386',
    auditBadge: '4× KAP WTP (2022–2025) • Neraca PSAK 412 Seimbang',
    tabs: {
      vaults: 'Brankas Wakaf',
      waterfall: 'Air Terjun PSAK 412',
      hisbah: 'Hisbah Digital DAO',
      merkle: 'Verifikator Merkle Odoo',
      forensic: 'Konsol Forensik AI CIO',
      brand: 'Kit Brand & Media',
    },
    kpis: {
      principalLabel: 'Ketahanan Pokok Wakaf',
      principalValue: '100% Utuh',
      principalSub: 'Total Aset Rp 1.404.880.000 • Selisih Rp 0',
      poolsLabel: 'Kolam Wakaf Genesis',
      poolsValue: '5 Brankas Aktif',
      poolsSub: 'WPUD · WPUM · WPAIR · WPPAL · WPMAS',
      auditLabel: 'Rekam Jejak Audit Eksternal',
      auditValue: '4× KAP WTP',
      auditSub: 'Opini Wajar Tanpa Pengecualian 2022–2025',
      waterLabel: 'Dampak Air Bersih WPAIR',
      waterValue: 'SROI 4,11×',
      waterSub: '41 Klaster Aktif • 26.357 Penerima Manfaat',
    },
    vaults: {
      heading: 'Brankas Wakaf (Mu’abbad & Mu’aqqat)',
      subheading:
        'Portofolio wakaf produktif terpagar sesuai akuntansi PSAK 412 dan prinsip pelestarian aset AAOIFI Shariah Standard 60.',
      psakTitle: 'Trajektori Keuangan PSAK 412 (Proyeksi 2024–2026)',
      psakSubtitle: 'Kesetimbangan neraca mutlak: Aset = Liabilitas Wakaf Temporer + Aset Neto (Selisih = Rp 0)',
      colYear: 'Tahun Buku',
      colStatus: 'Status Audit / Proyeksi',
      colAssets: 'Total Aset',
      colTempLiab: 'Liabilitas Wakaf Temporer (Mu’aqqat)',
      colNetAssets: 'Aset Neto (Mu’abbad)',
      colDiff: 'Selisih',
      poolsTitle: '5 Kolam Wakaf Genesis',
      sharePrice: 'Harga Unit Saham',
      sroiLabel: 'SROI Terverifikasi',
      yieldLabel: 'Est. Hasil Kas Bersih',
      principalLabel: 'Pokok Teralokasi',
      simTitle: 'Simulator Wakaf Mu’abbad vs Mu’aqqat',
      simSubtitle:
        'Simulasikan bagaimana ekuitas abadi (Mu’abbad) dan wakaf berjangka (Mu’aqqat) tercatat di buku besar PSAK 412.',
      simPoolLabel: 'Kolam Genesis Tujuan',
      simAmountLabel: 'Nominal Kontribusi (IDR)',
      simTypeLabel: 'Mode Keabadian Wakaf',
      muabbadLabel: 'Mu’abbad (Abadi)',
      muabbadDesc: 'Aset Neto PSAK 412 permanen; 100% pokok terkunci selamanya.',
      muaqqatLabel: 'Mu’aqqat (Berjangka)',
      muaqqatDesc: 'Liabilitas Wakaf Temporer PSAK 412; pokok kembali saat jatuh tempo.',
      simTermLabel: 'Durasi Jangka Waktu (Tahun)',
      simSharesOut: 'Sertifikat / Unit Diterbitkan',
      simPsakBucket: 'Klasifikasi PSAK 412',
      simProjectedYield: 'Imbal Hasil Bersih Tahunan',
      simProjectedSroi: 'Proyeksi Nilai Sosial (SROI)',
      simPrincipalReturn: 'Pengembalian Pokok Saat Jatuh Tempo',
      istibdalTitle: 'Penjaga Valuasi Istibdal (AAOIFI SS 60 Cl. 10/1/5)',
      istibdalRule:
        'Penukaran aset (Istibdal) diblokir on-chain kecuali penilaian KJPP independen >= 100% nilai tercatat dengan persetujuan ganda BWI & DPS.',
      istibdalReplacementLabel: 'Simulasi Valuasi Aset Pengganti (% dari Nilai Tercatat)',
      istibdalPass: 'ISTIBDAL MEMENUHI SYARAT — Nilai Aset Terjaga (>= 100%)',
      istibdalBlock: 'ISTIBDAL DITOLAK — Pertukaran Dilutif Diblokir',
    },
    waterfall: {
      heading: 'Air Terjun Imbal Hasil PSAK 412 & AAOIFI SS 60',
      subheading:
        'Simulator invarian smart-contract real-time yang menegakkan batas 10% UU 41/2004 Pasal 12, Sinking Fund di muka, dan penyaluran Mauquf ‘Alaih berbasis BAST.',
      grossYieldLabel: 'Imbal Hasil Bruto Terealisasi (IDR / Periode)',
      sinkingLabel: '1. Sinking Fund di Muka (10%–40%)',
      nazhirLabel: '2. Hak Pengelola / Fee Nazhir (Batas UU 41/2004 <= 10,0%)',
      mauqufLabel: '3. Penyaluran Mauquf ‘Alaih (Wajib >= 50,0%)',
      bastGateLabel: 'Gerbang Atestasi Oracle BAST Lapangan',
      bastSigned: 'BAST Terverifikasi & Ditandatangani — Dana Mauquf ‘Alaih Cair',
      bastPending: 'BAST Tertunda — Dana Mauquf ‘Alaih Ditahan di Escrow Terikat',
      invariantLockTitle: 'INVARIANT SMART CONTRACT REVERT: NazhirCapExceeded',
      invariantLockDesc:
        'Fee Nazhir yang diminta melampaui batas hukum 10,0% sesuai UU Wakaf No. 41/2004 Pasal 12. Eksekusi ditolak otomatis oleh kontrak.',
      clampButton: 'Kunci ke Batas Legal 10,0%',
      invariantOk: 'SELURUH INVARIAN SYARIAH & REGULASI TERPENUHI (Siap Eksekusi)',
      journalTitle: 'Pratinjau Jurnal Berpasangan PSAK 412',
      escrowHeld: 'DITAHAN DI ESCROW BAST',
      released: 'DISALURKAN KE PENERIMA MANFAAT',
    },
    hisbah: {
      heading: 'Tata Kelola Hisbah Digital Dua Kamar',
      subheading:
        'Pemungutan Suara Kuadratik Berbasis Soulbound DID anti-plutokrasi dipadukan dengan Hak Veto Dewan Pengawas Syariah (DPS) 21 hari & Penangkapan Deposit Zero-Burn.',
      chamber1Title: 'Kamar 1: Penghitungan Kuadratik DID Soulbound & Reputasi',
      chamber1Sub:
        'Ketahanan anti-whale: dompet whale 10.000.000 token tanpa DID dibatasi hanya 10 suara efektif, kalah 109:1 oleh Nazhir & Wakif terverifikasi.',
      whaleAlert: 'Whale 10 Juta Token Dibatasi (Tanpa DID Soulbound)',
      chamber2Title: 'Kamar 2: Gerbang Veto Multisig DPS & Jeda 21 Hari',
      chamber2Sub:
        'Dewan Pengawas Syariah memegang hak veto mutlak selama jendela tinjauan 21 hari sebelum perpindahan modal dieksekusi.',
      countdownLabel: 'Sisa Jendela Tinjauan DPS 21 Hari',
      zeroBurnTitle: 'Penangkapan Deposit Zero-Burn (Hifz al-Mal)',
      zeroBurnDesc:
        'Deposit proposal spam atau yang diveto DPS TIDAK PERNAH dibakar. 100% deposit sitaan dialirkan otomatis ke Brankas Pokok Mu’abbad.',
      proposalsTitle: 'Daftar Proposal Hisbah Aktif & Historis',
      simulateVoteBtn: '+1 Suara Wakif Terverifikasi',
      ssbSignBtn: 'Catat Persetujuan DPS',
      ssbVetoBtn: 'Jalankan Veto DPS & Sita Deposit',
      resetGovernanceBtn: 'Reset Simulasi',
      rawTokensCol: 'Saldo Token Mentah',
      didCol: 'DID / Rep',
      effectiveWeightCol: 'Bobot Efektif',
      voteCol: 'Sikap',
      capturedBadge: 'DIALIRKAN KE POKOK',
    },
    merkle: {
      heading: 'Verifikator Audit Merkle ERP Odoo 20.0',
      subheading:
        'Verifikasi SHA-256 WebCrypto langsung di peramban dengan pemisahan domain lintas-bahasa (leaf 0x00, pasangan terurut 0x01, node ganjil naik tanpa ubah).',
      selectLeafTitle: 'Pilih Catatan ERP Odoo 20.0 Terjangkar',
      payloadTitle: 'Payload JSON UTF-8 Kanonik (Sandbox Uji Manipulasi)',
      resetPayloadBtn: 'Pulihkan Payload Kanonik',
      tamperBtn: 'Simulasikan Ubah 1 Karakter',
      verifiedBadge: 'TERVERIFIKASI COCOK ON-CHAIN',
      tamperBadge: 'MANIPULASI TERDETEKSI — ROOT TIDAK COCOK',
      innerHashLabel: '1. Hash Internal: sha256(utf8Bytes(payload))',
      leafHashLabel: '2. Hash Daun Berdomain: sha256(0x00 || inner)',
      anchoredRootLabel: '3. Merkle Root Terjangkar On-Chain (Batch 5 Daun)',
      computedRootLabel: '4. Root Hasil Hitung Ulang (Daun Kandidat + Bukti)',
      proofArrayLabel: 'Array Bukti Inklusi (Sibling)',
      stepTraceTitle: 'Jejak Hashing Pasangan Leksikografis (0x01 || min || max)',
      oddNodeNote:
        'Pohon 5 daun menguji aturan node ganjil: indeks daun 4 (CWLS-WPUM) melewati emisi sibling di level 0 & 1 karena dipromosikan utuh.',
    },
    forensic: {
      heading: 'Konsol Skrining Forensik AI CIO',
      subheading:
        'Gerbang uji tuntas 9 titik (termodinamika, agronomi, finansial, dan syariah) guna mencegah penyaluran modal ke proyek cacat.',
      approvedTitle: 'Benchmark Lolos: Ijarah + Qardh Hasan Vaname Nautera',
      approvedVerdict: 'PASS',
      rejectedTitle: 'Proposal Eksternal Ditolak: Skema Bioflok Dataran Tinggi',
      rejectedVerdict: 'REJECT_NO_GO',
      riskScoreLabel: 'Skor Risiko Komposit AI CIO',
      matrixTitle: 'Matriks Perbandingan 9 Uji Forensik',
      colDimension: 'Dimensi Uji Forensik',
      colBenchmark: 'Benchmark Nautera (WPUD)',
      colRejected: 'Proposal Bioflok Eksternal',
      colRule: 'Ambang Batas Keras',
    },
    brand: {
      heading: 'Identitas Brand & Kit Pemasaran WAQF DAO',
      subheading:
        'Aset vektor resmi Medina Hisbah Vault Seal, 5 lencana kolam genesis, token warna kanonik, dan materi siaran pers siap cetak.',
      semioticsTitle: 'Filosofi Lambang — Segel Brankas Medina Hisbah',
      semioticsSubtitle:
        'Setiap elemen geometris pada segel WAQF DAO menerjemahkan Tahbisul Ashli wa Tasbilul Manfa’ah.',
      pillar1Title: '1. Oktagon Rub el Hizb (Pagar Pokok)',
      pillar1Desc:
        'Dua persegi saling kunci (0° & 45°) memadukan 4 tahap WAQF Framework dengan AAOIFI SS 60, PSAK 412, UU 41/2004, dan UU PDP.',
      pillar2Title: '2. Lengkungan Madinah & Batu Kunci 0x01',
      pillar2Desc:
        'Lengkungan mihrab membungkus berlian SHA-256 Merkle Root yang terjangkar dari neraca seimbang Odoo 20.0 ERP.',
      pillar3Title: '3. Tiga Aliran Air Terjun PSAK 412',
      pillar3Desc:
        'Mengalir terukur ke 40% Sinking Fund, 50,5% Mauquf ‘Alaih (gerbang BAST), serta <=10% hak pengelola Nazhir.',
      logosTitle: 'Paket Logo Vektor Master (SVG & PNG)',
      logosSubtitle:
        'Huruf vektor independen yang tampil tajam di GitHub, modul Odoo ERP, laporan audit KAP, hingga media sosial.',
      downloadOgBtn: 'Unduh OpenGraph PNG (1200×630)',
      poolsTitle: '5 Lencana Kolam Wakaf Genesis',
      poolsSubtitle: 'Emblem sektoral khusus untuk WPUD, WPUM, WPAIR, WPPAL, dan WPMAS.',
      paletteTitle: 'Sistem Warna Kanonik',
      paletteSubtitle: 'Klik kotak warna untuk menyalin kode HEX persis sesuai theme.css.',
      typographyTitle: 'Hierarki Tipografi Institusional',
      typographySubtitle: 'Kewibawaan editorial berpadu dengan keterbacaan angka audit tabular.',
      collateralTitle: 'Materi Cetak Eksekutif & Boilerplate Siaran Pers',
      collateralSubtitle:
        'Buka lembar fakta siap cetak ukuran A4 PDF atau salin narasi resmi lembaga.',
      onePagerIdBtn: 'Lembar Fakta Eksekutif (ID · A4)',
      onePagerEnBtn: 'Executive Fact Sheet (EN · A4)',
      certTemplateBtn: 'Templat Sertifikat AIW Wakif (A4)',
      boilerplateTitle: 'Boilerplate Siaran Pers Resmi (ID)',
      boilerplateText:
        'WAQF DAO adalah protokol infrastruktur wakaf produktif berbasis aset riil yang lahir dari praktik Yayasan Amal Produktif Indonesia (STBPN BWI 3.3.00386) dan PT Produktif Indonesia Berdaya (PT PIB) dalam ekosistem FWP dan ANI. Memadukan pembukuan Odoo 20.0 PSAK 412 (4x KAP WTP 2022-2025) dengan brankas nir-pemilik AAOIFI SS 60, Digital Hisbah, serta AI CIO Forensic Sentinel 9-Poin.',
      pitchTitle: 'Narasi Eksekutif 60 Detik (ID)',
      pitchText:
        'Berbeda dari token kripto spekulatif maupun pembukuan manual yang tertutup, WAQF DAO mengunci pokok abadi Mu’abbad dalam brankas nir-pemilik, menegakkan batas fee Nazhir <=10% UU 41/2004, mengunci pencairan Mauquf ‘Alaih dengan bukti BAST, serta mengawal Rp 1,404 Miliar aset teraudit (selisih Rp 0) termasuk Nautera 18,02% p.a. dan 41 klaster air bersih WPAIR (SROI 4,11x).',
      copyBtn: 'Salin',
      copiedLabel: 'Tersalin!',
    },
    footer: {
      disclaimer:
        'Portal Transparansi Institusional Publik • Tata Kelola WAQF Framework (Wijhah · ’Azam · Qiyam · Fahs) • Patuh PSAK 412 & AAOIFI SS 60.',
      partners:
        'Jangkar Ekosistem: Yayasan Amal Produktif Indonesia (STBPN BWI 3.3.00386) · PT Produktif Indonesia Berdaya (PT PIB) · Forum Wakaf Produktif (FWP) · Asosiasi Nazhir Indonesia (ANI)',
    },
  },
};
