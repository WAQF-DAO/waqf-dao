# WAQF DAO Brand Identity Guidelines (`v1.0`)

**Protocol:** WAQF DAO — Institutional On-Chain Endowment Protocol  
**Jurisprudential Anchors:** AAOIFI Shari'ah Standard No. 60 · AAOIFI GS 13 · PSAK 412 · UU No. 41/2004 · UU No. 27/2022 (UU PDP)  
**Institutional Ecosystem:** Yayasan Amal Produktif Indonesia (`STBPN BWI 3.3.00386`) · PT Produktif Indonesia Berdaya (`PT PIB`) · Forum Wakaf Produktif (`FWP`) · Asosiasi Nazhir Indonesia (`ANI`)

---

## 1. Visual Philosophy & Semiotics — *"The Medina Hisbah Vault Seal"*

Identitas visual **WAQF DAO** dibangun bukan di atas estetika kripto spekulatif, melainkan dari sintesis **arsitektur Islam klasik Madinah (Neo-Pasar Madinah)** dan **ketelitian sistem audit kelembagaan**. Setiap garis pada lambang resmi memiliki makna fungsional dan yuridis yang terikat langsung dengan kaidah ***Tahbisul Ashli wa Tasbilul Manfa'ah*** (*menahan pokok aset agar abadi dan mengalirkan manfaatnya untuk umat*):

1. **Segel Oktagonal *Rub el Hizb* (8 Titik Jangkar):**  
   Dua bujur sangkar yang saling mengunci pada sudut `0°` dan `45°` membentuk bintang delapan sudut:
   - Empat sudut pertama mewakili empat fase tata kelola **WAQF Framework**: ***Wijhah*** (arah & niat), ***'Azam*** (kovenan & akad), ***Qiyam*** (eksekusi produktif), dan ***Fahs*** (audit & *Hisbah*).
   - Empat sudut pengunci melambangkan empat pilar regulasi dan fikih: **AAOIFI SS 60**, **PSAK 412**, **UU No. 41/2004**, dan **UU PDP**.
   - Secara visual, bingkai oktagonal ini merepresentasikan **Brankas Nir-Pemilik (*Dhimmah Maliyyah Mustaqillah*)** yang memagari pokok wakaf (*Hifzh al-Mal*).
2. **Lengkungan *Mihrab* Madinah di Bagian Dalam:**  
   Siluet lengkung runcing (*pointed arch*) merujuk pada tradisi arsitektur *Masjid Nabawi* dan ruang publik *Pasar Al-Manakhah*, menciptakan ruang suaka modal (*sanctuary*) yang bebas dari fungsi ekstraksi sepihak (`sweep()`).
3. **Batu Kunci Berlian *Merkle Root* (`0x01`):**  
   Pada puncak lengkungan terdapat berlian berlapis emas-zamrud yang melambangkan **Odoo 20.0 ERP SHA-256 Merkle Root**, mengikat pembukuan *off-chain* yang seimbang (`diff = Rp 0`) ke catatan abadi Layer-2.
4. **Tiga Aliran Air Terjun (*PSAK 412 Waterfall*):**  
   Dari batu kunci berlian, hasil bersih aset produktif mengalir melalui tiga saluran sejajar di atas dua garis fondasi neraca berimbang:
   - **Saluran Kiri (`10%–40%` *Sinking Fund*):** Gradien Emas–Zamrud sebagai cadangan depresiasi, pemeliharaan, dan biosekuriti aset produktif.
   - **Saluran Tengah (`>= 50%` *Mauquf 'Alaih*):** Aliran utama paling lebar berwarna Zamrud Terang (`#1EB980`), melambangkan prioritas penyaluran manfaat masyarakat yang dikunci gerbang atestasi `BAST`.
   - **Saluran Kanan (`<= 10%` *Ujrah Nazhir*):** Saluran Emas Berdaulat yang dibatasi secara matematis sesuai Pasal 12 UU No. 41/2004.

---

## 2. Master Logo System & Asset Matrix

Seluruh aset vektor dibangun menggunakan huruf vektor presisi tinggi (*font-independent paths*) sehingga tampil tajam di GitHub, peramban, dokumen cetak, maupun aplikasi Odoo tanpa ketergantungan font eksternal.

| Varian Logo | File | Penggunaan Utama |
| :--- | :--- | :--- |
| **Primary App Seal (Dark)** | [`brand/logos/waqf-dao-mark.svg`](./logos/waqf-dao-mark.svg) / `.png` (`1024px`, `512px`) | Avatar aplikasi, ikon Odoo (`256px`), Apple Touch Icon, X/LinkedIn avatar, aplikasi mobile |
| **Transparent Emblem Mark** | [`brand/logos/waqf-dao-mark-transparent.svg`](./logos/waqf-dao-mark-transparent.svg) | Overlay di atas foto lapangan, dokumen sertifikat AIW, *watermark* laporan |
| **Horizontal Lockup (Dark)** | [`brand/logos/waqf-dao-horizontal-dark.svg`](./logos/waqf-dao-horizontal-dark.svg) | Header `README.md`, portal Web3 dark-mode, banner presentasi utama, kop surat digital |
| **Horizontal Lockup (Light Parchment)** | [`brand/logos/waqf-dao-horizontal-light.svg`](./logos/waqf-dao-horizontal-light.svg) | Kertas putih (*Whitepaper*), laporan audit KAP PSAK 412, *one-pager* cetak A4, brosur resmi |
| **Stacked Institutional Crest** | [`brand/logos/waqf-dao-stacked.svg`](./logos/waqf-dao-stacked.svg) | Backdrop panggung FGD/konferensi, sampul laporan tahunan, podium lembaga |
| **Monochrome Gold Foil** | [`brand/logos/waqf-dao-mono-gold.svg`](./logos/waqf-dao-mono-gold.svg) | Cetak *hot-stamping* emas pada map akta wakaf, plakat penghargaan, sertifikat fisik |
| **Monochrome Deep Ink** | [`brand/logos/waqf-dao-mono-ink.svg`](./logos/waqf-dao-mono-ink.svg) | Stempel resmi, fotokopi akta notaris/PPAT, cetak satu warna berbiaya efisien |
| **Favicon (`64x64` / `32x32`)** | [`brand/logos/favicon.svg`](./logos/favicon.svg) | Tab peramban (`apps/explorer/public/favicon.svg` & `favicon-32x32.png`) |

### Aturan Ruang Kosong (*Clear Space*) & Ukuran Minimum

- **Clear Space Minimum:** Sisakan ruang kosong minimal sebesar **`0.25 ×` lebar segel** (`128px` pada kanvas `512px`) di keempat sisi logo sebelum teks, tepi kartu, atau elemen grafis lain.
- **Ukuran Minimum Digital:** Segel utama minimal **`24 × 24 px`** (gunakan `favicon.svg` untuk ukuran `< 40 px`); *horizontal lockup* minimal lebar **`180 px`**.
- **Ukuran Minimum Cetak:** Segel minimal **`10 mm`**; *horizontal lockup* minimal lebar **`38 mm`**.

### Larangan Penggunaan (*Visual Misuse*)

- **Jangan** merentangkan, memiringkan, atau mengubah rasio aspek `1:1` segel *Rub el Hizb*.
- **Jangan** mengganti warna saluran tengah (*Mauquf 'Alaih*) dengan warna merah (`#C2333A`) atau warna neon di luar palet resmi.
- **Jangan** menempatkan *horizontal lockup* versi gelap di atas latar belakang terang tanpa wadah kartu obsidian-emerald, atau sebaliknya.
- **Jangan** menambahkan istilah "Token Kripto", "APYs Spekulatif", atau nama entitas eksternal di luar struktur jangkar kelembagaan resmi di dalam bingkai logo.

---

## 3. Canonical Color System

Seluruh warna diselaraskan 100% dengan token CSS di `apps/explorer/src/styles/theme.css`:

| Nama Token | Kode HEX | RGB | Estimasi CMYK | Peran & Konteks Pemakaian |
| :--- | :--- | :--- | :--- | :--- |
| **Medina Obsidian** | `#06110E` | `6, 17, 14` | `80, 55, 65, 86` | Latar kanvas utama portal, *dark mode* eksekutif |
| **Deep Emerald Vault** | `#0B1D18` | `11, 29, 24` | `82, 48, 66, 75` | Panel navigasi, dasar kartu segel |
| **Card Emerald** | `#102822` | `16, 40, 34` | `82, 44, 65, 65` | Tile KPI, modul analisis, panel tabel gelap |
| **Sovereign Dinar Gold** | `#D4A84F` | `212, 168, 79` | `15, 32, 76, 4` | Bingkai utama *Rub el Hizb*, huruf `DAO`, aksen otoritas |
| **Bright Gold Highlight** | `#ECC774` | `236, 199, 116` | `8, 20, 62, 0` | Nilai KPI, subjudul di atas latar gelap, titik jangkar |
| **Productive Emerald** | `#108458` | `16, 132, 88` | `84, 18, 74, 12` | Tombol aksi primer, status lulus audit/Syariah |
| **Usufruct Bright Emerald** | `#1EB980` | `30, 185, 128` | `78, 0, 62, 0` | Aliran *Mauquf 'Alaih*, indikator *live verification* |
| **Manuscript Parchment** | `#FAF7F0` | `250, 247, 240` | `2, 2, 6, 0` | Kertas laporan *Whitepaper*, kartu baca kontras tinggi, kop cetak |
| **Deep Ink** | `#11221D` | `17, 34, 29` | `78, 48, 60, 72` | Teks utama di atas perkamen, stempel monokrom |
| **Hisbah Veto Crimson** | `#C2333A` | `194, 51, 58` | `16, 90, 74, 6` | Peringatan veto DPS, pelanggaran batas `NazhirCapExceeded` |

---

## 4. Typography Hierarchy

| Peran | Font Family | Bobot (*Weights*) | Penggunaan |
| :--- | :--- | :--- | :--- |
| **Editorial Display** | `'Instrument Serif'`, Georgia, serif | `400` Regular / Italic | Judul utama *Whitepaper*, angka hero KPI, kutipan fikih berbahasa Arab/Latin |
| **Institutional UI & Body** | `'Plus Jakarta Sans'`, system-ui, sans-serif | `400`, `500`, `600`, `700`, `800` | Narasi strategis, label tombol, isi dokumen resmi, materi kampanye media sosial |
| **Cryptographic & Audit Mono** | `'JetBrains Mono'`, monospace | `400`, `600`, `700` | Hash SHA-256, angka neraca PSAK 412 (`tabular-nums`), ticker pool (`WPUD`..`WPMAS`), nomor izin `STBPN BWI` |

---

## 5. Co-Branding & Regulatory Framing Rules

1. **Posisi Protokol vs Entitas Terdaftar:**  
   Selalu tampilkan **WAQF DAO** sebagai *infrastruktur protokol dan portal transparansi*, bukan entitas penghimpun dana terpisah yang berdiri di luar hukum. Setiap publikasi institusional wajib mencantumkan jangkar resmi:  
   *Yayasan Amal Produktif Indonesia (`STBPN BWI 3.3.00386`) · PT Produktif Indonesia Berdaya (`PT PIB`) · Forum Wakaf Produktif (`FWP`) · Asosiasi Nazhir Indonesia (`ANI`).*
2. **Standar Terminologi (`POJK 23/2025` & `AAOIFI SS 60`):**
   - Gunakan: *"Sertifikat / Unit Wakaf Tercatat On-Chain"*, *"Brankas Pokok Terpagar"*, *"Bukti Audit Merkle PSAK 412"*, *"Imbal Hasil Aset Riil Produktif"*.
   - Hindari: *"Koin Investasi"*, *"Spekulasi Token"*, *"Staking Profit Kripto"*, atau istilah yang mengaburkan status non-komersial pokok wakaf (*Mu'abbad*).
3. **Aturan Isolasi Entitas (`Zero-Spill`):**  
   Seluruh aset komunikasi, kode sumber, SVG, dan dokumen publik WAQF DAO dipastikan bersih dari rujukan entitas terpisah di luar ekosistem resmi melalui pemindai otomatis `scripts/audit_hygiene.py`.
