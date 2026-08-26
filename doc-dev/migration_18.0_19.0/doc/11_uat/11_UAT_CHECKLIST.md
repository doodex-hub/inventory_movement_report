# UAT Checklist — Migrasi product_history_report

**Step:** 11 — UAT Sign-off (final)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`
**Tanggal:** 2026-08-26

> Kriteria sukses: user (staf Inventory) TIDAK merasakan bedanya dibanding sebelum migrasi ke Odoo 19, kecuali tampilan standar Odoo 19 itu sendiri (menu, warna, layout umum — bukan bagian dari modul ini). Satu perbedaan kecil yang MEMANG disengaja: tombol "Stock History" sekarang tampil langsung di form produk (tidak perlu klik "More" lagi seperti di versi sebelumnya) — ini perbaikan tampilan bawaan Odoo 19, bukan perubahan dari modul ini.
>
> **Draft ini disiapkan AI, TAPI harus dijalankan tangan sendiri oleh business user/stakeholder** (bukan AI/developer). Kolom Actual/Status di bawah **dikosongkan dengan sengaja** — AI tidak akan mengisinya kecuali diminta eksplisit oleh orang yang bersangkutan setelah benar-benar mencoba sendiri.

---

## Persiapan Sebelum UAT (Precondition & Data)

- [ ] Modul `product_history_report` sudah terinstall di environment Odoo 19.0 yang akan dipakai UAT (staging, BUKAN database produksi asli).
- [ ] Login sebagai user staf Inventory biasa (bukan Administrator) — supaya sekaligus memvalidasi hak akses standar.
- [ ] Minimal 1 produk yang sudah punya riwayat pergerakan stok (barang masuk dari supplier, atau transfer antar lokasi) — kalau staging tidak punya data seperti itu, buat dulu 1-2 transaksi stok sederhana sebelum mulai.

## Skenario Test (Test Script)

### T-01: Melihat riwayat pergerakan stok sebuah produk

**Data dummy yang perlu dientri:** tidak perlu data baru — pakai produk apapun yang sudah punya riwayat stok (barang masuk/keluar).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka menu Inventory → Products, pilih salah satu produk yang sudah punya riwayat stok | Form produk terbuka normal | | [ ] Pass [ ] Fail |
| 2 | Cari tombol kecil "Stock History" di bagian atas form (harusnya langsung kelihatan, tidak perlu klik tombol "More" lagi) | Tombol "Stock History" ditemukan | | [ ] Pass [ ] Fail |
| 3 | Klik tombol "Stock History" | Muncul laporan baru berjudul "Stocks Histories" dengan tabel/grafik pergerakan stok bulanan produk itu | | [ ] Pass [ ] Fail |
| 4 | Coba ganti tampilan ke mode grafik (icon grafik) dan mode pivot/tabel silang (icon tabel) | Kedua mode tampilan bisa dibuka tanpa error | | [ ] Pass [ ] Fail |
| 5 | Di laporan yang terbuka, klik ikon dropdown kecil di sisi kanan kotak pencarian (search bar), lalu cek bagian "Group By" | Muncul pilihan pengelompokan: "By products", "Date", "Category", "UOM" — masih ada dan bisa diklik seperti biasa | | [ ] Pass [ ] Fail |

### T-02: Barang masuk dari luar (supplier/customer return) tercatat sebagai "Input"

**Data dummy yang perlu dientri:** 1 transaksi penerimaan barang (Receipt) untuk produk apapun, qty bebas (mis. 10 unit), pastikan statusnya "Done"/selesai divalidasi.

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka laporan "Stock History" produk yang barusan menerima barang (lihat T-01) | Laporan terbuka | | [ ] Pass [ ] Fail |
| 2 | Cari baris bulan ini (atau bulan transaksi terjadi) | Kolom "Input" bertambah sesuai qty yang diterima | | [ ] Pass [ ] Fail |
| 3 | Cek kolom "Output" pada baris yang sama | Kolom "Output" TIDAK bertambah untuk transaksi ini | | [ ] Pass [ ] Fail |

### T-03: Transfer stok antar lokasi dalam gudang yang sama — perilaku lama yang sengaja dipertahankan

**Data dummy yang perlu dientri:** 1 transaksi transfer internal (Internal Transfer) memindahkan stok dari satu lokasi rak ke lokasi rak lain, dalam gudang yang sama, qty bebas (mis. 3 unit).

| # | Langkah | Expected | Actual | Status |
|---|---|---|---|---|
| 1 | Buka laporan "Stock History" produk yang barusan ditransfer | Laporan terbuka | | [ ] Pass [ ] Fail |
| 2 | Cek kolom "Input" DAN "Output" pada bulan transaksi | **Kedua kolom bertambah** sejumlah qty yang ditransfer — ini BUKAN kesalahan, memang sudah begini sejak versi lama, dipertahankan sengaja saat migrasi | | [ ] Pass [ ] Fail |

## Item yang TIDAK Bisa Dites Lewat Tampilan Biasa (Informasi, Bukan Kegagalan)

- **Race condition kalau 2 orang klik "Stock History" bersamaan untuk produk berbeda** — potensi salah tampil data sesaat sudah ada sejak versi lama, tidak diperbaiki saat migrasi ini. Tidak praktis diuji lewat klik manual biasa.
- **Siapa saja bisa melihat laporan ini** — laporan "Stock History" tidak dibatasi ke grup Inventory tertentu, semua staf internal bisa lihat. Ini juga perilaku lama yang dipertahankan, bukan perubahan baru.

## Sign-off per Kelompok Fitur

| # | Kelompok fitur | Skenario tercakup | Status | Catatan |
|---|---|---|---|---|
| 1 | Laporan riwayat stok per produk (termasuk filter pengelompokan) | T-01, T-02 | [ ] Pass [ ] Fail | |
| 2 | Perilaku lama yang dipertahankan (double-count transfer internal) | T-03 | [ ] Pass [ ] Fail | |

## Review Item Out-of-Scope

Stakeholder mengonfirmasi sadar & menerima hal-hal berikut TIDAK diperbaiki saat migrasi ini (keputusan terpisah kalau nanti ingin diperbaiki):

- Race condition laporan saat diakses bersamaan oleh >1 user (`FINDINGS.md` MF-01).
- Transfer stok internal dihitung ganda di kolom Input dan Output (`FINDINGS.md` MF-02).
- Laporan bisa dilihat semua staf internal, tidak dibatasi grup tertentu (`FINDINGS.md` MF-03).

## Prasyarat Sebelum Go-Live Produksi

- [ ] Rehearsal upgrade sungguhan di staging (bukan cuma database test kosong) — migrasi ini "port kode saja" (tidak ada data produksi lama yang di-clone), jadi tidak ada script upgrade data untuk direhearse. Cukup pastikan instalasi bersih di staging yang representatif sebelum ke produksi.
- [ ] Backup database produksi sebelum instalasi modul versi 19.0 ini.

## Sign-off

| Role | Nama | Tanggal | Tanda tangan |
|---|---|---|---|
| Dev/Owner | | | |
| PM | | | |
| FA | | | |
| User | | | |

> Kosongkan sampai stakeholder benar-benar menjalankan skenario T-01 dst. dengan tangan sendiri (atau eksplisit menyatakan persetujuan verbal, seperti project 17.0→18.0 sebelumnya — dicatat apa adanya, bukan diam-diam ditandai sebagai eksekusi tangan tercatat) dan menyetujui.
