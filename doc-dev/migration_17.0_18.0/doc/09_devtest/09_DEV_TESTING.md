# Dev Testing — product_history_report

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-08-24

---

**Eksekusi:** `docker compose up db_target odoo_target` (`docker-env/docker-compose.yml`, image `odoo:18.0` resmi, tag baked ke file compose — bukan argumen shell langsung, sehingga tidak berisiko MSYS path-mangling). Command di dalam container: `odoo -d product_history_report_target -i product_history_report --addons-path=...,/mnt/extra-addons --test-enable --test-tags=/product_history_report --stop-after-init`.

Modul tidak punya Owl/JS (`01a_MIGRATION_INTAKE.md` §2b, Fase E N/A) — tidak ada Tour test, tabel di bawah cuma Integration.

## 9a. Audit Kesiapan Test

**Registrasi:** `tests/__init__.py` meng-import `test_product_history_report` — 1 file, ter-load penuh, tidak ada file test yang terlewat.

**Isi tiap method (dibaca langsung, bukan cuma nama):**

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 | Tombol Stock History ada di arch | `test_ac_01_01_button_present_in_form_arch` | ✅ Lengkap | `assertIn` ke `get_view()['arch']` |
| AC-01-02 | Action window benar | `test_ac_01_02_action_open_stock_history_returns_expected_action` | ✅ Lengkap | 3 assertion (`res_model`, `view_mode`, `domain`) |
| AC-02-01 | qty running-sum >13 bulan | `test_ac_02_01_qty_includes_pre_window_balance` | ✅ Lengkap | Setup data nyata (`stock.move` via `button_validate()`), `assertAlmostEqual` |
| AC-02-02 | Race condition (tidak ditest) | — | ❌ Tidak ada (by design) | Sifat non-deterministik, tidak reliable diuji unit test — konsisten `05b_TEST_PLAN_MIGRATION.md` |
| AC-03-01 | Customer→internal = income saja | `test_ac_03_01_customer_return_is_income_only` | ✅ Lengkap | `assertGreaterEqual`/`assertEqual` |
| AC-03-02 | Double-count internal→internal | `test_ac_03_02_internal_transfer_counted_as_both_income_and_outcome` | ✅ Lengkap | Verifikasi eksplisit bug MF-02 tetap terjadi |
| AC-04-01 | Filter multi-company | `test_ac_04_01_company_filter_excludes_other_company` | ✅ Lengkap | Kontrol + kandidat company palsu |
| AC-05-01 | ACL terbuka tanpa grup | `test_ac_05_01_read_open_for_user_without_inventory_group` | ✅ Lengkap | User baru tanpa grup, `with_user()` |
| AC-05-02 | create/write/unlink gagal di DB | `test_ac_05_02_create_on_view_fails` | ✅ Lengkap | `assertRaises(Exception)` |

**Verdict audit:** Semua 8 method Lengkap (bukan stub) — dikonfirmasi baca isi tiap method langsung, konsisten dengan hasil G1 #2 (semua 8 benar-benar tereksekusi, bukan silently skip). Lanjut eksekusi.

## Baseline

- Characterization test asli source module: sama persis 8 method di atas, sudah PASS di `source-codebase` (17.0) — hasil kerja `doc-dev-backfill` Step 04, dicatat di `doc-dev/backfill/test/04A_DEV_TESTING.md` ("8/8 Integration test PASS nyata, Odoo 17.0").
- Applicability Check Fase E (Owl/JS): Tidak, N/A — tidak ada Tour test yang wajib.

## Hasil Unit, Integration & Tour Test (target-codebase, Odoo 18.0)

> Dieksekusi bersamaan dengan Fase G2 step 6 (`06c_IMPLEMENTATION_LOG.md`) — dua run, run #1 menemukan DIFF-12 (test-blocking, ditangani lewat step 3/4 sebelum fix), run #2 setelah fix.

| AC | Unit | Integration | Tour (Owl/JS) | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01 | — | `test_ac_01_01_button_present_in_form_arch` | N/A | ✅ Pass | — |
| AC-01-02 | — | `test_ac_01_02_action_open_stock_history_returns_expected_action` | N/A | ✅ Pass | Assertion `view_mode` sudah diupdate `graph,pivot,list` |
| AC-02-01 | — | `test_ac_02_01_qty_includes_pre_window_balance` | N/A | ✅ Pass | — |
| AC-02-02 | — | (tidak ditest, by design) | N/A | — | Konsisten baseline 17.0 |
| AC-03-01 | — | `test_ac_03_01_customer_return_is_income_only` | N/A | ✅ Pass | — |
| AC-03-02 | — | `test_ac_03_02_internal_transfer_counted_as_both_income_and_outcome` | N/A | ✅ Pass | Bug MF-02 dikonfirmasi tetap terjadi identik |
| AC-04-01 | — | `test_ac_04_01_company_filter_excludes_other_company` | N/A | ✅ Pass | — |
| AC-05-01 | — | `test_ac_05_01_read_open_for_user_without_inventory_group` | N/A | ✅ Pass | ACL longgar (MF-03) dikonfirmasi tetap terjadi |
| AC-05-02 | — | `test_ac_05_02_create_on_view_fails` | N/A | ✅ Pass | — |

**Hasil eksekusi run #2 (final):** `0 failed, 0 error(s) of 8 tests` — dikonfirmasi silang jumlah baris log `Starting TestProductHistoryReport.*` = 8 (exact match jumlah method, bukan false-pass tag-filter kosong).

## Addendum — Tour Test Ditambahkan (2026-08-24, setelah gate awal)

**Revisi §"Applicability Check Fase E" di atas:** tidak ada Owl/JS CUSTOM di modul ini (tetap benar), TAPI Tour test (`HttpCase.start_tour`) tidak memerlukan Owl/JS custom — Tour bisa menguji alur klik UI standar apapun. Ditambahkan SETELAH gate Step 9/10 awal karena AI-interaktif (browser automation eksternal, lihat `10_qa/10_BUSINESS_FLOW_MIGRATION.md`) gagal total akibat limitasi environment — Tour test (headless Chrome yang dikelola Odoo SENDIRI via `HttpCase`, bukan automation eksternal) dipakai sebagai gantinya untuk memverifikasi S-01 (Smoke, `10_qa/10_BUSINESS_FLOW_MIGRATION.md`) secara genuinely otomatis, bukan cuma baca arch XML statis (`test_ac_01_01`).

**File baru:** `static/tests/tours/stock_history_tour.js` + `tests/test_stock_history_tour.py`. Manifest ditambah key `assets.web.assets_tests` (wajib untuk registrasi Tour, TIDAK ada di 17.0 karena modul belum punya Tour — ini penambahan test infrastructure, bukan perubahan business logic, sesuai `03_MIGRATION_SPEC.md` §4 "boleh: menambah test baru").

**Alur yang diuji (real click, real browser, dikelola Odoo sendiri):** buka apps menu → Inventory → Products menu → search produk fixture → klik kartu kanban produk → klik dropdown "More" (tombol Stock History collapse ke sana karena button box penuh — dikonfirmasi perilaku IDENTIK di `native-source`/17.0, bukan regresi migrasi) → klik "Stock History" → assert breadcrumb berganti jadi "Stocks Histories" (window action `target: 'current'` benar-benar terbuka, bukan cuma dict Python yang benar).

**2 percobaan gagal sebelum lulus** (dicatat sebagai lesson, bukan disembunyikan):
1. Percobaan 1: trigger `.o_data_cell:contains(...)` — GAGAL, default Products view adalah **Kanban**, bukan list, jadi `.o_data_cell` tidak pernah match. Fix: pakai search bar (`.o_searchview_input`, `run: "edit ..."` + `"press Enter"`) lalu `.o_kanban_record:contains(...)`.
2. Percobaan 2: trigger `button:contains("Stock History")` langsung — GAGAL, tombol collapse ke dropdown **"More"** (`.o_button_more`) karena button box produk ini sudah penuh (On Hand/Forecasted/Documents/Reordering Rules). Fix: klik `.o_button_more` dulu, baru `.o_dropdown_more button:contains("Stock History")`.

**Hasil final:** `0 failed, 0 error(s) of 9 tests` (8 test lama + 1 Tour baru), Tour selesai 11/11 langkah PASS.

## Kontribusi ke Knowledge Base

- [x] Ada — DIFF-12 (`product.template.type='product'` dihapus 18.0, ganti `is_storable`) ditemukan lewat kegagalan test run #1 di step ini (Fase G2, digabung dengan step 6) — sudah dicatat `migration-tool/migration-records/product_history_report_17.0_18.0/SUMMARY.md` CAND-01.

## Verdict

- [x] ✅ **Semua AC prioritas Unit/Integration pass** — lanjut ke step 10
