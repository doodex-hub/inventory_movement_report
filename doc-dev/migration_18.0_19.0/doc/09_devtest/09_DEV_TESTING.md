# Dev Testing — product_history_report

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-08-26

---

**Eksekusi:** `docker compose up --build` (`docker-env/docker-compose.yml`, image `odoo:19.0` resmi + `google-chrome-stable` untuk Tour, tag baked ke file compose — bukan argumen shell langsung, sehingga tidak berisiko MSYS path-mangling). Command di dalam container: `odoo -d product_history_report_target -i product_history_report --addons-path=...,/mnt/extra-addons --test-enable --test-tags=/product_history_report --stop-after-init`.

Modul punya 1 Tour test (`static/tests/tours/stock_history_tour.js` + `tests/test_stock_history_tour.py`, ditambahkan sebagai addendum Step 9 project 17→18) — tabel di bawah mencakup Integration DAN Tour.

## 9a. Audit Kesiapan Test

**Registrasi:** `tests/__init__.py` meng-import `test_product_history_report` dan `test_stock_history_tour` — 2 file, ter-load penuh, tidak ada file test yang terlewat.

**Isi tiap method (dibaca langsung, bukan cuma nama — `python3` tidak tersedia di environment sesi ini untuk script `ast` otomatis, jadi audit dilakukan dengan membaca isi file langsung, sudah dilakukan saat Step 2 investigasi + dikonfirmasi ulang di sini):**

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 | Tombol Stock History ada di arch | `test_ac_01_01_button_present_in_form_arch` | ✅ Lengkap | `assertIn` ke `get_view()['arch']` |
| AC-01-02 | Action window benar | `test_ac_01_02_action_open_stock_history_returns_expected_action` | ✅ Lengkap | 3 assertion (`res_model`, `view_mode`, `domain`) |
| AC-01-03 | Groupby search panel (DIFF-01) | `test_stock_history_tour` (2 step baru ditambahkan Step 10, lihat addendum) | ✅ Lengkap | Awalnya didorong ke Step 10 Manual di `05b_TEST_PLAN_MIGRATION.md`, TERNYATA bisa ditutup otomatis via extended Tour — lihat "Addendum" di bawah |
| AC-02-01 | qty running-sum >13 bulan | `test_ac_02_01_qty_includes_pre_window_balance` | ✅ Lengkap | Setup data nyata (`stock.move` via `button_validate()`), `assertAlmostEqual` |
| AC-02-02 | Race condition (tidak ditest) | — | ❌ Tidak ada (by design) | Sifat non-deterministik, tidak reliable diuji unit test — konsisten `05b_TEST_PLAN_MIGRATION.md` |
| AC-03-01 | Customer→internal = income saja | `test_ac_03_01_customer_return_is_income_only` | ✅ Lengkap | `assertGreaterEqual`/`assertEqual` |
| AC-03-02 | Double-count internal→internal | `test_ac_03_02_internal_transfer_counted_as_both_income_and_outcome` | ✅ Lengkap | Verifikasi eksplisit bug MF-02 tetap terjadi |
| AC-04-01 | Filter multi-company | `test_ac_04_01_company_filter_excludes_other_company` | ✅ Lengkap | Kontrol + kandidat company palsu |
| AC-05-01 | ACL terbuka tanpa grup | `test_ac_05_01_read_open_for_user_without_inventory_group` | ✅ Lengkap | User baru tanpa grup, `with_user()` |
| AC-05-02 | create/write/unlink gagal di DB | `test_ac_05_02_create_on_view_fails` | ✅ Lengkap | `assertRaises(Exception)` |
| (Tour) | Klik nyata tombol Stock History end-to-end | `test_stock_history_tour` | ✅ Lengkap | `HttpCase.start_tour`, 10 step, headless Chrome dikelola Odoo sendiri |

**Verdict audit:** Semua 8 method Integration + 1 Tour Lengkap (bukan stub) — dikonfirmasi baca isi tiap method langsung, konsisten dengan hasil eksekusi (semua 9 benar-benar tereksekusi, bukan silently skip — lihat jumlah baris `Starting Test*` = 9 di log). Lanjut eksekusi.

## Baseline

- Characterization test asli source module: sama persis 8 method Integration + 1 Tour di atas, sudah PASS di `source-codebase` (18.0) — hasil kerja migrasi 17→18 (`doc-dev/migration_17.0_18.0/doc/09_devtest/09_DEV_TESTING.md`, "0 failed, 0 error(s) of 9 tests", Tour 11/11 step).
- Applicability Check Fase E (Owl/JS) dari Step 6: Tidak (N/A untuk kode aplikatif) — tapi Tour test tetap applicable (tidak butuh Owl/JS custom, cuma klik UI standar), diwarisi dari project 17→18.

## Hasil Unit, Integration & Tour Test (target-codebase, Odoo 19.0)

> Dieksekusi bersamaan dengan Fase G2 Step 6 (`06_implementation/06c_IMPLEMENTATION_LOG.md`) — 2 run. Run #1 menemukan DIFF-15 (test-blocking, 4 test) + DIFF-16 (Tour timeout), ditangani lewat Step 2/3 (dokumentasi dulu) sebelum fix. Run #2 setelah fix.

| AC | Unit | Integration | Tour (Owl/JS) | Pass/Fail | Catatan |
|---|---|---|---|---|---|
| AC-01-01 | — | `test_ac_01_01_button_present_in_form_arch` | Tercakup juga lewat Tour | ✅ Pass | — |
| AC-01-02 | — | `test_ac_01_02_action_open_stock_history_returns_expected_action` | Tercakup juga lewat Tour | ✅ Pass | Tidak butuh update assertion (token `view_mode` sudah final sejak 18.0) |
| AC-01-03 | — | — | `test_stock_history_tour` (extended) | ✅ Pass | Lihat "Addendum — AC-01-03 Ditutup via Extended Tour" di bawah |
| AC-02-01 | — | `test_ac_02_01_qty_includes_pre_window_balance` | N/A | ✅ Pass | Run #1 ERROR (DIFF-15) → run #2 Pass setelah fix `_make_move()` |
| AC-02-02 | — | (tidak ditest, by design) | N/A | — | Konsisten baseline 18.0 |
| AC-03-01 | — | `test_ac_03_01_customer_return_is_income_only` | N/A | ✅ Pass | Run #1 ERROR (DIFF-15) → run #2 Pass |
| AC-03-02 | — | `test_ac_03_02_internal_transfer_counted_as_both_income_and_outcome` | N/A | ✅ Pass | Run #1 ERROR (DIFF-15) → run #2 Pass — bug MF-02 dikonfirmasi tetap terjadi identik |
| AC-04-01 | — | `test_ac_04_01_company_filter_excludes_other_company` | N/A | ✅ Pass | Run #1 ERROR (DIFF-15) → run #2 Pass |
| AC-05-01 | — | `test_ac_05_01_read_open_for_user_without_inventory_group` | N/A | ✅ Pass | ACL longgar (MF-03) dikonfirmasi tetap terjadi — juga membuktikan fix DIFF-02 (`group_ids`) benar |
| AC-05-02 | — | `test_ac_05_02_create_on_view_fails` | N/A | ✅ Pass | Tidak terpengaruh DIFF-15 (tidak pakai `_make_move()`) — Pass di run #1 & #2 |
| (Tour) | — | — | `test_stock_history_tour` | ✅ Pass | Run #1 FAILED (DIFF-16, timeout `.o_button_more`) → run #2 Pass, 10/10 step, log `tour succeeded` |

**Hasil eksekusi run #1:** `1 failed, 4 error(s) of 9 tests` — 4 error dari DIFF-15 (`ValueError: Invalid field 'name' in 'stock.move'`), 1 failed dari DIFF-16 (Tour timeout `.o_button_more` tidak ditemukan). DIFF-10 (open question Step 2) terkonfirmasi TIDAK bermasalah — 4 `env.ref()` picking type/lokasi semua resolve normal, error terjadi SETELAH itu di `stock.move.create()`.

**Hasil eksekusi run #2 (setelah fix DIFF-15 & DIFF-16):** `0 failed, 0 error(s) of 9 tests` — dikonfirmasi silang jumlah baris log `Starting Test*` = 9 (exact match jumlah method: 8 Integration + 1 Tour), Tour menyelesaikan 10/10 step (satu step lebih sedikit dari project 17→18 yang 11 step — karena step "buka .o_button_more" dihapus, tombol diklik langsung).

## Addendum — AC-01-03 Ditutup via Extended Tour (2026-08-26, setelah gate awal, saat Step 10 dimulai)

**Revisi `05b_TEST_PLAN_MIGRATION.md`:** AC-01-03 awalnya didorong ke Step 10 Manual karena dianggap tidak ada jalur otomatis untuk verifikasi UI search panel groupby. Ternyata SALAH — sama seperti pola project 17→18 (Tour test ditemukan sebagai jalur otomatis pengganti AI-interaktif yang gagal), Tour yang SUDAH ADA (`stock_history_tour`) bisa diperpanjang 2 step tanpa infrastruktur baru: buka dropdown search options (`.o_searchview_dropdown_toggler`) → assert filter "By products" (`.o_group_by_menu .o_menu_item:contains("By products")`) masih ada & clickable. Ini "menambah test baru" (diizinkan `03_MIGRATION_SPEC.md` §4), BUKAN mengubah business logic.

**Investigasi teknis yang mendasari:** dibaca langsung source `addons/web/static/src/search/search_bar_menu/search_bar_menu.xml` di `enterprise19.0` — heading "Group By" yang tampil ke user di dropdown TERNYATA di-render oleh komponen JS generik `SearchBarMenu` (`<h5 class="o_dropdown_title">Group By</h5>`, hardcoded di template, BUKAN dari atribut `string=` tag `<group>` arch modul). Ini berarti atribut `string="Group By"`/`expand="0"` yang dihapus dari `<group>` (DIFF-01) kemungkinan besar SUDAH TIDAK punya efek visual apapun di UI modern sejak beberapa versi — cuma legacy attribute yang baru sekarang ditolak skema RNG. Extended Tour ini mengonfirmasi SECARA EMPIRIS (bukan cuma dugaan dari baca source) bahwa filter groupby tetap tampil & berfungsi normal.

**Hasil eksekusi run #3 (final):** `0 failed, 0 error(s) of 9 tests`, Tour menyelesaikan **12/12 step** (10 step lama + 2 step baru), step terakhir `[12/12] ... The 'By products' Group By filter is still present and clickable` sukses, log `tour succeeded`.

## Kontribusi ke Knowledge Base

- [x] Ada — dua temuan lewat kegagalan test run #1 di step ini (Fase G2, digabung dengan Step 6) — sudah dicatat `migration-tool/migration-records/product_history_report_18.0_19.0/SUMMARY.md`:
  - **DIFF-15** (`stock.move.name` dihapus 19.0, ganti compute `reference`)
  - **DIFF-16** (button box `ButtonBox` threshold overflow `.o_button_more` berubah di 19.0)
  - Juga konfirmasi **DIFF-10 resolved** (xmlid `stock.picking_type_*`/`stock.stock_location_stock` tetap aman).
  - Tambahan dari Addendum: **DIFF-01 klarifikasi** — heading "Group By" di UI adalah hardcoded di komponen JS generik `SearchBarMenu`, TIDAK berasal dari atribut `string=` tag `<group>` arch — kemungkinan atribut itu sudah vestigial (tanpa efek visual) sejak beberapa versi sebelum dihapus total dari skema di 19.0.

## Verdict

- [x] ✅ **Semua AC pass, termasuk AC-01-03** (ditutup via extended Tour, addendum di atas) — lanjut ke step 10 tanpa item manual yang tertunda
