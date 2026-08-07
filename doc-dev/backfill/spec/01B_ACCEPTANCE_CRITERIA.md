# Acceptance Criteria — product_history_report

**Module:** `product_history_report`
**Ref:** `01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-08-07
**Status:** Backfill retroaktif

> Format: Given/When/Then, diturunkan dari Business Rules (BR-*) di `01A_FUNCTIONAL_SPEC.md`.

---

## AC-01 — Tombol Stock History (ref BR-01)

**AC-01-01** — ref `BR-01` `[HASIL-BACA]`
Given user membuka form `product.template` (mode read atau edit, produk apapun)
When form ter-render
Then tombol statistik "Stock History" (icon sinyal) muncul di kotak tombol, tepat setelah tombol
"Stock Moves" bawaan `stock`.

**AC-01-02** — ref `BR-01` `[HASIL-BACA]`
Given user berada di form produk manapun
When user klik tombol "Stock History"
Then window action terbuka dengan judul "Stocks Histories", `view_mode` graph/pivot/tree, berisi
baris `stock.history.view` yang `date >= date_debut` (12 bulan sebelum awal bulan berjalan) untuk
produk itu saja.

---

## AC-02 — Isi laporan per produk (ref BR-02, BR-04)

**AC-02-01** — ref `BR-02`, `BR-04` `[HASIL-BACA]`
Given produk X punya riwayat `stock.move` (state `done`) sejak lebih dari 13 bulan lalu
When tombol "Stock History" diklik untuk produk X
Then baris `stock.history.view` yang ditampilkan (setelah filter `date >= date_debut` Python)
mencakup satu baris per bulan untuk 12 bulan terakhir, dengan `qty` (kolom running-sum) yang sudah
memperhitungkan akumulasi seluruh histori sebelumnya (bukan mulai dari nol di awal jendela 12
bulan) — dibuktikan lewat perbandingan `qty` bulan pertama jendela terhadap SUM manual seluruh
`income - outcome` sejak awal data.

**AC-02-02** — ref `BR-02` `[PERLU-KEPUTUSAN]`
Given dua user (A dan B) membuka form produk BERBEDA (produk A dan produk B) dan klik tombol
"Stock History" pada waktu yang HAMPIR bersamaan
When request keduanya dieksekusi berdekatan (di jendela waktu antara `DROP VIEW`/`CREATE VIEW`
salah satu request dan `SELECT` request yang lain)
Then perilaku SEKARANG tidak deterministik — salah satu user berpotensi melihat data produk yang
SALAH (milik user lain) atau mendapat error "relation does not exist" sesaat, karena `stock_history_view`
adalah satu nama tabel fisik global yang di-drop+create ulang tanpa locking. Lihat `FINDINGS.md`
F-01 untuk keputusan pemilik modul.

---

## AC-03 — Perhitungan income/outcome (ref BR-03)

**AC-03-01** — ref `BR-03` `[HASIL-BACA]`
Given ada `stock.move` (done) dari lokasi customer (usage `customer`) ke lokasi internal warehouse
(usage `internal`) — mis. return dari customer
When view di-rebuild untuk produk itu
Then quantity move itu masuk kolom `income` bulan terjadinya, TIDAK masuk `outcome` (karena source
bukan `internal`).

**AC-03-02** — ref `BR-03` `[PERLU-KEPUTUSAN]`
Given ada `stock.move` (done) internal→internal (mis. transfer rak A ke rak B, dua-duanya lokasi
usage `internal`)
When view di-rebuild
Then quantity move itu masuk KEDUA kolom `income` DAN `outcome` pada bulan yang sama (net ke `qty`
= 0 untuk move itu, tapi angka mentah income/outcome bulan itu naik oleh volume transfer internal).
Status disengaja/bug: lihat `FINDINGS.md` F-02.

---

## AC-04 — Filter multi-company (ref BR-05)

**AC-04-01** — ref `BR-05` `[HASIL-BACA]`
Given user login dengan company aktif = Company A saja (bukan multi-company allowed)
And ada `stock.move` untuk produk X di Company B (company lain, user tidak switch ke sana)
When user klik "Stock History" untuk produk X
Then baris yang menghitung move Company B TIDAK ikut ke income/outcome/qty — hanya move milik
company aktif user (`self.env.companies.ids`) yang dihitung.

---

## AC-05 — Akses model report (ref BR-06)

**AC-05-01** — ref `BR-06` `[HASIL-BACA]`
Given user internal manapun (tanpa grup khusus Inventory) punya akses baca ke `product.template`
When user membuka `stock.history.view` (lewat tombol Stock History atau `search`/`read` langsung
via RPC)
Then `read` diizinkan (ACL tidak membatasi per grup) — TIDAK ADA pembatasan visibilitas berbasis
grup untuk data pergerakan stok ini.

**AC-05-02** — ref `BR-06` `[HASIL-BACA]`
Given user mencoba `create`/`write`/`unlink` langsung ke `stock.history.view` (mis. lewat
developer mode/RPC)
When request dikirim
Then operasi kemungkinan GAGAL di level database (Postgres VIEW tanpa `INSTEAD OF` trigger) —
bukan diblokir oleh ACL Odoo (yang justru mengizinkannya secara nominal). Diverifikasi nyata di
Step 04 (`FINDINGS.md` F-04 kalau ternyata perilakunya beda dari dugaan ini).
