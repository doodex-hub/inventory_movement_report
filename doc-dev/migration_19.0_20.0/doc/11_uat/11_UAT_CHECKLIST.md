# UAT Checklist — Migrasi product_history_report

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-09-24
**Status:** ✔️ Sign-off diterima (dev, via chat — dasar: test AI)

> Kriteria sukses: staf Inventory TIDAK merasakan bedanya dibanding Odoo 19, kecuali tampilan standar Odoo 20 itu sendiri (menu, warna, gaya ikon bawaan) dan satu perubahan yang disengaja: fungsi pembentuk laporan tidak lagi bisa dipanggil dari luar aplikasi (perbaikan keamanan, tidak terlihat di layar).
>
> Skrip ini disusun AI dalam bahasa awam untuk dijalankan tangan sendiri oleh business user. Kolom **Actual/Status per langkah sengaja dikosongkan** — AI tidak mengisinya.

## Catatan Sign-off (2026-09-24)

**Diterima via konfirmasi langsung dev (Kuncoro) di sesi ini: "akan di sign-off percaya pada test AI yang sudah dilakukan" — BUKAN hasil eksekusi tangan per langkah T-01..T-05.** Ditulis apa adanya (tidak diam-diam ditandai "Pass" per baris), pola sama seperti sign-off project 17.0→18.0 dan 18.0→19.0.

Dasar kepercayaan (semua dieksekusi nyata, bukan simulasi):
- **Step 9:** Run Community 15/15 & Run Enterprise 14/14 + 1 skip by design (`0 failed of 17` masing-masing), baseline 19.0 10/10 — `09_devtest/09_DEV_TESTING.md`.
- **Step 10:** 12/12 skenario `[DIKONFIRMASI]`; Odoo 19.0 & 20.0 Enterprise hidup berdampingan dengan data identik — laporan 15/15 baris identik, tampilan List identik, ikon setara, posisi tombol identik; diklik langsung lewat browser headless (Playwright) — `10_qa/10_BUSINESS_FLOW_MIGRATION.md`, bukti di `10_qa/evidence/`.

Pemetaan T-XX → bukti AI: T-01 ↔ S-01/S-04/S-05/S-06/S-12; T-02 ↔ S-03 (retur customer 7 unit masuk Input); T-03 ↔ S-03 (saldo awal 100 dari >13 bulan lalu); T-04 ↔ S-07; T-05 ↔ S-09/S-10. Kalau nanti staf Inventory ingin menjalankan skrip ini secara formal, kolom Actual/Status tetap tersedia.

---

## Persiapan Sebelum UAT (Precondition & Data)

- [ ] Modul `product_history_report` versi 20.0.1.0.0 terinstall di Odoo 20.0 staging (BUKAN database produksi).
- [ ] Login sebagai staf Inventory biasa (grup Inventory / User), bukan Administrator.
- [ ] Satu produk uji, misal **"UAT Produk Riwayat"** (tipe barang disimpan/storable) dengan transaksi pada tabel di T-02/T-03.

## Skenario Test (Test Script)

### T-01: Membuka riwayat pergerakan stok sebuah produk

**Data dummy:** produk "UAT Produk Riwayat" yang sudah punya minimal satu penerimaan tervalidasi.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Inventory → Products → Products, buka "UAT Produk Riwayat" | Form produk terbuka | | [ ] Pass [ ] Fail |
| 2 | Cari tombol **Stock History** (ikon bar sinyal) di deretan tombol atas form. Kalau tidak terlihat, klik **More** | Tombol ditemukan, ikonnya bar sinyal (bukan kotak kosong/teks aneh) | | [ ] Pass [ ] Fail |
| 3 | Klik **Stock History** | Halaman berganti ke **Stocks Histories**, pertama tampil grafik batang per bulan | | [ ] Pass [ ] Fail |
| 4 | Klik ikon Pivot, lalu ikon List (kanan atas) | Keduanya terbuka tanpa error; List berisi satu baris per akhir bulan (13 baris) | | [ ] Pass [ ] Fail |
| 5 | Klik panah dropdown di kotak pencarian → bagian **Group By** | Ada pilihan **By products, Date, Category, UOM**, bisa diklik | | [ ] Pass [ ] Fail |

### T-02: Barang masuk tercatat di kolom "Input"

**Data dummy:** Receipt dari supplier 10 unit "UAT Produk Riwayat" (validasi), lalu Return dari customer 7 unit (validasi).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka Stock History produk → List | Baris bulan berjalan: **Input** bertambah 17 (10 + 7) | | [ ] Pass [ ] Fail |
| 2 | Bandingkan kolom **Stock Quantity uom** baris terakhir dengan **On Hand** di form produk | Sama | | [ ] Pass [ ] Fail |

### T-03: Saldo awal dari transaksi lama ikut dihitung

**Data dummy:** di staging yang punya riwayat lebih dari 13 bulan (atau minta tim dev menyiapkan transaksi bertanggal lama), produk dengan penerimaan tua, misal 100 unit >13 bulan lalu.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka Stock History → List | Baris paling awal sudah menunjukkan **Stock Quantity uom = 100**, walau transaksinya lebih tua dari 12 bulan | | [ ] Pass [ ] Fail |

### T-04: Transfer antar lokasi internal (perilaku lama, sengaja dipertahankan)

**Data dummy:** Internal Transfer 4 unit dari WH/Stock ke lokasi internal lain (validasi).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka Stock History → List, baris bulan berjalan | 4 unit muncul di **Input** DAN **Output**; saldo tidak berubah — sama seperti di Odoo 19 | | [ ] Pass [ ] Fail |

### T-05: Hak akses baca laporan (perilaku lama, sengaja dipertahankan)

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Login sebagai user internal TANPA grup Inventory, buka laporan lewat link yang dibagikan staf Inventory | Laporan tetap terbaca — sama seperti Odoo 19 (lihat FINDINGS.md MF-03) | | [ ] Pass [ ] Fail |

### T-06: Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Perbaikan keamanan 20.0** (fungsi pembentuk laporan tidak bisa dipanggil dari luar aplikasi & hanya menerima angka) — tidak terlihat di layar; dibuktikan test otomatis `test_ac_07_01/02` (MF-10, SCOPE-02).
- **Data laporan tidak bisa diedit langsung** — hanya lewat developer mode; dibuktikan test `test_ac_05_02` (BSL-008).
- **Filter multi-company** — butuh instance multi-company; dibuktikan test `test_ac_04_01` (BSL-006).

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Tombol & tampilan laporan | T-01 | Diterima (dasar: test AI) | S-01, S-04, S-05, S-06, S-12 `[DIKONFIRMASI]` |
| 2 | Perhitungan laporan | T-02, T-03, T-04 | Diterima (dasar: test AI) | S-03 (15/15 baris identik 19.0↔20.0), S-07 |
| 3 | Hak akses | T-05, T-06 | Diterima (dasar: test AI) | S-09, S-10, S-11 |

## Review Item Out-of-Scope

Diterima dev 2026-09-24 (disetujui di intake/chat, `03_MIGRATION_SPEC.md` §4-5):
- Bug/quirk warisan tetap dipertahankan identik 19.0: race condition SQL view global (MF-01), double-count transfer internal (MF-02), ACL terbuka semua user (MF-03), cache stale (MF-04), log `has no table` (MF-09).
- **Perubahan disengaja:** SCOPE-01 aset store dari branch rilis 19.0; SCOPE-02 fix keamanan MF-10 **hanya di 20.0** (17.0/18.0/19.0 tetap rentan); SCOPE-03 penanda versi store/README → 20.0.

## Prasyarat Sebelum Go-Live Produksi

- [x] Rehearsal upgrade data produksi — **N/A**: port kode saja, instalasi baru di 20.0 (dikonfirmasi dev, Step 1).
- [ ] Backup database sebelum instalasi di server produksi (standar operasional).
- [x] README modul & root sudah "20.0" (A6 + SCOPE-03).
- [ ] **Dev:** sinkronkan perubahan `static/description/index.html` ke sumber `tools/variant.py` sebelum re-derive store berikutnya (MF-08).
- [ ] **Dev:** `git push` branch `migration/20.0` (manual) & proses rilis branch `20.0` sesuai alur repo.
- [ ] Opsional: backport fix MF-10 ke 19.0/18.0/17.0 (di luar migrasi ini, keputusan dev).

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| Dev / pemilik modul | Kuncoro | 2026-09-24 | Via chat: "akan di sign-off percaya pada test ai yang sudah dilakukan" |
| PM | — | — | Tidak ada di sesi ini |
| FA / User | — | — | Tidak ada di sesi ini |

> Sign-off didasarkan pada laporan/bukti eksekusi AI (Step 9/10), BUKAN eksekusi tangan skenario T-01..T-05 — dicatat transparan sesuai permintaan dev.

## Penutupan Migrasi

- [x] `doc/MIGRATION_CLOSED.md` ditulis dengan SHA commit gate Step 11 (lihat file tersebut).
