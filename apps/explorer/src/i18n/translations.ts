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
    footer: {
      disclaimer:
        'Portal Transparansi Institusional Publik • Tata Kelola WAQF Framework (Wijhah · ’Azam · Qiyam · Fahs) • Patuh PSAK 412 & AAOIFI SS 60.',
      partners:
        'Jangkar Ekosistem: Yayasan Amal Produktif Indonesia (STBPN BWI 3.3.00386) · PT Produktif Indonesia Berdaya (PT PIB) · Forum Wakaf Produktif (FWP) · Asosiasi Nazhir Indonesia (ANI)',
    },
  },
};
