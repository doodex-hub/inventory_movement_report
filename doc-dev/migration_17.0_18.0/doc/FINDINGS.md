# Findings — product_history_report (migrasi 17.0 → 18.0)

**Modul:** product_history_report
**Migrasi:** 17.0 → 18.0
**Terakhir update:** 2026-08-24

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | SQL view global `stock_history_view` di-drop+recreate per klik, race condition antar user | 1 | `[DIWARISI-SOURCE]` | Tinggi | 🔓 Terbuka — pertahankan identik kecuali dev minta fix |
| MF-02 | Transfer internal→internal dihitung ganda di income DAN outcome | 1 | `[DIWARISI-SOURCE]` | Sedang | 🔓 Terbuka — pertahankan identik |
| MF-03 | ACL `stock.history.view` terbuka semua user internal tanpa `group_id` | 1 | `[DIWARISI-SOURCE]` | Rendah | 🔓 Terbuka — pertahankan identik |
| MF-04 | ORM cache stale kalau `recreate_view()` dipanggil >1x dalam environment sama | 1 | `[DIWARISI-SOURCE]` | Rendah | 🔓 Terbuka — pertahankan identik |

---

## Detail

### MF-01 — SQL view global di-drop+recreate per klik, race condition antar user
**Ditemukan di:** Step 1 (2026-08-24), diwarisi dari `doc-dev/backfill/FINDINGS.md` F-01 (2026-08-07)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-002` (`01b_BASELINE_SPEC.md`), asal `F-01` (`doc-dev/backfill/FINDINGS.md`)
**Lokasi:** `product_history_report/models/stock_history_view.py:24-26`, dipanggil dari `product_history_report/models/product_template.py:19`
**Deskripsi:** `recreate_view()` men-drop lalu create ulang SQL view global `stock_history_view` (nama fisik satu-satunya di database) tanpa locking, di-scope ke satu produk+company lewat f-string SQL. Dua klik ber-dekatan (user berbeda, produk berbeda) berpotensi race condition.
**Dampak di 18.0:** Sama seperti 17.0 — bug ini bagian dari behavior yang harus dipertahankan identik (`CLAUDE_TEMPLATE.md` §Source of Truth), BUKAN diperbaiki saat migrasi, kecuali dev eksplisit minta sebagai perubahan yang disengaja.
**Rekomendasi:** Tidak ada tindakan saat migrasi. Kalau dev ingin fix, itu keputusan terpisah dari scope migrasi 17→18 (harus dicatat eksplisit di `01a_MIGRATION_INTAKE.md` §5 sebagai perubahan yang disengaja).
**Keputusan pemilik modul:** *(kosong — diisi manusia, warisan dari `F-01` yang juga belum diputuskan)*

---

### MF-02 — Transfer internal→internal dihitung ganda di income DAN outcome
**Ditemukan di:** Step 1 (2026-08-24), diwarisi dari `doc-dev/backfill/FINDINGS.md` F-02 (2026-08-07, dikonfirmasi lewat test eksekusi nyata Step 04 backfill)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-004` (`01b_BASELINE_SPEC.md`), asal `F-02` (`doc-dev/backfill/FINDINGS.md`)
**Lokasi:** `product_history_report/models/stock_history_view.py:29-33`
**Deskripsi:** `income`/`outcome` dievaluasi independen per baris move, bukan mutually exclusive — move internal→internal masuk kedua kolom sekaligus pada bulan yang sama. `qty` net tetap benar.
**Dampak di 18.0:** Harus tetap identik — angka income/outcome bulanan akan tetap menghitung seluruh aktivitas gudang (termasuk transfer internal), bukan cuma throughput eksternal murni.
**Rekomendasi:** Tidak ada tindakan saat migrasi.
**Keputusan pemilik modul:** *(kosong — diisi manusia, warisan dari `F-02` yang juga belum diputuskan)*

---

### MF-03 — ACL `stock.history.view` terbuka semua user internal tanpa `group_id`
**Ditemukan di:** Step 1 (2026-08-24), diwarisi dari `doc-dev/backfill/FINDINGS.md` F-04 (2026-08-07, dikonfirmasi test eksekusi nyata)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-007` (`01b_BASELINE_SPEC.md`), asal `F-04` (`doc-dev/backfill/FINDINGS.md`)
**Lokasi:** `product_history_report/security/ir.model.access.csv:2`
**Deskripsi:** `access_stock_history_view` beri `read/write/create/unlink=1,1,1,1` tanpa `group_id` — semua user internal bisa baca data pergerakan stok, tidak dibatasi grup Inventory. `write`/`create`/`unlink` secara praktis gagal di level database (view Postgres tanpa `INSTEAD OF` trigger), dikonfirmasi test.
**Dampak di 18.0:** Visibilitas data stok tetap terbuka ke semua user internal pasca migrasi kecuali dev minta dibatasi.
**Rekomendasi:** Tidak ada tindakan saat migrasi. Opsional (keputusan terpisah dari scope migrasi): batasi `group_id` ke `stock.group_stock_user`.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### MF-04 — ORM cache stale kalau `recreate_view()` dipanggil >1x dalam environment sama
**Ditemukan di:** Step 1 (2026-08-24), diwarisi dari `doc-dev/backfill/FINDINGS.md` F-09 (2026-08-07)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-009` (`01b_BASELINE_SPEC.md`), asal `F-09` (`doc-dev/backfill/FINDINGS.md`)
**Lokasi:** `product_history_report/models/stock_history_view.py:24-26`
**Deskripsi:** DROP+CREATE VIEW lewat SQL mentah bypass ORM cache invalidation — pemanggilan berulang dalam environment/transaksi yang sama bisa menyajikan data basi secara silent.
**Dampak di 18.0:** Sama seperti 17.0, tidak bermasalah di alur produksi normal (request baru tiap klik), tapi berisiko di skenario environment panjang (shell, batch server action).
**Rekomendasi:** Tidak ada tindakan saat migrasi. Opsional: tambah `invalidate_model()` di akhir `recreate_view()` — keputusan terpisah dari scope migrasi.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

## Cara Pakai

Lihat `migration-tool/templates/FINDINGS.md` §Cara Pakai. Ringkasnya: update file ini setiap step (1-11) menemukan gap/bug/ambiguitas baru yang butuh keputusan manusia. `F-05`/`F-06`/`F-08` di `doc-dev/backfill/FINDINGS.md` TIDAK dibawa ke sini karena tag aslinya `[HASIL-BACA]` murni (dead code/import/catatan metodologi test) — tidak genuinely butuh keputusan pemilik modul, sudah cukup tercatat di `01b_BASELINE_SPEC.md` §8 (`BSL-010`, `BSL-011`).
