# Findings — product_history_report (migrasi 17.0 → 18.0)

**Modul:** product_history_report
**Migrasi:** 17.0 → 18.0
**Terakhir update:** 2026-10-05 (hotfix keamanan pasca-rilis — lihat MF-13)

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | SQL view global `stock_history_view` di-drop+recreate per klik, race condition antar user | 1 | `[DIWARISI-SOURCE]` | Tinggi | 🔓 Terbuka — pertahankan identik kecuali dev minta fix |
| MF-02 | Transfer internal→internal dihitung ganda di income DAN outcome | 1 | `[DIWARISI-SOURCE]` | Sedang | 🔓 Terbuka — pertahankan identik |
| MF-03 | ACL `stock.history.view` tanpa grup — terbuka untuk semua user, TERMASUK portal/public | 1 / 2026-10-05 | `[DIWARISI-SOURCE]` | Sedang | ✅ DIPERBAIKI 2026-10-05 (18.0.1.0.1): `stock.group_stock_user`, baca saja — lihat MF-13 |
| MF-04 | ORM cache stale kalau `recreate_view()` dipanggil >1x dalam environment sama | 1 | `[DIWARISI-SOURCE]` | Rendah | 🔓 Terbuka — pertahankan identik |
| MF-09 | `ERROR Model stock.history.view has no table.` di log registry load (model `_auto=False` tanpa `init()`) | 2026-10-05 | `[DIWARISI-SOURCE]` | Rendah | 🔓 Terbuka — dikonfirmasi ada di 18.0 (log Docker 2026-10-05); sengaja tidak dikerjakan |
| MF-10 | **SQL injection via RPC**: `recreate_view()` publik + argumen di-f-string ke SQL — user login mana pun (termasuk portal) bisa memanggilnya | 2026-10-05 | `[DIWARISI-SOURCE]` | **Kritis** | ✅ DIPERBAIKI 2026-10-05 (18.0.1.0.1): `@api.private` + argumen dipaksa integer — lihat MF-10 & MF-13 |
| MF-13 | Rilis hotfix 2026-10-05: fix MF-10 + ACL MF-03 (18.0.1.0.1) | 2026-10-05 | rilis | — | ✅ Dipublish 2026-10-05 |

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
> **Update 2026-10-05:** DIPERBAIKI di 18.0.1.0.1. Catatan lama ("semua user internal") tidak lengkap: reproduksi Docker 2026-10-05 menunjukkan user **portal** juga bisa `search_read` model ini (peringkat dinaikkan ke Sedang). ACL kini `stock.group_stock_user`, baca saja. Lihat MF-13.
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

---

### MF-09 — `Model stock.history.view has no table` di log registry load
**Ditemukan di:** review pasca-rilis 2026-10-05
**Tag:** `[DIWARISI-SOURCE]`
**Lokasi:** `product_history_report/models/stock_history_view.py` (`_auto = False`, tanpa `init()`)
**Deskripsi:** registry mencatat ERROR sampai tombol "Stock History" pertama diklik. Dikonfirmasi muncul di log Docker 18.0 pada 2026-10-05. Hanya noise log.
**Keputusan pemilik modul:** 2026-10-05 dev: dibiarkan seperti ini.

---

### MF-10 — SQL injection via RPC pada `stock.history.view.recreate_view()`
**Ditemukan di:** review pasca-rilis 2026-10-05 (ID disamakan dengan MF-10 di `migration_19.0_20.0`)
**Tag:** `[DIWARISI-SOURCE]`
**Lokasi:** `product_history_report/models/stock_history_view.py` (`recreate_view`)
**Deskripsi:** method publik tanpa `@api.private`; `product_template_id` dan `companies` diinterpolasi f-string ke `CREATE VIEW`. Reproduksi Docker 2026-10-05 (kode rilis sebelum fix): user **internal** dan **portal** sama-sama BERHASIL memanggil `recreate_view` lewat `/web/dataset/call_kw`. Payload SQL berbahaya sengaja tidak dijalankan; dampak injection disimpulkan dari kode (argumen langsung masuk teks SQL).
**Perbaikan:** `@api.private` + `int(product_template_id)` + companies dipaksa integer — sama dengan fix 20.0. Setelah fix: pemanggilan RPC ditolak ("Private methods ... cannot be called remotely"), tombol "Stock History" untuk user Inventory tetap jalan.
**Keputusan pemilik modul:** 2026-10-05 dev: perbaiki di 18.0 dan 19.0 (membalik keputusan 2026-09-24 "versi sebelumnya belum"). 17.0 tidak disentuh.

---

### MF-13 — Rilis hotfix 2026-10-05 (18.0.1.0.1)
**Perubahan kode (dari `origin/staging/18.0`, bukan dari `migration/18.0`):** `b299826` (injection), `7504c36` (ACL), `703ec7b` (bump)
- `recreate_view`: `@api.private` + argumen dipaksa integer (MF-10).
- `security`: akses `stock.history.view` dibatasi ke `stock.group_stock_user`, baca saja (MF-03). Sebelumnya: semua user (termasuk portal/public) dengan CRUD penuh.
- Versi manifest `18.0.1.0.1`. Efek samping yang disetujui dev: user tanpa hak Inventory yang membuka form produk mendapat error akses saat klik "Stock History".

**Bukti uji (Docker, skrip RPC sama sebelum dan sesudah, upgrade lewat `button_immediate_upgrade`):**

| Skenario | Sebelum | Sesudah |
|---|---|---|
| `recreate_view` via RPC (internal / portal) | DITERIMA | ditolak |
| Portal `search_read` stok | BISA | ditolak |
| User internal tanpa grup Inventory baca | bisa | ditolak |
| User Inventory: tombol + baca | jalan | jalan |
| User Inventory create record | bisa | ditolak |

**Test suite lama (diambil dari `migration/18.0`, dijalankan di salinan kode rilis; 9 test (8 integrasi + 1 tour)):**
- `test_ac_03_01_customer_return_is_income_only` GAGAL di 18.0 baik SEBELUM maupun sesudah fix — bukan akibat hotfix; penyebab belum diselidiki.
- Setelah fix gagal karena menegaskan akses lama (diharapkan): `test_ac_05_01_read_open_for_user_without_inventory_group`. Test ini ada di `tests/` branch `migration/18.0` dan BELUM diperbarui — tindak lanjut.

**Belum teruji:** angka laporan dengan pergerakan stok nyata sebelum/sesudah (query SQL tidak diubah); tampilan browser.
**Tidak dikerjakan (keputusan dev 2026-10-05: "masih biarkan"):** MF-01 (race view global), MF-02 (transfer internal ganda), MF-09 (log noise), kode mati/import tak terpakai, rujukan "Odoo 17" di `index.html` store.
**Catatan audit operasional:** perubahan ACL berlaku setelah modul di-upgrade; ACL ada di data modul sehingga tidak ada sisa hak di database yang perlu dibersihkan.
**Rilis:** `staging/18.0` ac345f1→703ec7b; `18.0` 756e48b→eb5a926 (merge commit).
