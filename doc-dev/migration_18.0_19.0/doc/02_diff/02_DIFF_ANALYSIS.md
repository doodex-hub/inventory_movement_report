# Diff & Compatibility Analysis — product_history_report

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `migration-tool/knowledge/version-diffs/18-to-19.md`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/18-to-19.md` | Ya | §1 (riset OCA wiki, sebagian diverifikasi langsung) + §1a (temuan project nyata `advanced_sales_analysis`, rename `sale.order.line.tax_id`) — tidak ada satupun poin yang langsung relevan ke `base`/`stock` API yang dipakai modul ini, dicek manual satu-satu di §1 bawah |
| `dependency-compat/stock/...` | Tidak | Belum ada entry `stock` untuk pasangan versi manapun (17→18 juga belum, cuma dicatat sebagai kandidat di `migration-records/product_history_report_17.0_18.0/SUMMARY.md`) — temuan Step 2 ini jadi data point PERTAMA untuk `stock` 18→19, dicatat ke `migration-records/product_history_report_18.0_19.0/SUMMARY.md` |

## 0b. Gate Community vs Enterprise

- [x] Dicek ulang `01a_MIGRATION_INTAKE.md` §2 — TIDAK ADA baris "Native Enterprise". Dependency cuma `base`+`stock`, keduanya Community.
- [x] Lanjut §1 di bawah cukup dengan `native-target` (`enterprise19.0` — folder gabungan Community+Enterprise, tapi semua simbol yang dicek modul ini murni Community: `base`/`stock`) vs `native-source` (`odoo18`).

## 0c. Gate Transitive Dependency

- [x] Tidak ada dependency yang akan dihapus dari `depends` (`base`+`stock` tetap dipakai, keduanya masih ada utuh di 19.0) — gate ini N/A, dicatat eksplisit supaya jelas bukan terlewat.

---

## 1. Perubahan Native (Core/Enterprise)

Simbol yang dipakai/di-inherit modul ini, dicek langsung terhadap `native-target` (`enterprise19.0`) vs `native-source` (`odoo18`).

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `views/stock_history_view.xml:10` `<group expand="0" string="Group By">` (search view `view_stock_history_search2`) | Skema RNG tag `<group>` di search/form view (`addons/base/rng/common.rng`) | **Atribut dihapus (install-blocking)** | Atribut `expand`/`string` **dihapus total** dari skema `<group>` di 19.0 — `schema_valid()` (`odoo/tools/view_validation.py`) akan gagal validasi RNG, `ir.ui.view._check_xml()` men-raise `ValidationError('Invalid view %(name)s definition...')`. **Modul gagal install total** kalau tidak diubah. | Dikonfirmasi langsung bandingkan `odoo18/odoo/addons/base/rng/common.rng:294-313` (masih ada `<rng:attribute name="expand"/>` + `<rng:attribute name="string"/>` di definisi `group`) vs `enterprise19.0/odoo/addons/base/rng/common.rng:295-312` (KEDUA atribut itu tidak ada lagi di definisi yang sama) — juga dikonfirmasi jalur `raise ValidationError` di `ir_ui_view.py:507-513` (`check = valid_view(...)`, `if not check: raise ValidationError(...)`) |
| DIFF-02 | `tests/test_product_history_report.py:189` `'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]` (create `res.users` di test `test_ac_05_01_...`) | Field `res.users.groups_id` | **Rename (test-blocking)** | `res.users.groups_id` **di-rename total** jadi `group_ids` di 19.0 (`addons/base/models/res_users.py:257`). Field `groups_id` tidak ada lagi — `create()` akan gagal (`ValueError: Invalid field 'groups_id'` atau serupa) begitu test ini jalan. Ini konsisten dengan §1 `knowledge/version-diffs/18-to-19.md` ("Access rights (views/menus/actions): `groups_id` diganti `group_ids`") — riset di muka TERKONFIRMASI relevan untuk modul ini, bukan cuma teori. | Dikonfirmasi langsung grep `enterprise19.0/odoo/addons/base/models/res_users.py:257` (`group_ids = fields.Many2many(...)`) — `groups_id` tidak ditemukan sebagai field definition di file yang sama (hanya referensi lama di komentar/`_fields_pre_display` list) |
| DIFF-03 | `models/stock_history_view.py:24,26` `tools.drop_view_if_exists(self._cr, ...)` + `self._cr.execute(query)` | Property `self._cr` (alias `self.env.cr`) | **Deprecated, TETAP jalan (bukan blocking)** | `_cr` sekarang ditandai `@api.deprecated("Deprecated since 19.0, use self.env.cr directly")` (`odoo/orm/models.py:5913`) — property masih ADA dan berfungsi (return `self.env.cr`), cuma memicu warning deprecation di log, TIDAK install/runtime-blocking. Sama pola dengan `toggle_active`/`_cr`/`_uid`/`_context` lain di `knowledge/version-diffs/18-to-19.md` §1. | Dikonfirmasi langsung `enterprise19.0/odoo/orm/models.py:5911-5918` — property `_cr` ADA, isinya `return self.env.cr` |
| DIFF-04 | `models/stock_history_view.py` SQL mentah — `stock_move.date/company_id/location_id/location_dest_id/state`; `stock_move_line.move_id/company_id/product_id/quantity/date`; `stock_location.usage`; `product_product.product_tmpl_id`; `product_template.uom_id/categ_id/active` | Field-field core `stock`/`product` di atas | **Tidak berubah** | Aman — semua kolom fisik yang dipakai query SQL mentah tetap ada dengan nama sama | Dikonfirmasi langsung `enterprise19.0/odoo/addons/stock/models/stock_move.py:28,35,75,81,107` (`date`/`company_id`/`location_id`/`location_dest_id`/`state`), `stock_move_line.py:26,29,30,37,60` (`move_id`/`company_id`/`product_id`/`quantity`/`date`), `stock_location.py:32` (`usage`), `addons/product/models/product_template.py:81,118,129` (`categ_id`/`uom_id`/`active`) — identik posisi/nama dengan `odoo18` |
| DIFF-05 | `models/stock_history_view.py:1,25` `from odoo import ... tools` + `tools.drop_view_if_exists(...)` | `odoo.tools.sql.drop_view_if_exists(cr, viewname)` | **Tidak berubah** | Aman — signature identik `(cr, viewname)` | `enterprise19.0/odoo/tools/sql.py:632` — signature sama persis dengan `odoo18` |
| DIFF-06 | `models/product_template.py:17` `self.env.companies.ids` | API multi-company `env.companies` | **Tidak berubah** | Aman | Tidak ada entry breaking untuk `env.companies` di `knowledge/version-diffs/18-to-19.md` §1/§1a; API stabil sejak versi jauh lebih lama |
| DIFF-07 | `models/product_template.py:5-31` `is_storable` (dipakai test fixture, `tests/test_*.py`) | Field `product.template.is_storable` | **Tidak berubah** | Aman — sudah field final sejak fix migrasi 17→18 (`is_storable` menggantikan `type='product'`), masih ada persis di 19.0 | `enterprise19.0/odoo/addons/stock/models/product.py:821` (`is_storable = fields.Boolean(...)`) |
| DIFF-08 | `views/views.xml:7` `inherit_id="stock.product_template_form_view_procurement_button"` + xpath implisit `<button name="action_view_stock_move_lines" position="after">` | XML-ID `product_template_form_view_procurement_button` + button `action_view_stock_move_lines` | **Tidak berubah** | Aman — inherit target dan xpath implisit tetap match | `enterprise19.0/odoo/addons/stock/views/product_views.xml:429` (XML-ID ada), `:499` (button `action_view_stock_move_lines` ada di dalam record yang sama, atribut `name` tidak berubah) |
| DIFF-09 | `views/stock_history_view.xml` — `<list>` (bukan `<tree>`, sudah fix migrasi 17→18), `<pivot>`/`<graph>` dengan `<field type="col"/"measure">`, `<filter domain="[]" context="{'group_by':...}">` | Skema RNG `list_view.rng`/`pivot_view.rng`/`graph_view.rng`/`common.rng` (`field`, `filter`) | **Tidak berubah** (kecuali DIFF-01 di atas) | Aman — `<list>` sudah bentuk final sejak 17→18, `type=` di `<field>` tidak dibatasi enum di skema, `<filter string=/domain=/context=>` masih didukung penuh | Dikonfirmasi langsung `enterprise19.0/odoo/addons/base/rng/{pivot,graph}_view.rng` (tidak ada perubahan struktur yang relevan) dan `common.rng:360-375` (`filter` masih punya `string`/`domain`/`context`) |
| DIFF-10 | `tests/test_product_history_report.py` — `self.env.ref('stock.stock_location_stock')`, `'stock.picking_type_in'`, `'stock.picking_type_out'`, `'stock.picking_type_internal'` | XML-ID picking type/lokasi yang dibuat cascade dari `<record id="warehouse0" model="stock.warehouse">` (`stock_data.xml`, BUKAN demo) | **Kemungkinan tidak berubah, TAPI perlu verifikasi eksekusi nyata (G1)** | `<record id="warehouse0">` masih ADA persis (`stock_data.xml`, non-demo, selalu load) di 19.0 — mekanisme yang membuat sub-xmlid `stock.picking_type_in`/`stock.stock_location_stock` dari record ini tidak berubah secara statis (tidak ada hardcode Python yang beda ditemukan di kedua versi). **Sinyal yang mencurigakan:** Odoo's OWN test suite (`enterprise19.0/odoo/addons/stock/tests/common.py`, class `TestStockCommon`) di 19.0 SUDAH TIDAK memakai `env.ref('stock.picking_type_in'/...)` sama sekali lagi — diganti bikin warehouse+picking type sendiri per test class. Tidak jelas apakah ini murni refactor test-hygiene (menghindari shared global fixture) atau ada perubahan lain yang belum terlihat dari review statis. **Ini bukan klaim final** — mirip pola `DIFF-12` di project 17→18 (`product.template.type`) yang baru ketahuan lewat eksekusi G1 nyata, bukan review kode statis. | `enterprise19.0/odoo/addons/stock/data/stock_data.xml:55` (`<record id="warehouse0">` ada, identik posisi dengan `odoo18/addons/stock/data/stock_data.xml:75`), `enterprise19.0/odoo/addons/stock/tests/common.py:9-38` (rewrite `TestStockCommon`, tidak ada `env.ref('stock.picking_type_*')` sama sekali) |
| DIFF-11 | `security/ir.model.access.csv` | Format CSV ACL | **Tidak berubah** | Aman | Format `ir.model.access.csv` tidak berubah 18→19 |
| DIFF-12 | Modul tidak override `create()`/`_sql_constraints`/`read_group()`/`name_search`/`toggle_active`/`odoo.osv.expression`/`auto_join`/`@api.returns`/`SUPERUSER_ID` import/`@ormcache_context` | Berbagai breaking change API di `knowledge/version-diffs/18-to-19.md` §1 | **N/A** | Tidak berdampak — grep langsung `source-codebase/product_history_report/**/*.py` tidak ada match untuk simbol manapun di daftar breaking change umum 18→19 | Grep langsung — 0 match untuk semua simbol tersebut di seluruh kode modul |
| DIFF-13 | `controllers/controllers.py` (boilerplate, semua di-comment); `models/*.py` `from odoo.http import request` (tidak dipakai) | N/A | **Tidak berubah** | Dead code/import, sama seperti temuan `01b_BASELINE_SPEC.md` BSL-010/BSL-011 — aman dibersihkan sebagai cleanup opsional, bukan wajib migrasi | — |
| DIFF-14 | `__manifest__.py:17` `'version': '18.0.1.0.0'` | Konvensi versi manifest | **Wajib diupdate (housekeeping standar, bukan breaking API)** | Bukan perubahan API, tapi WAJIB di-bump ke `19.0.1.0.0` di Step 6 Fase A — konvensi standar tiap migrasi, dicatat di sini supaya tidak lupa | — |

**Kesimpulan §1:** Modul ini murni backend SQL-view + 1 method Python + 2 view XML + test suite. **DIFF-01** (install-blocking, `<group expand=/string=>` di search view) dan **DIFF-02** (test-blocking, `res.users.groups_id`→`group_ids`) adalah dua perubahan wajib yang genuinely baru untuk pasangan versi 18→19 (bukan pengulangan temuan 17→18). **DIFF-10** perlu verifikasi eksekusi nyata di Step 9 G1 sebelum dianggap aman — jangan diasumsikan otomatis OK dari review statis semata. **DIFF-03** opsional cleanup (deprecated, tidak blocking). Sisanya konfirmasi stabil.

## 2. Kompatibilitas Dependency (OCA/Third-Party)

| Dependency | Versi target tersedia? | Sumber cek | Risiko |
|---|---|---|---|
| `base` | Ya, core 19.0 | `enterprise19.0/odoo/addons/base/` ada | Rendah — hanya `res.users.groups_id`→`group_ids` (DIFF-02) dan skema `<group>` (DIFF-01) yang relevan ke modul ini |
| `stock` | Ya, core 19.0 | `enterprise19.0/odoo/addons/stock/` ada, semua simbol yang dipakai modul dikonfirmasi §1 | Rendah — semua field SQL mentah stabil (DIFF-04), satu-satunya area abu-abu adalah DIFF-10 (xmlid picking type/location di test) |

Tidak ada dependency OCA/third-party (dikonfirmasi `01a_MIGRATION_INTAKE.md` §0).

## 3. Temuan Baru — Kandidat untuk Migration Records

- [x] `DIFF-01` (`<group expand=/string=>` dihapus dari skema RNG) — **temuan baru**, TIDAK ada di `knowledge/version-diffs/18-to-19.md` §1/§2 sama sekali (§2 malah salah mengklaim ini perubahan `<tree>`→`<list>` era 17→18, BUKAN soal atribut `<group>`). Dicatat ke `migration-tool/migration-records/product_history_report_18.0_19.0/SUMMARY.md` kategori `version-diff`.
- [x] `DIFF-02` (`res.users.groups_id`→`group_ids`) — ini KONFIRMASI ULANG dari `knowledge/version-diffs/18-to-19.md` §1 yang sudah ada (riset di muka, sekarang diverifikasi relevan ke project nyata KEDUA). Tetap dicatat ke `SUMMARY.md` sebagai data point konfirmasi.
- [x] `DIFF-03` (`self._cr` deprecated tapi tetap jalan) — konfirmasi ulang §1 knowledge base yang sudah ada, tidak perlu ditulis ulang ke `SUMMARY.md`.
- [x] `DIFF-10` (xmlid picking type/location + rewrite `TestStockCommon` di 19.0) — **temuan baru** (kategori `dependency-compat`, `stock`), dicatat sebagai open question ke `SUMMARY.md` — perlu ditutup dengan hasil eksekusi nyata Step 9 G1, bukan cuma dugaan dari review statis.

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| DIFF-01 — `<group expand=/string=>` search view | **Tinggi (install-blocking)** | Wajib fix di Step 6 (hapus dua atribut itu) sebelum modul bisa install sama sekali di 19.0 |
| DIFF-02 — `res.users.groups_id`→`group_ids` di test fixture | **Tinggi (test-blocking, 1 test: `test_ac_05_01_...`)** | Wajib fix `group_ids` di Step 6 sebelum Step 9 bisa jalan penuh |
| DIFF-10 — xmlid picking type/location di test + rewrite `TestStockCommon` 19.0 | **Sedang (belum pasti, perlu verifikasi G1)** | Tidak diubah dulu di Step 6 kecuali G1 (eksekusi nyata) membuktikan memang gagal — analog `DIFF-12` project 17→18 |
| DIFF-03 — `self._cr` deprecated | Rendah | Opsional dibersihkan ke `self.env.cr`, tidak wajib |
| DIFF-14 — bump versi manifest | Rendah (housekeeping wajib, bukan risiko teknis) | Standar tiap migrasi, dikerjakan Step 6 Fase A |
| DIFF-04 s/d DIFF-09, DIFF-11, DIFF-12, DIFF-13 | Tidak ada / sangat rendah | Semua dikonfirmasi stabil lewat cek langsung ke `native-target` |
