# Implementation Log — product_history_report

**Step:** 6 — Code Migration
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-24

---

## Applicability Check

Dari `01_intake/01a_MIGRATION_INTAKE.md` §2b — modul murni backend, tidak ada fitur di bawah ini:

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| B2 (Model Kompleks) | ☐ Tidak | Tidak ada field JSON/relasi berantai/dynamic model creation |
| C1 (View Sederhana) | ☑ Ya | Modul punya `views/stock_history_view.xml` + `views/views.xml` — TIDAK N/A (beda dari kasus `advanced_sales_analysis`) |
| C2 (Semantik XML) | ☐ Tidak | Tidak ada `attrs=`/`states=`/domain-context dinamis, hanya `domain="[]"` statis |
| D1 (Controllers) | ☐ Tidak | `controllers/controllers.py` boilerplate, tidak expose route |
| D2 (Assets & CSS) | ☐ Tidak | Tidak ada `static/src/`, tidak ada key `assets` |
| E (JavaScript/Owl) | ☐ Tidak | Tidak ada file `.js` |
| F (Upgrade Template) | ☐ Tidak | Otomatis N/A karena E N/A |

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 (Manifest Bootstrap) | ✅ | 2026-08-24 |
| A2 (XML Tree→List) | ✅ | 2026-08-24 |
| G1 #1 (setelah A2) | ✅ Pass (install bersih, tapi test setup gagal — DIFF-12) | 2026-08-24 |
| A3 (Security Hardening) | ✅ N/A — ACL sudah lengkap, tidak ada perubahan (dikonfirmasi DIFF-08) | 2026-08-24 |
| G1 #2 (setelah A3, + fix DIFF-12) | ✅ Pass (install bersih + 8/8 test pass) | 2026-08-24 |
| A4 (Skeleton Integrity) | ✅ N/A — struktur folder sudah konsisten, tidak ada perubahan | 2026-08-24 |
| A5 (Python API Compat) | ✅ N/A — tidak override `create()`/`_name_search`/dst (dikonfirmasi DIFF-09) | 2026-08-24 |
| B1 (Model Risiko Rendah) | ✅ N/A — tidak ada perubahan model (dikonfirmasi DIFF-05, DIFF-06) | 2026-08-24 |
| B2 | N/A — dikonfirmasi Applicability Check | — |
| C1 (View Sederhana) | ✅ Selesai — bagian dari A2 (tree→list DUA kali dikerjakan: tag view DAN token `view_mode`) | 2026-08-24 |
| C2 | N/A — dikonfirmasi Applicability Check | — |
| D1 | N/A — dikonfirmasi Applicability Check | — |
| D2 | N/A — dikonfirmasi Applicability Check | — |
| E | N/A — dikonfirmasi Applicability Check | — |
| F | N/A — dikonfirmasi Applicability Check (otomatis, E juga N/A) | — |
| G2 (Validasi Akhir) | ✅ Pass — lihat entry [Fase G2] di bawah | 2026-08-24 |

## Riwayat Percobaan G1 (Install Test)

**Mode:** C — AI jalankan langsung (Claude Code CLI, Mode Git aktif, Docker tersedia di environment sesi).

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A2 | C | ❌ Fail (install modul sendiri SUKSES — "Module product_history_report loaded in 0.50s, 128 queries", TAPI post-install test `setUpClass` error) | `ValueError: Wrong value for product.template.type: 'product'` — DIFF-12, ditemukan baru di run ini, belum pernah tertangkap review statis step 2/3 | 2026-08-24 |
| 2 | A3 (+ fix DIFF-12 di test fixture) | C | ✅ Pass — install bersih, `0 failed, 0 error(s) of 8 tests` (dikonfirmasi silang: 8 baris `Starting TestProductHistoryReport.*` di log = 8 method test yang benar-benar dieksekusi, bukan false-pass MSYS mangling) | — | 2026-08-24 |

---

## Entri

## [Fase A1] Manifest Bootstrap

- **Scope:** `product_history_report/__manifest__.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2b Critical Blocker #1
- **Aksi:**
  - `__manifest__.py`: `'version': '17.0.1.0.0'` → `'version': '18.0.1.0.0'`
- **Secara eksplisit TIDAK dilakukan:**
  - Tidak menghapus/mengubah `depends`, `data`, atau field manifest lain apapun
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase A2] XML Tree → List (Mekanis)

- **Scope:** `product_history_report/views/stock_history_view.xml`, `product_history_report/models/product_template.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2b Critical Blocker #2-3, §2b View List Checklist #1-3
- **Aksi:**
  - `views/stock_history_view.xml` baris 51/59 (record `stock_history_tree_view2`): `<tree string="stock history">` → `<list string="stock history">`, tutup `</tree>` → `</list>`
  - `views/stock_history_view.xml` baris 66 (`action_stock_history_graph2`): `view_mode` `graph,tree,pivot` → `graph,list,pivot`
  - `views/stock_history_view.xml` baris 73 (`action_stock_history_tree2`): `view_mode` `tree,pivot,graph` → `list,pivot,graph`
  - `models/product_template.py` baris 29 (`action_open_stock_history()`): `'view_mode': 'graph,pivot,tree'` → `'graph,pivot,list'`
- **Secara eksplisit TIDAK dilakukan:**
  - Field di dalam `<list>` (date/product_template_id/categ_id/uom_id/income/outcome/qty) tidak diubah sama sekali
  - `view_type: 'form'` (DIFF-03, dead key) TIDAK dihapus — dibiarkan apa adanya, opsional cleanup di luar scope migrasi
- **Risiko:** LOW
- **Status:** ✅ Selesai — dikonfirmasi G1 #1 & #2 (install bersih, tidak ada `ParseError`)

## [Fase A3] Security Hardening

- **Scope:** `product_history_report/security/ir.model.access.csv`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` DIFF-08
- **Aksi:** Tidak ada — dikonfirmasi format CSV ACL tidak berubah 17→18, ACL yang ada (`access_stock_history_view`) sudah valid untuk model `_auto=False`.
- **Secara eksplisit TIDAK dilakukan:**
  - Tidak membatasi `group_id` (ACL longgar dipertahankan identik, `FINDINGS.md` MF-03) — ini bug/quirk source, BUKAN gap kompatibilitas 18.0
- **Risiko:** Tidak ada
- **Status:** ✅ N/A (tidak ada perubahan diperlukan)

## [Fase A4] Skeleton & Folder Integrity — N/A, dikonfirmasi Applicability Check tidak ada gap struktural (semua folder `models/`/`views/`/`security/`/`controllers/`/`static/`/`tests/` sudah konsisten, `__init__.py` lengkap)

## [Fase A5] Python API Compatibility — N/A, dikonfirmasi `03_MIGRATION_SPEC.md` DIFF-09: modul tidak override `create()`/`_name_search`/`_check_recursion`/`user_has_groups`/`check_access_rights` — tidak ada API yang perlu disesuaikan

## [Fase B1] Model Risiko Rendah — N/A, dikonfirmasi DIFF-05/DIFF-06: semua field `stock.move`/`stock.move.line`/`product.product`/`product.template` yang dipakai SQL mentah + `tools.drop_view_if_exists` byte-identik 17↔18

## [Fase C1] View Sederhana (Mekanis)

- **Scope:** sama seperti Fase A2 — tree→list adalah SATU-SATUNYA perubahan view yang diperlukan modul ini
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2b View List Checklist
- **Aksi:** Sudah tuntas di Fase A2 (dikerjakan lebih awal karena juga blocker install, sesuai urutan Fase A yang diprioritaskan dari blocker paling kritis). Tidak ada aksi tambahan di sini.
- **Secara eksplisit TIDAK dilakukan:** Tidak ada perubahan menu/action lain di luar tree→list
- **Risiko:** LOW
- **Status:** ✅ Selesai (digabung ke A2)

## [Fase G2] Validasi Akhir

- **Scope:** Runtime smoke-check spesifik ke DIFF-01/DIFF-02/DIFF-12 (bukan full AC sweep — itu tugas step 9/10)
- **Aksi:**
  - `docker compose up db_target odoo_target` (image `odoo:18.0` resmi, mount `product_history_report/` target-codebase, `-i product_history_report --test-enable --test-tags=/product_history_report --stop-after-init`)
  - Run #1: install modul SUKSES (konfirmasi DIFF-01/DIFF-02 resolved — tidak ada `ParseError: Invalid view type`), tapi test error di `setUpClass` (DIFF-12 baru ditemukan, lihat "Riwayat Percobaan G1")
  - Fix DIFF-12 di `tests/test_product_history_report.py` (`'type': 'product'` → `'is_storable': True`)
  - Run #2: install bersih + **0 failed, 0 error(s) of 8 tests** — dikonfirmasi silang jumlah baris `Starting Test*` = 8 (bukan false-pass MSYS path-mangling, tidak relevan di sini karena tag dibaked ke `docker-compose.yml`, bukan argumen shell langsung, tapi tetap diverifikasi sebagai kebiasaan wajib)
- **Kriteria minimal G2 terpenuhi:**
  - Tidak ada warning server saat start (selain warning kosmetik `_description`/rule tanpa group yang sudah ada sebelum migrasi, bukan regresi baru)
  - Diff/fix breaking (DIFF-01, DIFF-02, DIFF-12) terkonfirmasi valid di runtime nyata
- **Risiko:** Tidak ada (setelah fix)
- **Status:** ✅ Selesai

---

## Temuan di Luar Spec

- [x] Ada — DIFF-12 (`product.template.type='product'` dihapus, ganti `is_storable`) ditemukan LEWAT eksekusi G1 nyata, BUKAN dari review statis step 2/3. Ditangani SESUAI prosedur ("STOP, jangan improvisasi, balik ke step 3/4 dulu") — `02_DIFF_ANALYSIS.md` dan `03_MIGRATION_SPEC.md` diupdate dengan entry DIFF-12 SEBELUM fix diterapkan, bukan fix dulu baru dokumentasi menyusul.

## Kontribusi ke Knowledge Base

- [x] Ada — dicatat ke `migration-tool/migration-records/product_history_report_17.0_18.0/SUMMARY.md`: **CAND-01** (`product.template.type` selection value `'product'` dihapus di 18.0, diganti field `is_storable` Boolean dari modul `stock` — kandidat kuat promosi ke `knowledge/version-diffs/17-to-18.md` §1, karena ini breaking change level PLATFORM yang berpotensi mengenai BANYAK modul custom yang membuat produk storable secara programatik/test, bukan spesifik ke `product_history_report`).
