# Implementation Log — product_history_report

**Step:** 6 — Code Migration
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `migration-tool/templates/06a_CODE_MIGRATION_PHASES.md`
**Tanggal:** 2026-08-26

---

## Applicability Check

Dari `01_intake/01a_MIGRATION_INTAKE.md` §2b — modul murni backend, tidak ada fitur di bawah ini:

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| C1 (View Sederhana) | ☑ Ya | Modul punya `views/stock_history_view.xml` + `views/views.xml` — sama seperti project 17→18, TIDAK N/A |
| B2 (Model Kompleks) | ☐ Tidak | Tidak ada field JSON/relasi berantai/dynamic model creation |
| C2 (Semantik XML) | ☐ Tidak | Tidak ada `attrs=`/`states=`/domain-context dinamis, hanya `domain="[]"` statis |
| D1 (Controllers) | ☐ Tidak | `controllers/controllers.py` boilerplate, tidak expose route |
| D2 (Assets & CSS) | ☐ Tidak | Tidak ada `static/src/`, hanya `static/tests/tours/` (test-only, bukan aplikatif) |
| E (JavaScript/Owl) | ☐ Tidak | Tidak ada komponen Owl aplikatif — 1 file JS adalah test tour, ditangani sebagai bagian verifikasi test (G1/Step 9), bukan Fase E |
| F (Upgrade Template) | ☐ Tidak | Otomatis N/A karena E N/A |

---

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 (Manifest Bootstrap) | ✅ | 2026-08-26 |
| A2 (XML Tree→List) | ✅ N/A — sudah final sejak migrasi 17→18, tidak ada `<tree>` tersisa | 2026-08-26 |
| A3 (Security Hardening) | ✅ N/A — ACL sudah lengkap, tidak ada perubahan (dikonfirmasi DIFF-11) | 2026-08-26 |
| A4 (Skeleton Integrity) | ✅ N/A — struktur folder sudah konsisten, tidak ada perubahan | 2026-08-26 |
| A5 (Python API Compat) | ✅ N/A — tidak override `create()`/`_name_search`/dst (dikonfirmasi DIFF-12) | 2026-08-26 |
| G1 #1 (setelah A1 + C1) | ❌ Fail — install SUKSES, tapi 1 failed + 4 error(s) of 9 tests | 2026-08-26 |
| C1 (View Sederhana — fix DIFF-01) | ✅ Selesai | 2026-08-26 |
| (fix DIFF-02, DIFF-15, DIFF-16 — test-only, di luar Fase A-G formal) | ✅ Selesai | 2026-08-26 |
| G1 #2 (setelah C1 + semua fix test) | ✅ Pass — 0 failed, 0 error(s) of 9 tests | 2026-08-26 |
| B1 (Model Risiko Rendah) | ✅ N/A — tidak ada perubahan model (dikonfirmasi DIFF-04, DIFF-05) | 2026-08-26 |
| B2 | N/A — dikonfirmasi Applicability Check | — |
| C2 | N/A — dikonfirmasi Applicability Check | — |
| D1 | N/A — dikonfirmasi Applicability Check | — |
| D2 | N/A — dikonfirmasi Applicability Check | — |
| E | N/A — dikonfirmasi Applicability Check | — |
| F | N/A — dikonfirmasi Applicability Check (otomatis, E juga N/A) | — |
| G2 (Validasi Akhir) | ✅ Pass — digabung dengan G1 #2 (server hidup, 9/9 test termasuk Tour test membuktikan runtime nyata, bukan cuma install) | 2026-08-26 |

## Riwayat Percobaan G1 (Install Test)

**Mode:** C — AI jalankan langsung (Claude Code CLI, Mode Git aktif, Docker tersedia di environment sesi — dikonfirmasi `docker --version` dan image `odoo:19.0` berhasil di-pull).

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A1 + C1 (fix DIFF-01, DIFF-02 sudah diterapkan sebelum run pertama) | C | ❌ Fail — install modul SUKSES ("Module product_history_report loaded in 0.81s, 142 queries", tidak ada `ParseError`/`ValidationError` — DIFF-01 & install-blocking lain terkonfirmasi resolved), TAPI **1 failed, 4 error(s) of 9 tests** | 4 error: `ValueError: Invalid field 'name' in 'stock.move'` (DIFF-15, ditemukan BARU di run ini) di `test_ac_02_01`/`test_ac_03_01`/`test_ac_03_02`/`test_ac_04_01`. 1 failed: Tour test timeout `Element (.o_button_more) has not been found` (DIFF-16, ditemukan BARU di run ini) | 2026-08-26 |
| 2 | Fix DIFF-15 (hapus key `name` di `_make_move()`) + DIFF-16 (ubah trigger tour) | C | ✅ Pass — **0 failed, 0 error(s) of 9 tests** (dikonfirmasi silang: 9 baris `Starting Test*` = 9 method test yang benar-benar dieksekusi; Tour test menyelesaikan 10/10 step, log `tour succeeded`) | — | 2026-08-26 |

---

## Entri

## [Fase A1] Manifest Bootstrap

- **Scope:** `product_history_report/__manifest__.py`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2b Critical Blocker #1, DIFF-14
- **Aksi:** `'version': '18.0.1.0.0'` → `'version': '19.0.1.0.0'`
- **Secara eksplisit TIDAK dilakukan:** Tidak menghapus/mengubah `depends`, `data`, atau field manifest lain apapun
- **Risiko:** LOW
- **Status:** ✅ Selesai

## [Fase C1] View Sederhana (Mekanis)

- **Scope:** `product_history_report/views/stock_history_view.xml`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` §2 baris 1, DIFF-01
- **Aksi:** Record `view_stock_history_search2`, baris 10: `<group expand="0" string="Group By">` → `<group>` (hapus dua atribut, isi `<filter>` di dalamnya tidak berubah)
- **Secara eksplisit TIDAK dilakukan:** Tidak menghapus/mengubah filter groupby apapun di dalam `<group>` — hanya atribut tag pembungkusnya
- **Risiko:** LOW
- **Status:** ✅ Selesai — dikonfirmasi G1 #1 & #2 (install bersih, tidak ada `ValidationError`); AC-01-03 (verifikasi manual filter groupby masih berfungsi) ditunda ke Step 10 sesuai `05b_TEST_PLAN_MIGRATION.md`

## [Fase A3] Security Hardening — N/A, dikonfirmasi DIFF-11: format CSV ACL tidak berubah 18→19, ACL yang ada (`access_stock_history_view`) sudah valid

## [Fase A4] Skeleton & Folder Integrity — N/A, dikonfirmasi Applicability Check tidak ada gap struktural

## [Fase A5] Python API Compatibility — N/A, dikonfirmasi `03_MIGRATION_SPEC.md` DIFF-12: modul tidak override API manapun yang berubah 18→19

## [Fase B1] Model Risiko Rendah — N/A, dikonfirmasi DIFF-04/DIFF-05: semua field SQL mentah + `tools.drop_view_if_exists` byte-identik 18↔19

## [Test Fix, di luar Fase A-G formal] `groups_id`→`group_ids`

- **Scope:** `product_history_report/tests/test_product_history_report.py:189`
- **Item spec (ref):** `03_MIGRATION_SPEC.md` DIFF-02
- **Aksi:** `'groups_id': [(6, 0, [...])]` → `'group_ids': [(6, 0, [...])]` di `create()` `res.users` (test `test_ac_05_01_...`)
- **Risiko:** LOW
- **Status:** ✅ Selesai — dikonfirmasi G1 #2 (`test_ac_05_01_read_open_for_user_without_inventory_group` PASS)

## [Test Fix, ditemukan G1, di luar Fase A-G formal] `stock.move.name` dihapus (DIFF-15)

- **Scope:** `product_history_report/tests/test_product_history_report.py:64-65` (`_make_move()`)
- **Item spec (ref):** `02_DIFF_ANALYSIS.md` DIFF-15 (BARU, ditemukan G1 run #1 — **STOP-dan-dokumentasikan-dulu dijalankan**: `02_DIFF_ANALYSIS.md` dan `03_MIGRATION_SPEC.md` diupdate dengan entry DIFF-15 SEBELUM fix diterapkan, konsisten prosedur `DIFF-12` project 17→18)
- **Aksi:** Hapus key `'name': 'BACKFILL test move',` dari `self.env['stock.move'].create({...})` — tidak ada pengganti, field ini dihapus total di 19.0 (diganti compute `reference`, tidak settable via `create()`), dan modul produksi tidak pernah membaca/menulis field ini
- **Secara eksplisit TIDAK dilakukan:** Tidak menambahkan field `reference`/pengganti apapun — tidak ada kebutuhan fungsional untuk deskripsi move di test ini
- **Risiko:** LOW (mekanis, satu baris) — tapi WAJIB (test-blocking untuk 4 test)
- **Status:** ✅ Selesai — dikonfirmasi G1 #2 (4 test yang sebelumnya error sekarang PASS)

## [Test Fix, ditemukan G1, di luar Fase A-G formal] Tour trigger `.o_button_more` tidak render (DIFF-16)

- **Scope:** `product_history_report/static/tests/tours/stock_history_tour.js` (step 9-10 lama)
- **Item spec (ref):** `02_DIFF_ANALYSIS.md` DIFF-16 (BARU, ditemukan G1 run #1 — didokumentasikan dulu sebelum fix, sama seperti DIFF-15)
- **Aksi:** Hapus step `{trigger: ".o_button_more", ...}`, ubah trigger step "Click the Stock History stat button" dari `.o_dropdown_more button:contains("Stock History")` jadi `button:contains("Stock History")` (klik langsung, tanpa lewat overflow menu)
- **Secara eksplisit TIDAK dilakukan:** Tidak mengubah button `views/views.xml` (`class="oe_stat_button"`) atau perilaku produksinya sama sekali — ini murni penyesuaian test terhadap perubahan threshold overflow `ButtonBox` native 19.0 (bukan sesuatu yang modul ini kontrol)
- **Risiko:** LOW (mekanis) — tapi WAJIB (Tour test gagal tanpa ini)
- **Status:** ✅ Selesai — dikonfirmasi G1 #2 (Tour 10/10 step, `tour succeeded`)

## [Fase G2] Validasi Akhir

- **Scope:** Runtime smoke-check spesifik ke DIFF-01/DIFF-02/DIFF-15/DIFF-16/DIFF-10 (bukan full AC sweep — itu tugas step 9/10, meski secara praktis G1 run #2 ini SUDAH menjalankan seluruh 9 test)
- **Aksi:** `docker compose up --build` (image `odoo:19.0` resmi + google-chrome-stable untuk Tour, mount `product_history_report/` target-codebase, `-i product_history_report --test-enable --test-tags=/product_history_report --stop-after-init`), 2 run (lihat "Riwayat Percobaan G1")
- **Kriteria minimal G2 terpenuhi:**
  - Tidak ada warning server yang baru/tidak dikenal saat start (hanya warning kosmetik `_description`/rule tanpa group yang sudah ada sebelum migrasi)
  - Semua diff/fix breaking (DIFF-01, DIFF-02, DIFF-15, DIFF-16) terkonfirmasi valid di runtime nyata; DIFF-10 terkonfirmasi TIDAK bermasalah
- **Risiko:** Tidak ada (setelah fix)
- **Status:** ✅ Selesai

---

## Temuan di Luar Spec

- [x] Ada — **DUA** temuan baru lewat eksekusi G1 run #1 nyata, BUKAN dari review statis step 2/3:
  1. **DIFF-15** (`stock.move.name` dihapus, diganti compute `reference`) — mirip pola `DIFF-12` project 17→18 (`product.template.type`), ditangani SESUAI prosedur ("STOP, dokumentasikan ke `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md` dulu, baru fix").
  2. **DIFF-16** (tombol "Stock History" tidak lagi collapse ke `.o_button_more` overflow menu di 19.0) — temuan UI/tour-only, ditangani prosedur yang sama.

## Kontribusi ke Knowledge Base

- [x] Ada — dicatat ke `migration-tool/migration-records/product_history_report_18.0_19.0/SUMMARY.md`:
  - **DIFF-01** (`<group expand=/string=>` dihapus dari skema RNG) — kandidat kuat promosi `knowledge/version-diffs/18-to-19.md` §1 (breaking change level PLATFORM, pola `<group>` search view SANGAT umum di modul custom).
  - **DIFF-15** (`stock.move.name` dihapus, diganti `reference` compute) — kandidat promosi `knowledge/dependency-compat/stock/18-to-19.md` (data point PERTAMA untuk `stock` 18→19).
  - **DIFF-16** (button box overflow threshold berubah di 19.0) — kandidat catatan `knowledge/version-diffs/18-to-19.md` (kemungkinan level `web`, bukan spesifik `stock` — relevan untuk SEMUA Tour test modul manapun yang mengasumsikan stat button collapse ke `.o_button_more`).
  - **DIFF-10 resolved** (xmlid `stock.picking_type_*` aman) — data point konfirmasi tambahan untuk `knowledge/dependency-compat/stock/18-to-19.md`.
