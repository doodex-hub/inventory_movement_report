# Diff & Compatibility Analysis — product_history_report

**Step:** 2 — Diff & Compatibility Analysis
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-24
**Status:** ✅ Selesai (step non-gate)
**Ref:** `01_intake/01a_MIGRATION_INTAKE.md`, `01_intake/01b_BASELINE_SPEC.md`, `migration-tool/knowledge/`

Native yang dicek langsung: `native-source` `odoo19` (19.0), `native-target` `odoo20` (20.0, HEAD `b0329e93ae8`), `native-source-enterprise` `enterprise19`, `native-target-enterprise` `enterprise20` (HEAD `bbccc6bce1`).

---

## 0. Knowledge Base Check

| Sumber | Sudah ada entry? | Lokasi | Relevan? |
|---|---|---|---|
| `version-diffs/19-to-20.md` | Ya (6 baris, dari `optional_field_save` + `pos_margin_sale`) | `migration-tool/knowledge/version-diffs/19-to-20.md` | **Ya — baris `ir.model.access.csv`/`ir.rule` → `ir.access.csv`** (DIFF-01). Baris lain (`/web/session/logout`, `logOutItem`, ACL `res.partner` self-write, `computeOptionalActiveFields`, fitur pin `mail`) tidak relevan — modul tidak menyentuh `web` JS/`res.partner`/`mail` (dikonfirmasi grep §0d). |
| `dependency-compat/stock/` | Ada `18-to-19.md` saja, belum ada `19-to-20.md` | — | Konteks: `stock.move.name`→`reference` (sudah ditangani 18→19). Tidak ada entry 19→20 — analisis baru (DIFF-03). |
| `dependency-compat/base/` | Tidak ada | — | — |
| `migration-records/pos-margin-sale_19.0_20.0/SUMMARY.md` (kandidat, belum dipromosikan) | `_to_store` dihapus, `product_variant_easy_edit_view` dihapus | — | Tidak relevan (grep §0d: 0 match) |

## 0b. Gate Community vs Enterprise

- [x] Intake §2: tidak ada dependency Enterprise di manifest, TAPI dev menjawab "enterprise kemungkinan depend" (MF-07) → Enterprise tetap dicek penuh sebagai lingkungan deploy.
- [x] `enterprise20` dicek: (1) tidak ada model/tabel/method bernama `stock.history.view`/`stock_history_view`/`action_open_stock_history` (0 match `*.py/*.xml/*.csv`) — tidak ada tabrakan; (2) tidak ada XML Enterprise yang merujuk `action_view_stock_move_lines` (anchor xpath modul ini) — tidak ada Enterprise yang memindah/menghapus anchor; (3) `quality_control` meng-inherit view yang sama (`stock.product_template_form_view_procurement_button`) tapi xpath-nya ke `action_view_related_putaway_rules`, tidak bersinggungan — 19.0 vs 20.0 bedanya cuma ikon `fa-list`/`fa-check` → `format_list_bulleted`/`check` (bukti tambahan DIFF-02: Enterprise juga ikut migrasi ikon); (4) `web_enterprise` (`auto_install: ['web']`) mengganti menu apps Community dengan Home Menu → selector `.o_navbar_apps_menu button` di tour test tidak ada di instance Enterprise (DIFF-12 — dampak ke test harness, bukan behavior modul). Kolom "Sumber" di §1 menyebut clone mana yang dicek.

## 0c. Gate Transitive Dependency

- [x] Tidak ada dependency yang dihapus dari `depends` — gate N/A. Dicatat: dicek, tidak ada dependency transitif yang perlu ditambahkan.

## 0d. Gate Grep Menyeluruh

Grep seluruh `product_history_report/` (`*.py`, `*.xml`, `*.js`, `*.csv`, termasuk `tests/`) untuk semua simbol dari knowledge base 19→20 + temuan analisis baru:

| Simbol | Hasil | DIFF |
|---|---|---|
| `ir.model.access` | `__manifest__.py:23` (+ file `security/ir.model.access.csv`) | DIFF-01 |
| `ir.rule` | 0 | — |
| `session/logout`, `log_out`, `user_menu_items`, `computeOptionalActiveFields`, `pinned_at`, `_to_store`, `easy_edit` | 0 | — |
| `product_uom` (key) | `tests/test_product_history_report.py:68` (`'product_uom': ...`). `product_uom_qty` di baris 67 TIDAK terdampak (masih ada di 20.0) | DIFF-03 |
| `product_uom_id` | 0 | — |
| `icon="fa-` / `fa-` | `views/views.xml:13` (`icon="fa-signal"`). (`static/description/index.html` halaman store tidak dirender web client — di luar lingkup) | DIFF-02 |
| `self._cr` | `models/stock_history_view.py:25,110` | DIFF-07 (tidak berubah) |
| `registry.clear_cache`, `_rec_names_search`, `t-call`, `groups_id`, `<tree`, `.name` | 0 | — |
| `@odoo-module` | `static/tests/tours/stock_history_tour.js:1` | DIFF-11 (tidak berubah) |
| `view_type` | `models/product_template.py:28` (dict action), `tests/...py:94` (`get_view(view_type=...)`) | DIFF-08 (tidak berubah) |

## 0e. Gate Silent-Regression per Tipe Override

| Override | Kategori | Hasil cek |
|---|---|---|
| `product.template.action_open_stock_history()` | (a) Python — method BARU (bukan override; tanpa `super()`) | Arah kedua (tabrakan dengan native target): `action_open_stock_history` 0 match di `odoo20` + `enterprise20` → tidak ada method native baru bernama sama. Entry point: tombol XML `type="object"` — tidak berubah. |
| `stock.history.view` (model baru `_auto=False`) + `recreate_view()` | (a) Python — model & method baru | Tabrakan nama model/tabel `stock_history_view` di `odoo20`/`enterprise20`: 0 match. Kolom SQL yang dibaca langsung — lihat DIFF-05. |
| `views/views.xml` inherit `stock.product_template_form_view_procurement_button` | (b) XML inheritance | View native masih ada (`odoo20/addons/stock/views/product_views.xml:423`), `<button name="action_view_stock_move_lines">` masih ada di dalam `<t groups="stock.group_stock_user">` yang sama → xpath match, visibilitas grup sama. Tombol tetangga berganti ikon (DIFF-02). |
| Tour `stock_history_tour` (`web_tour.tours` registry) | (d) Registry | Shape registry 20.0 (`web_tour/static/src/@types/registries.d.ts`): `{test?, url, steps()}` — sama dengan yang dipakai. Selector UI diverifikasi lewat eksekusi nyata di G1/Step 9 (DIFF-11, DIFF-12). |
| (c) Owl `patch()` | — | Tidak ada. |

Step 9 wajib assert NILAI (qty/income/outcome, atribut `data-icon` tombol, isi baris ACL), bukan cuma "tidak ada exception".

---

## 1. Perubahan Native (Core/Enterprise)

| ID | File/simbol modul | Simbol native terkait | Status di target | Dampak | Sumber |
|---|---|---|---|---|---|
| DIFF-01 | `security/ir.model.access.csv` + entry manifest `data` | Model `ir.model.access` (dan `ir.rule`) | **Dihapus** — diganti model `ir.access` (`odoo20/odoo/addons/base/models/ir_access.py`), file data `ir.access.csv` skema `id,name,model_id,group_id/id,operation,domain`. `convert_csv_import` menurunkan nama model dari nama file (`odoo20/odoo/tools/convert.py:739-740`) → `ir.model.access.csv` akan mencari `env['ir.model.access']` yang tidak ada → **install gagal**. Semua 226 manifest addon Community 20.0 sudah pakai `ir.access.csv` (0 yang masih `ir.model.access.csv`). **Semantik baru:** baris tanpa `group_id` = *restriction* (`kind='restriction'`, di-AND, tidak memberi akses); baris dengan grup = *permission* (di-OR). Port mentah baris tanpa grup = model tak bisa diakses siapapun. Konversi resmi (`odoo20/odoo/upgrade_code/19.4-00-ir-access.py:517-519`): ACL tanpa grup → `base.group_everyone` (grup baru 20.0 "Role / Everyone", `odoo20/odoo/addons/base/security/base_groups.xml:92-96`, di-imply `group_portal`+`group_public`+`group_user`; TIDAK ada di 19.0). | **Tinggi (install-blocking) — wajib.** Target: `security/ir.access.csv` berisi `access_stock_history_view,stock_history_view,stock.history.view,base.group_everyone,crud,`; manifest `data` ganti path. Mempertahankan BSL-007/MF-03 (akses terbuka semua user). | Knowledge base (`19-to-20.md` baris 3) + analisis baru `odoo20` (semantik restriction/permission, konversi resmi, `group_everyone`) |
| DIFF-02 | `views/views.xml:13` `icon="fa-signal"` | `ViewButton` `iconFromString()` (`odoo20/addons/web/static/src/views/view_button/view_button.js:24-30`), `.oi` mixin (`odoo20/addons/web/static/src/webclient/icons.scss`), font subset `addons/web/tooling/icons/icons_wishlist.txt` | **Behavior berubah** — 19.0: `icon` `fa-*` → `<i class="fa fa-signal">` Font Awesome. 20.0: selalu `<i class="o_button_icon oi" data-icon="fa-signal">` dirender via ligature Material Symbols — `fa-signal` bukan nama ligature valid → ikon rusak/teks liar. Stat button native di view yang sama sudah dikonversi (`fa-exchange`→`sync_alt`, `fa-refresh`→`cached`, `fa-area-chart`→`area_chart`, dst). Padanan resmi Odoo untuk `fa-signal`: `android_cell_5_bar` (`odoo20/addons/sale/views/product_views.xml:57,100`, commit native `5d739f24054`), ada di subset font (`icons_wishlist.txt:17`). | **Sedang (visual, silent — tidak error install).** Target: `icon="android_cell_5_bar"`. Mempertahankan BSL-013 (tombol ber-ikon bar sinyal). MF-05. | Analisis baru `odoo20` + `enterprise20` (`quality_control`) |
| DIFF-03 | `tests/test_product_history_report.py:68` `'product_uom': self.product.uom_id.id` di `stock.move.create()` | `stock.move.product_uom` | **Rename** → `uom_id` (`odoo20/addons/stock/models/stock_move.py:68`, compute+store+precompute; commit native `3852885f37a` "[IMP] uom: rename logistic fields" — juga `stock.move.line.product_uom_id`→`uom_id`, tidak dipakai modul). Field tak dikenal di `create()` → `ValueError: Invalid field 'product_uom'` → 4 test Integration yang pakai `_make_move` (AC-02-01, AC-03-01, AC-03-02, AC-04-01) gagal. | **Sedang (test-only, tidak menyentuh kode produksi).** Target: key `'uom_id'`. SQL `recreate_view()` tidak memakai kolom uom `stock_move` (hanya `product_template.uom_id`, tidak berubah). | Analisis baru `odoo20` (knowledge base belum punya — kandidat `dependency-compat/stock/19-to-20.md`) |
| DIFF-04 | `__manifest__.py` `version: '19.0.1.0.0'` | Konvensi versi modul | **Wajib diubah** — prefix versi harus seri 20.0 | Rendah. Target `20.0.1.0.0`. | Konvensi Odoo |
| DIFF-05 | SQL mentah `recreate_view()` — kolom `stock_move(id, product_id, state, location_id, location_dest_id, company_id)`, `stock_move_line(move_id, product_id, quantity, date, company_id)`, `stock_location(id, usage)`, `product_product(id, product_tmpl_id)`, `product_template(id, active, uom_id, categ_id)` | Field ORM tersimpan terkait di `stock`/`product` | **Tidak berubah** — semua field ada & stored di 20.0 (`stock_move.py` `location_id`/`location_dest_id` store=True, `stock_move_line.py:38,61` `quantity`/`date`, `stock_location.py:33` `usage` selection sama termasuk `'internal'`, `product_template.py:90,156,167` `categ_id`/`uom_id`/`active`). | Tidak ada. Dibuktikan ulang lewat test Integration (nilai qty/income/outcome) di Step 9. | Analisis baru `odoo19` vs `odoo20` |
| DIFF-06 | `views/views.xml` `inherit_id="stock.product_template_form_view_procurement_button"`, xpath `<button name="action_view_stock_move_lines" position="after">` | View native & tombol anchor | **Tidak berubah** (struktur) — record masih ada, anchor masih di dalam `<t groups="stock.group_stock_user">`. Perubahan 20.0 di view itu hanya ikon tombol lain + `tracking`→`store_by` untuk tombol lot (tidak bersinggungan). | Tidak ada. | Analisis baru `odoo19` vs `odoo20` (diff record penuh) |
| DIFF-07 | `models/stock_history_view.py:25,110` `self._cr`, `tools.drop_view_if_exists` | `BaseModel._cr`, `odoo.tools.sql.drop_view_if_exists` | **Tidak berubah** — `_cr` sudah `@deprecated("Deprecated since 19.0, use self.env.cr directly")` di 19.0 dan masih sama di 20.0 (`odoo20/odoo/orm/models.py:5389-5391`), hanya warning. `drop_view_if_exists(cr, viewname)` signature sama (`odoo20/odoo/tools/sql.py:651`). | Tidak ada. **Dipertahankan** (bukan wajib kompatibilitas; mengganti = refactor terlarang CLAUDE.md). | Analisis baru |
| DIFF-08 | `models/product_template.py:28` dict action berisi `'view_type': 'form'`; test `get_view(view_type='form')` | `ir.actions.act_window` dict, `Base.get_view()` | **Tidak berubah** — `view_type` di dict action sudah diabaikan web client sejak lama (19.0 juga); `get_view(self, view_id=None, view_type='form', **options)` sama (`odoo20/odoo/addons/base/models/ir_ui_view.py:3164`). | Tidak ada — dipertahankan apa adanya. | Analisis baru |
| DIFF-09 | Model `stock.history.view` tanpa `_description` | `model_classes.py` warning | **Tidak berubah** — warning "has no _description" ada di 19.0 dan 20.0 (`odoo20/odoo/orm/model_classes.py:295`). | Tidak ada — dipertahankan (menambah `_description` bukan wajib kompatibilitas). | Analisis baru |
| DIFF-10 | Test API: `product.template.is_storable`, `res.users.group_ids`, `stock.picking` `action_confirm`/`action_assign`/`button_validate`, `stock.move.line.quantity`, xmlid `stock.stock_location_*`/`stock.picking_type_*`, `stock.group_stock_user`, `invalidate_model`/`invalidate_recordset`, `mute_logger` | `product`/`base`/`stock`/`odoo.tests` | **Tidak berubah** — field/grup ada di 20.0 (`res_users.py:251` `group_ids`; `stock_security.xml:9` `group_stock_user` identik 19.0). | Tidak ada (dibuktikan G1). | Analisis baru |
| DIFF-11 | Tour `static/tests/tours/stock_history_tour.js` — `/** @odoo-module **/`, registry `web_tour.tours`, selector `.o_navbar_apps_menu button`, `.o_app[data-menu-xmlid="stock.menu_stock_root"]`, `button:contains("Products")`, `.o_searchview_input`, `.o_kanban_record`, `.o_breadcrumb .active`, `.o_searchview_dropdown_toggler`, `.o_group_by_menu .o_menu_item` | `web_tour`, navbar, search bar | **Tidak berubah (statis)** — shape registry sama; `@odoo-module` masih diproses transpiler 20.0 (`odoo20/odoo/tools/js_transpiler.py`); menu `stock.menu_stock_root` + "Products" (`menu_stock_inventory_control`) sama; kelas navbar/search masih ada di `odoo20/addons/web/static/src`. Kepastian penuh hanya dari eksekusi tour (pelajaran DIFF-16 18→19). | Rendah-Sedang (test-only). Verifikasi G1/Step 9. | Analisis baru |
| DIFF-12 | Tour yang sama, dijalankan di instance **Enterprise** | `web_enterprise` Home Menu (`enterprise20/web_enterprise`, `auto_install: ['web']`) | **Behavior lingkungan berbeda** — di Enterprise tidak ada `.o_navbar_apps_menu` (diganti Home Menu), step pertama tour tidak akan ketemu. Sama berlakunya di 19.0 Enterprise (tidak pernah dites di 18→19). | Rendah (test harness, bukan behavior modul). Penanganan di Step 3 (spec). | Analisis baru `enterprise20` |
| DIFF-13 | Lingkungan deploy Enterprise — modul Enterprise stock/quality | `quality_control` (inherit view yang sama), `stock_enterprise`, `stock_barcode`, `stock_accountant` | **Tidak berubah untuk modul ini** — tidak ada tabrakan nama, tidak ada Enterprise yang menyentuh anchor tombol atau tabel yang dibaca SQL modul (Enterprise tidak mengubah kolom `stock_move`/`stock_move_line` inti yang dipakai). | Rendah. Dibuktikan lewat run Step 9 dengan addons Enterprise. | Analisis baru `enterprise19` vs `enterprise20` |

### 1b. Perubahan disengaja non-native (dari intake, bukan breaking change)

| ID | Item | Keputusan |
|---|---|---|
| SCOPE-01 | Port aset App Store dari branch rilis `19.0`: `static/description/**` (banner.gif, icon.png baru, `assets/gifs|icons|screens`, `index.html` baru; `banner.png` + 4 aset lama dihapus seperti di branch 19.0) + key `images` manifest `['static/description/banner.gif', 'static/description/icon.png']` | Disetujui dev 2026-09-24 (MF-06) |

## 2. Kompatibilitas Dependency (OCA/Third-Party)

| Dependency | Versi target tersedia? | Sumber cek | Risiko |
|---|---|---|---|
| — | — | Tidak ada dependency OCA/third-party (intake §0) | — |

## 3. Temuan Baru — Tulis ke Migration Records

- [x] Kandidat `version-diff`: (a) ikon `fa-*` di atribut `icon` button → Material Symbols (`fa-signal`→`android_cell_5_bar`, dengan cara deteksi & sumber pemetaan resmi); (b) melengkapi entry `ir.access` yang ada — semantik baris tanpa grup = restriction + konversi resmi ke `base.group_everyone` (menjawab "butuh riset tambahan" di knowledge base: nama file lama TIDAK diterima, model `ir.model.access` tidak ada lagi).
- [x] Kandidat `dependency-compat` (`stock/19-to-20.md`): `stock.move.product_uom` → `uom_id`, `stock.move.line.product_uom_id` → `uom_id`.
- [x] Kandidat proses/tool: tour test yang navigasi via `.o_navbar_apps_menu` tidak portable ke instance Enterprise (`web_enterprise` Home Menu).
- Ditulis ke `migration-tool/migration-records/product_history_report_19.0_20.0/SUMMARY.md` — TIDAK dipromosikan ke `knowledge/` di step ini.

## 4. Ringkasan Risiko

| Item | Level risiko | Catatan |
|---|---|---|
| DIFF-01 ACL → `ir.access` | Tinggi | Install-blocking; semantik grup wajib `base.group_everyone` agar BSL-007 identik. Verifikasi: test AC-05-01 (user internal tanpa grup stock bisa read) + assert isi record `ir.access` + (baru) user portal. |
| DIFF-02 ikon Material | Sedang | Silent visual; install tetap sukses. Verifikasi: assert arch `icon="android_cell_5_bar"` + DOM `data-icon` di tour. |
| DIFF-03 `product_uom`→`uom_id` (test) | Sedang | 4 test gagal kalau tidak diubah; kode produksi aman. |
| DIFF-11/12 tour | Rendah-Sedang | Hanya terbukti lewat eksekusi nyata; Enterprise butuh penanganan harness. |
| DIFF-05 SQL | Rendah | Kolom stabil; dibuktikan nilai test. |
| Sisanya | Rendah | Tidak berubah. |
