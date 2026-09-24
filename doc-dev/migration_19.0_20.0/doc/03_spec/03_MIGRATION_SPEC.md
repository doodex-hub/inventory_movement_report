# Migration Spec (Teknis) — product_history_report

**Step:** 3 — Migration Spec
**Versi:** 19.0 → 20.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-09-24
**Status:** ✅ Selesai (step non-gate)

> Dokumen ini memandu IMPLEMENTASI (step 6). Dasar testing/acceptance = `01b_BASELINE_SPEC.md` + kode 19.0, bukan dokumen ini.

---

## 1. Ringkasan Strategi

Port langsung dengan **3 perubahan wajib kompatibilitas** + 1 perubahan disengaja:
1. ACL `ir.model.access.csv` → `ir.access.csv` dengan `base.group_everyone` (DIFF-01, install-blocking).
2. Ikon stat button `fa-signal` → `android_cell_5_bar` (DIFF-02, silent visual).
3. Test fixture `stock.move` `'product_uom'` → `'uom_id'` (DIFF-03, test-only).
4. Versi manifest `20.0.1.0.0` (DIFF-04).
5. SCOPE-01: port aset store `static/description/**` + key `images` dari branch rilis `19.0` (disetujui dev).

Kode Python (`models/*.py`) **tidak diubah sama sekali** — SQL, logika window, race condition, dead import, `self._cr` (deprecated sejak 19.0, bukan wajib) dipertahankan byte-identik. Test ditambah (bukan diganti) untuk membuktikan DIFF-01/02 dan menangani DIFF-12.

## 2. Strategi per File/Simbol

| File/simbol | Ref DIFF | Strategi migrasi | Risiko | Ref BSL |
|---|---|---|---|---|
| `security/ir.model.access.csv` → **hapus**; **baru** `security/ir.access.csv` | DIFF-01 | Isi persis output konversi resmi (`odoo/upgrade_code/19.4-00-ir-access.py`): header `id,name,model_id,group_id/id,operation,domain`, baris `access_stock_history_view,stock_history_view,stock.history.view,base.group_everyone,crud,`. XML-ID `access_stock_history_view` DIPERTAHANKAN (tidak rename). Verifikasi silang: jalankan skrip resmi `odoo-bin upgrade_code --script 19.4-00-ir-access` terhadap salinan modul 19.0 di container dan bandingkan output (Fase A2). | Tinggi → rendah setelah verifikasi skrip resmi | BSL-007, BSL-008 |
| `__manifest__.py` `data` | DIFF-01 | Ganti entry `'security/ir.model.access.csv'` → `'security/ir.access.csv'` **di posisi yang sama (pertama)** — menyimpang sengaja dari skrip resmi yang menambahkan di akhir list; urutan tidak berpengaruh karena file ACL cuma butuh model Python sudah terdaftar (selalu terjadi sebelum data load). Diff lebih kecil, konvensi "security dulu" tetap. | Rendah | — |
| `__manifest__.py` `version` | DIFF-04 | `19.0.1.0.0` → `20.0.1.0.0` | Rendah | BSL-015 |
| `__manifest__.py` `images` | SCOPE-01 | `['static/description/banner.png']` → `['static/description/banner.gif', 'static/description/icon.png']` (persis branch `19.0` commit `9b88ff8`) | Rendah | BSL-015 |
| `static/description/**` | SCOPE-01 | `git checkout 19.0 -- product_history_report/static/description` + hapus file yang dihapus di branch 19.0 (`banner.png`, `assets/doodex_odoo.png`, `assets/image_inventory_move.png`, `..._move2.png`, `..._move3.png`) supaya isi folder IDENTIK dengan branch `19.0` (59 file). `index.html` TIDAK diedit manual — header file itu sendiri menyatakan "DERIVED, NOT HAND-WRITTEN… Generated from the 17.0 source with tools/variant.py" (MF-08). | Rendah (ukuran repo +~31 MB karena banner.gif) | — |
| `views/views.xml` atribut `icon` | DIFF-02 | `icon="fa-signal"` → `icon="android_cell_5_bar"`. Atribut lain (`string`, `type`, `name`, `class`, posisi xpath) tidak disentuh. | Sedang → rendah dengan assert arch + DOM | BSL-013 |
| `views/stock_history_view.xml` | DIFF-06 (tidak berubah) | Tidak diubah (sudah `<list>`, `<group>` tanpa atribut sejak 18→19). | Rendah | BSL-010, BSL-012 |
| `models/product_template.py`, `models/stock_history_view.py`, `controllers/`, `__init__.py` | DIFF-05, 07, 08, 09 | **Tidak diubah** | Rendah | BSL-001..006, 009, 011, 014 |
| `tests/test_product_history_report.py` `_make_move` | DIFF-03 | `'product_uom': self.product.uom_id.id` → `'uom_id': self.product.uom_id.id` (satu key; nilai & semantik sama). Test lain tidak diubah. | Rendah | BSL-004..006 |
| `tests/test_product_history_report.py` — test BARU | DIFF-01, DIFF-02 | Tambah 3 test (tidak mengubah yang lama): (1) `test_ac_05_03_acl_record_is_group_everyone_crud` — record `ir.access` `product_history_report.access_stock_history_view`: `group_id == base.group_everyone`, `operation == 'crud'`, `domain` kosong, `kind == 'permission'`; (2) `test_ac_05_04_read_open_for_portal_user` — user portal (`base.group_portal`) bisa search baris view (BSL-007: 19.0 ACL tanpa grup berlaku semua user); (3) `test_ac_01_04_button_icon_is_material_signal` — arch form `product.template` memuat tombol `action_open_stock_history` dengan `icon="android_cell_5_bar"` dan tanpa `fa-signal`. | Rendah | BSL-007, BSL-013 |
| `tests/test_stock_history_tour.py` + tour lama | DIFF-11, DIFF-12 | Tour lama `stock_history_tour` DIPERTAHANKAN apa adanya (JS tidak diubah). Python: `test_stock_history_tour` di-`skipTest` HANYA bila modul `web_enterprise` terinstal (Home Menu Enterprise tidak punya `.o_navbar_apps_menu`) — di Community tetap jalan penuh. | Rendah | BSL-001, BSL-012 |
| `static/tests/tours/stock_history_form_tour.js` (BARU) + test Python baru | DIFF-02, DIFF-12 | Tour edition-agnostic, dimulai langsung dari URL form produk fixture (`/odoo/action-stock.product_template_action_product/<id>`): (1) assert tombol `button[name="action_open_stock_history"]` memuat `i.o_button_icon[data-icon="android_cell_5_bar"]` (bukti DOM DIFF-02), (2) klik tombol, (3) breadcrumb "Stocks Histories", (4) graph view ter-render (`.o_graph_renderer`, view pertama `graph,pivot,list` BSL-001/012). Jalan di Community DAN Enterprise. Kalau URL `/odoo/action-...` ternyata tidak memuat form di tour harness, fallback: navigasi `/web#model=product.template&id=<id>&view_type=form`. | Sedang (tour baru — terbukti hanya lewat eksekusi) | BSL-001, BSL-012, BSL-013 |
| `static/tests/tours/stock_history_tour.js` | DIFF-11 | Tidak diubah (header komentar tetap). | Rendah–Sedang (selector dibuktikan G1) | — |

## 2b. Risk Analysis Terstruktur

### Critical Migration Blockers

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version harus `20.0.x` | `__manifest__.py` | — |
| 2 | `ir.model.access.csv` tidak bisa di-load (model dihapus) | `security/`, `__manifest__.py` | `knowledge/version-diffs/19-to-20.md` baris `ir.access` |
| 3 | Baris ACL tanpa grup berubah semantik jadi restriction | `security/ir.access.csv` | idem + `SUMMARY.md` project ini |

**Priority:** HIGH — sebelum runtime testing apapun.

### OWL Widget yang Butuh Rewrite/Review
Tidak ada (tidak ada Owl aplikatif).

### Controller & Route
Tidak ada (`controllers/` kosong).

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Tour test baru di `web.assets_tests` — tercakup glob `product_history_report/static/tests/tours/*.js` yang sudah ada, manifest `assets` tidak perlu diubah | `__manifest__.py` | Rendah |
| 2 | Aset store +59 file (banner.gif 30 MB) | `static/description/` | Rendah |

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref BSL |
|---|---|---|---|---|
| 1 | Kolom SQL `stock_move`/`stock_move_line`/`stock_location`/`product_*` — tidak berubah | `models/stock_history_view.py` | Rendah (dibuktikan test nilai) | BSL-004..006 |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Instance Enterprise: `quality_control` meng-inherit view yang sama (xpath lain) — kombinasi view harus tetap valid | form `product.template` | Sedang — dibuktikan run Enterprise Step 9 |
| 2 | Instance Enterprise: Home Menu mengganti apps menu (tour lama) | test harness | Rendah — ditangani skip + tour baru |

### Urutan Prioritas Testing

1. Install & startup — Community murni (G1), lalu Community + Enterprise stock/quality (`stock_enterprise`, `quality_control`, `stock_barcode`).
2. ACL: record `ir.access` + akses user internal tanpa grup stock + user portal (AC-05-01/03/04), create gagal di DB (AC-05-02).
3. Core flow nilai: saldo pembuka, income/outcome, double-count, filter company (AC-02-01, AC-03-01/02, AC-04-01).
4. UI: arch tombol + ikon (AC-01-01/04), action dict (AC-01-02), tour Community (AC-01-03), tour form edition-agnostic.

### View List (dulu Tree) Checklist
Sudah `<list>`/`list` sejak 17→18 — tidak ada item.

### Estimasi Effort

| Area | Effort | Catatan |
|---|---|---|
| Kode produksi | < 30 menit | 4 file kecil |
| Test + tour baru | ~1 jam | termasuk debug selector tour |
| Environment Odoo 20 (build from source) | ~30-60 menit | resep `optional_field_save` |

## 3. Data Migration

N/A — port kode saja. (Catatan untuk kalau suatu saat jadi upgrade instance: skrip upgrade resmi Odoo sendiri yang mengonversi baris `ir.model.access` di DB; modul ini tidak butuh migration script.)

## 4. Scope

### Termasuk
- DIFF-01..04 (wajib), SCOPE-01 (disengaja), test tambahan pembukti.

### Di Luar Scope (sengaja)
- Memperbaiki MF-01..MF-04 (bug warisan).
- Mengganti `self._cr` → `self.env.cr`, menambah `_description`, membersihkan dead import/dead action (bukan wajib kompatibilitas).
- Mengedit manual `static/description/index.html` (masih menyebut "Odoo 19") dan README/LISEZMOI (masih "17.0") — dicatat MF-08, jadi tugas dev lewat tooling `tools/variant.py` mereka.
