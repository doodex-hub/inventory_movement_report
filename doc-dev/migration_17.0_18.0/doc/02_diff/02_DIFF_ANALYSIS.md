# Diff & Compatibility Analysis — product_history_report

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `migration-tool/knowledge/version-diffs/17-to-18.md`

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi |
|---|---|---|
| `version-diffs/17-to-18.md` | Ya | `migration-tool/knowledge/version-diffs/17-to-18.md` §1 (dipakai langsung — `<tree>`→`<list>` blocker sudah terdokumentasi di sana) |
| `dependency-compat/stock/...` | Tidak | Belum ada entry khusus `stock` — temuan Step 2 ini dicatat ke `migration-records/product_history_report_17.0_18.0/SUMMARY.md` sebagai kandidat |

## 0b. Gate Community vs Enterprise

- [x] Dicek ulang `01a_MIGRATION_INTAKE.md` §2 — TIDAK ADA baris "Native Enterprise". Dependency cuma `base`+`stock`, keduanya Community.
- [x] Lanjut §1 di bawah cukup dengan `native-target` (`odoo18`) vs `native-source` (`odoo17`) Community saja.

## 0c. Gate Transitive Dependency

- [x] Tidak ada dependency yang akan dihapus dari `depends` (`base`+`stock` tetap dipakai, keduanya masih ada utuh di 18.0) — gate ini N/A, dicatat eksplisit supaya jelas bukan terlewat.

---

## 1. Perubahan Native (Core/Enterprise)

Simbol yang dipakai/di-inherit modul ini, dicek langsung terhadap `native-target` (`odoo18`) vs `native-source` (`odoo17`).

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `views/stock_history_view.xml:51` `<tree string="stock history">` (record `stock_history_tree_view2`) | Sintaks view XML — `<tree>` dihapus, wajib `<list>` | **Dihapus/Rename (install-blocking)** | Modul **gagal install total** di 18.0 kalau tidak diubah — `ParseError: Invalid view type: 'tree'` | `knowledge/version-diffs/17-to-18.md` §1 (`odoo/odoo#159909`), dikonfirmasi juga: 0 occurrence `<tree` tersisa di `odoo18/addons/stock/**` (grep langsung) |
| DIFF-02 | `views/stock_history_view.xml:66,73` (`action_stock_history_graph2` `view_mode="graph,tree,pivot"`, `action_stock_history_tree2` `view_mode="tree,pivot,graph"`) + `models/product_template.py:29` (`'view_mode': 'graph,pivot,tree'`) | Token `view_mode` — `tree` sebagai token view mode diganti `list` | **Rename (install/runtime-blocking untuk view mode itu)** | Window action dengan token `view_mode` masih menyebut `tree` akan gagal me-resolve view tree yang sudah tidak ada — konsisten dengan DIFF-01 (dua sisi dari perubahan yang sama) | Dikonfirmasi langsung: `odoo18/addons/stock/views/stock_move_views.xml:388` pakai `<field name="view_mode">list</field>`; grep `view_mode` dengan token `tree,` di seluruh `odoo18/addons/stock/**` → 0 match (semua sudah `list`) |
| DIFF-03 | `models/product_template.py:28` (`'view_type': 'form'`) | Key `view_type` di dict action window | Tidak dipakai lagi secara aktif | Rendah — key ini sudah lama tidak dipakai native manapun yang dicek (`odoo18/addons/stock` 0 match), kemungkinan besar diam-diam diabaikan ORM, bukan error. Belum ditemukan bukti ini bikin crash | Grep langsung `odoo18/addons/stock` untuk `'view_type': 'form'` → 0 match |
| DIFF-04 | `views/views.xml:7` `inherit_id="stock.product_template_form_view_procurement_button"` + xpath implisit `<button name="action_view_stock_move_lines" position="after">` | XML-ID `product_template_form_view_procurement_button` + button `action_view_stock_move_lines` | **Tidak berubah** | Aman — inherit target dan xpath implisit tetap match | `odoo18/addons/stock/views/product_views.xml:398` (XML-ID ada), `:325` (button `action_view_stock_move_lines` ada, atribut `name` tidak berubah) |
| DIFF-05 | `models/stock_history_view.py` SQL mentah — `stock_move_line.quantity`, `.date`, `.company_id`; `stock_move.date`, `.company_id`, `.location_id`, `.location_dest_id`, `.state`; `product_product.product_tmpl_id`; `product_template.uom_id`, `.categ_id`, `.active` | Field-field core `stock`/`product` di atas | **Tidak berubah** | Aman — semua kolom fisik yang dipakai query SQL mentah tetap ada dengan nama sama, query tidak perlu diubah | Dicek langsung `odoo18/addons/stock/models/stock_move_line.py:35` (`quantity = fields.Float(...)`, `:56` `date`), `stock_move.py:34,41,77,83,109` (`date`/`company_id`/`location_id`/`location_dest_id`/`state`) — identik dengan `odoo17` pada baris yang sama persis |
| DIFF-06 | `models/stock_history_view.py:1,25` `from odoo import ... tools` + `tools.drop_view_if_exists(self._cr, 'stock_history_view')` | `odoo.tools.sql.drop_view_if_exists` | **Tidak berubah** | Aman | `odoo18/odoo/tools/sql.py:582` vs `odoo17/odoo/tools/sql.py:544` — signature & nama identik |
| DIFF-07 | `models/product_template.py:17` `self.env.companies.ids` | API multi-company `env.companies` | **Tidak berubah** | Aman — tidak ada perubahan API multi-company yang relevan di `knowledge/version-diffs/17-to-18.md` | Tidak ada entry breaking di knowledge base untuk `env.companies`; API ini sudah stabil sejak versi jauh lebih lama |
| DIFF-08 | `security/ir.model.access.csv` | Format CSV ACL | **Tidak berubah** | Aman | Format `ir.model.access.csv` tidak berubah 17→18 |
| DIFF-09 | Modul tidak override `create()`/`copy()`/`search()`/`_name_search`/`_check_recursion`/`user_has_groups` | Berbagai breaking change API di `knowledge/version-diffs/17-to-18.md` §1 | **N/A** | Tidak berdampak — modul tidak memakai simbol manapun yang berubah di daftar breaking change umum 17→18 | Grep langsung `source-codebase/product_history_report/**/*.py` — tidak ada match untuk `user_has_groups`, `_name_search`, `_check_recursion`, `check_access_rights`, `@api.model\s+def create` |
| DIFF-10 | `controllers/controllers.py` (boilerplate, semua di-comment) | N/A | **Tidak berubah** | Tidak ada dampak — file ini tidak expose route apapun di kedua versi | `01b_BASELINE_SPEC.md` BSL — sudah dicatat sebagai dead code, bukan target migrasi aktif |
| DIFF-11 | `models/product_template.py:3`, `models/stock_history_view.py:3` `from odoo.http import request` (tidak dipakai) | N/A | **Tidak berubah** | Dead import, aman dihapus sebagai cleanup opsional (bukan migrasi wajib) — lihat `01b_BASELINE_SPEC.md` BSL-011 | — |

| DIFF-12 | `tests/test_product_history_report.py:27` `cls.env['product.template'].create({'name': ..., 'type': 'product'})` | `product.template.type` — selection value `'product'` dihapus | **Rename (test-blocking, ditemukan lewat eksekusi G1 nyata, BUKAN review statis)** | `setUpClass` test GAGAL total (`ValueError: Wrong value for product.template.type: 'product'`) — SEMUA 8 test di file ini tidak bisa jalan sama sekali (gagal di `setUpClass`, bukan cuma 1 test) sampai diperbaiki. Bukan bug modul (`product_history_report` tidak pernah set `type='product'` di kode produksinya sendiri), murni fixture test lama | Dikonfirmasi eksekusi nyata `docker compose up` (G1, Odoo 18.0 resmi) + cek langsung `odoo18/addons/product/models/product_template.py:57-68` (`selection=[('consu','Goods'),('service','Service'),('combo','Combo')]`, TIDAK ADA `'product'` lagi) dan `odoo18/addons/stock/models/product.py:691` (field baru `is_storable` Boolean, ditambahkan modul `stock`, menggantikan peran `type='product'` untuk produk storable/tracked) |

**Kesimpulan §1:** Modul ini murni backend SQL-view + 1 method Python + 2 view XML. **DIFF-01/DIFF-02** (install-blocking, sisi dari `<tree>`→`<list>` yang sama) dan **DIFF-12** (test-blocking, ditemukan lewat eksekusi G1 nyata bukan review statis) adalah tiga perubahan wajib — sisanya konfirmasi stabil, tidak perlu perubahan kode produksi.

## 2. Kompatibilitas Dependency (OCA/Third-Party)

| Dependency | Versi target tersedia? | Sumber cek | Risiko |
|---|---|---|---|
| `base` | Ya, core 18.0 | `odoo18/odoo/addons/base/` ada | Tidak ada |
| `stock` | Ya, core 18.0 | `odoo18/addons/stock/` ada, semua simbol yang dipakai modul dikonfirmasi §1 | Tidak ada |

Tidak ada dependency OCA/third-party (dikonfirmasi `01a_MIGRATION_INTAKE.md` §0).

## 3. Temuan Baru — Kandidat untuk Migration Records

- [x] `DIFF-01`/`DIFF-02` (`<tree>`→`<list>` + token `view_mode`) — ini KONFIRMASI ULANG dari entry `knowledge/version-diffs/17-to-18.md` §1 yang sudah ada, bukan temuan baru. Tidak perlu ditulis ke `SUMMARY.md`.
- [x] `DIFF-05` (stabilitas field `stock.move`/`stock.move.line` dipakai lewat SQL mentah, bukan ORM) — **temuan baru**, dicatat ke `migration-tool/migration-records/product_history_report_17.0_18.0/SUMMARY.md` kategori `dependency-compat` (`stock`), kandidat promosi ke `knowledge/dependency-compat/stock/17-to-18.md` (belum ada entry `stock` di knowledge base).

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| DIFF-01/DIFF-02 — `<tree>`/`view_mode` token `tree` | **Tinggi (install-blocking)** | Wajib fix di Step 6 Fase C (view migration) sebelum modul bisa install sama sekali di 18.0 |
| DIFF-03 — `view_type: 'form'` dead key | Rendah | Opsional dibersihkan, tidak wajib |
| DIFF-04 s/d DIFF-11 | Tidak ada / sangat rendah | Semua dikonfirmasi stabil lewat cek langsung ke `native-target` |
| DIFF-12 — `product.template.type='product'` di test fixture | **Tinggi (test-blocking, semua 8 test)** | Ditemukan lewat eksekusi G1 nyata (bukan review statis) — wajib fix `is_storable=True` sebelum Step 9 bisa jalan |
