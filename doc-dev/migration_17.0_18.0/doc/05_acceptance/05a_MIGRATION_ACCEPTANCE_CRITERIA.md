# Migration Acceptance Criteria — product_history_report

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/01b_BASELINE_SPEC.md` dan kode 17.0 yang berjalan — **bukan** `03_spec/03_MIGRATION_SPEC.md`
**Tanggal:** 2026-08-24

> Semua AC di sini diwarisi langsung dari `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md` (AC-01..AC-05, sudah dikonfirmasi lewat 8 integration test nyata di Step 04 backfill) — bukan ditulis ulang dari nol, hanya dipetakan ke `BSL-NNN` (`01b_BASELINE_SPEC.md`) dan ditegaskan berlaku IDENTIK di 18.0.

---

## AC-01 — Tombol Stock History (verifies BSL-001, BSL-003)

**AC-01-01** (verifies `BSL-001`)
Given user membuka form `product.template` (mode read atau edit, produk apapun) di 18.0
When form ter-render
Then tombol statistik "Stock History" (icon `fa-signal`) muncul di kotak tombol, tepat setelah tombol "Stock Moves" bawaan `stock` — identik dengan 17.0.

**AC-01-02** (verifies `BSL-001`, `BSL-003`)
Given user berada di form produk manapun di 18.0
When user klik tombol "Stock History"
Then window action terbuka dengan judul "Stocks Histories", `view_mode` **`graph,pivot,list`** (bukan `graph,pivot,tree` — token berubah karena migrasi platform, BUKAN perubahan behavior, lihat `03_MIGRATION_SPEC.md` DIFF-02), berisi baris `stock.history.view` yang `date >= date_debut` (12 bulan sebelum awal bulan berjalan) untuk produk itu saja — konten & filter identik dengan 17.0.

---

## AC-02 — Isi laporan per produk (verifies BSL-002, BSL-005)

**AC-02-01** (verifies `BSL-005`)
Given produk X punya riwayat `stock.move` (state `done`) sejak lebih dari 13 bulan lalu, di 18.0
When tombol "Stock History" diklik untuk produk X
Then baris `stock.history.view` yang ditampilkan mencakup satu baris per bulan untuk 12 bulan terakhir, dengan `qty` (running-sum) yang sudah memperhitungkan akumulasi seluruh histori sebelumnya — identik dengan 17.0.

**AC-02-02** (verifies `BSL-002` — **HARUS TETAP ADA, bukan diperbaiki**, lihat `FINDINGS.md` MF-01)
Given dua user membuka form produk BERBEDA dan klik "Stock History" hampir bersamaan, di 18.0
When request keduanya dieksekusi berdekatan
Then perilaku tetap TIDAK deterministik sama seperti 17.0 (race condition SQL view global tetap ada) — kalau di 18.0 perilaku ini "membaik secara tidak sengaja" (misal karena perubahan locking internal Postgres/ORM), itu perlu dicatat sebagai temuan, BUKAN dianggap otomatis benar tanpa verifikasi (behavior yang berubah dari source, walau ke arah "lebih baik", tetap wajib dilaporkan sebagai gap ke `FINDINGS.md`).

---

## AC-03 — Perhitungan income/outcome (verifies BSL-004)

**AC-03-01** (verifies `BSL-004`)
Given ada `stock.move` (done) dari lokasi customer ke lokasi internal warehouse, di 18.0
When view di-rebuild untuk produk itu
Then quantity move itu masuk kolom `income` bulan terjadinya, TIDAK masuk `outcome` — identik dengan 17.0.

**AC-03-02** (verifies `BSL-004` — **HARUS TETAP ADA, bukan diperbaiki**, lihat `FINDINGS.md` MF-02)
Given ada `stock.move` (done) internal→internal, di 18.0
When view di-rebuild
Then quantity move itu tetap masuk KEDUA kolom `income` DAN `outcome` pada bulan yang sama — double-count ini WAJIB tetap terjadi identik dengan 17.0, bukan bug yang diperbaiki saat migrasi.

---

## AC-04 — Filter multi-company (verifies BSL-006)

**AC-04-01** (verifies `BSL-006`)
Given user login dengan company aktif = Company A saja, ada `stock.move` untuk produk X di Company B, di 18.0
When user klik "Stock History" untuk produk X
Then baris yang menghitung move Company B TIDAK ikut ke income/outcome/qty — identik dengan 17.0.

---

## AC-05 — Akses model report (verifies BSL-007, BSL-008)

**AC-05-01** (verifies `BSL-007` — **HARUS TETAP ADA, bukan diperbaiki**, lihat `FINDINGS.md` MF-03)
Given user internal manapun (tanpa grup khusus Inventory) punya akses baca ke `product.template`, di 18.0
When user membuka `stock.history.view`
Then `read` tetap diizinkan tanpa pembatasan grup — identik dengan 17.0 (ACL longgar ini dipertahankan, bukan diperketat).

**AC-05-02** (verifies `BSL-008`)
Given user mencoba `create`/`write`/`unlink` langsung ke `stock.history.view`, di 18.0
When request dikirim
Then operasi tetap GAGAL di level database (Postgres VIEW tanpa `INSTEAD OF` trigger) — identik dengan 17.0, bukan diblokir ACL.

---

## Catatan Traceability

Semua `BSL-NNN` di `01b_BASELINE_SPEC.md` sudah tercakup AC di atas KECUALI `BSL-009` (ORM cache stale, `FINDINGS.md` MF-04 — sudah dicakup test existing `test_ac_04_01` sebagai efek samping metodologi test, bukan AC produksi terpisah), `BSL-010`/`BSL-011` (dead code/import, tidak actionable sebagai AC — cukup dicatat di baseline spec).
