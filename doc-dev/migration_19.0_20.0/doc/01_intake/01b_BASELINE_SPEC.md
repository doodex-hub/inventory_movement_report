# Baseline Spec — product_history_report

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 19.0.
**Tanggal:** 2026-09-24
**Status:** ✔️ Disetujui (gate Step 1, 2026-09-24)
**Sumber:** Direkonsiliasi dari `doc-dev/migration_18.0_19.0/doc/01_intake/01b_BASELINE_SPEC.md` (BSL-001..011, SELESAI + UAT 2026-08-26) + cross-check langsung ke kode `migration/19.0` (`git show migration/19.0:product_history_report/...`) + cross-check ulang ke `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` (BR-01..06) dan `01B_ACCEPTANCE_CRITERIA.md` (AC-01-01..AC-05-02). Test executable ada di lokasi yang sama (`product_history_report/tests/`, 9/9 PASS di 19.0).

---

## Ringkasan untuk Review — Perlu Konfirmasi User

Tally provenance: 11 `[MATCH]` (BSL-001..011, diwarisi & dicek ulang ke kode 19.0 — tidak ada drift), 0 `[GAP]`, 4 `[NO-SPEC]` baru (BSL-012..015 — klaim yang sebelumnya cuma deskriptif di §6 tanpa nomor, sekarang diberi ID karena justru area ini yang tersentuh perubahan 20.0; lesson `ai-doc/findings/2026-08-31_baseline-spec-field-coverage-gap.md`).

1. **BSL-002 / BSL-004 / BSL-007 / BSL-009 — 4 bug/quirk HARUS DIPERTAHANKAN** (race condition SQL view global, double-count transfer internal, ACL tanpa grup, ORM cache stale) — lihat `FINDINGS.md` MF-01..MF-04.
2. **BSL-007 dipertajam (penting untuk 20.0):** baris ACL tanpa `group_id` di 19.0 berlaku untuk SEMUA user — internal, portal, maupun public — bukan cuma user internal. Padanan persis di 20.0 adalah `base.group_everyone` (Step 2 DIFF-01).
3. **BSL-013 (baru)** — tampilan tombol: label "Stock History", ikon `fa-signal` (Font Awesome, bar sinyal), kelas `oe_stat_button`, diletakkan tepat setelah tombol "In/Out" (`action_view_stock_move_lines`). Di 20.0 ikon ini wajib diganti padanan Material Symbols agar tampilan tetap sama (DIFF-02).
4. **BSL-005** — window SQL ~13.2 bulan (baris saldo pembuka) vs filter tampil 12 bulan (Python) — pertahankan persis.
5. Modul murni backend + 1 tour test (bukan kode aplikatif).

---

## 1. Tujuan Modul

Modul menambah laporan riwayat pergerakan stok bulanan (~13 bulan terakhir) per produk, diakses lewat tombol statistik "Stock History" pada form `product.template`. User bisa melihat tren stok masuk/keluar dan quantity kumulatif dalam bentuk graph (default), pivot, atau list, tanpa membuka Stock Moves mentah.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `product.template` (extend) | Method `action_open_stock_history()` + tombol statistik pemicunya |
| `stock.history.view` (baru, `_auto=False`, SQL view, tanpa `_description`) | Baris laporan bulanan per `product_template_id`: tanggal akhir bulan (+ baris agregat saldo pembuka), income, outcome, qty kumulatif, kategori, UoM |

## 3. Field dengan Makna Bisnis

### stock.history.view
- **Identitas:** `date` (Date, label "Date"), `product_template_id` (M2o `product.template`, label "Product", readonly), `categ_id` (M2o `product.category`, label "Category", readonly), `uom_id` (M2o `uom.uom`, tanpa label eksplisit)
- **Struktur:** `income` (Float, label "Input", `digits=(8, 6)`), `outcome` (Float, label "Output", `digits=(8, 6)`), `qty` (Float, label "Stock Quantity uom", `digits=(8, 6)`, running sum `ROUND(..., 3)`) — lihat BSL-014
- **Desain:** `_auto=False`, isi = hasil `CREATE VIEW` SQL mentah, dibuat ulang tiap kali dibutuhkan. Primary key `id` = `CONCAT(product_template_id, YYYYMMDD)` (deterministik per produk+tanggal).

## 4. Business Workflow / State Transition

### Tombol Stock History (form produk)
- `[BSL-001]` `[MATCH]` (ref: BR-01, AC-01-01, AC-01-02) Form `product.template` mendapat tombol statistik "Stock History" (lihat BSL-013 untuk detail tampilan). Klik memanggil `action_open_stock_history()`, yang mengembalikan window action: `name` "Stocks Histories", `res_model` `stock.history.view`, `view_mode` `graph,pivot,list`, `target` `current`, `domain` `[('id', 'in', <ids baris dengan date >= date_debut>)]`, dengan `date_debut` = tanggal 1 bulan berjalan dikurangi 12 bulan. (Key `view_type: 'form'` ikut di dict — sisa lama, diabaikan web client.)
- `[BSL-002]` `[MATCH]` (ref: BR-02, AC-02-02, F-01 backfill) **[HARUS DIPERTAHANKAN — MF-01]** `action_open_stock_history()` menghitung `companies` (`','.join(self.env.companies.ids)`), lalu memanggil `stock.history.view.recreate_view(self.id, companies)` yang DROP lalu CREATE ULANG SQL view fisik `stock_history_view` — nama GLOBAL satu untuk seluruh database, di-scope ke satu `product_template_id`+`companies` lewat f-string SQL langsung. Tanpa locking. Dua klik berdekatan (user/produk berbeda) berpotensi race condition.
- `[BSL-003]` `[MATCH]` (ref: BR-01, catatan) `self.id` dipakai tanpa `self.ensure_one()` — aman dari tombol form single-record; error `ValueError` generik kalau dipanggil multi-record.

## 5. Server-Side Logic dengan Side Effect

### stock.history.view.recreate_view()
- `[BSL-004]` `[MATCH]` (ref: BR-03, AC-03-01, AC-03-02, F-02 backfill) **[HARUS DIPERTAHANKAN — MF-02]** Satu `stock.move` (`state='done'`) dihitung `income` bila `location_dest_id.usage='internal'` dan `outcome` bila `location_id.usage='internal'` — independen. Internal→internal tercatat sebagai keduanya. `qty` net tetap benar. Quantity diambil dari `SUM(stock_move_line.quantity)` per move; tanggal = `MIN(stock_move_line.date)` per move.
- `[BSL-005]` `[MATCH]` (ref: BR-04, AC-02-01) Baris paling awal = SATU baris agregat saldo pembuka (semua income/outcome dengan tanggal `<= date_trunc('MONTH', CURRENT_DATE - INTERVAL '1.1 year')`), supaya `qty` running sum mencerminkan kumulatif sejak awal riwayat. Deret tanggal = akhir bulan dari ~13.2 bulan lalu s/d akhir bulan berjalan (`generate_series(...) - 1 day`). Filter tampil ke user 12 bulan (Python).
- `[BSL-006]` `[MATCH]` (ref: BR-05, AC-04-01) Subquery `stock_move_line` dan CTE utama sama-sama difilter `company_id IN (companies)` — move company lain tidak ikut. Produk diambil hanya bila `product_template.active IS TRUE`.
- `[BSL-007]` `[MATCH]` (ref: BR-06, AC-05-01, F-04 backfill) **[HARUS DIPERTAHANKAN — MF-03]** ACL `access_stock_history_view` (`security/ir.model.access.csv`) memberi read/write/create/unlink = 1,1,1,1 TANPA `group_id`. Di 19.0 baris ACL tanpa grup berlaku untuk **semua user** (internal, portal, public — semantik `ir.model.access` global). Dikonfirmasi test: user internal tanpa `stock.group_stock_user` bisa search/read.
- `[BSL-008]` `[MATCH]` (ref: BR-06, AC-05-02) `create()` langsung ke `stock.history.view` gagal di level database (VIEW Postgres tanpa `INSTEAD OF` trigger), bukan diblokir ACL.

## 6. Client-Side Behavior (Views, JS, Owl)

### Backend
- Form `product.template`: tambah satu stat button (`views/views.xml`, inherit `stock.product_template_form_view_procurement_button`, `position="after"` terhadap `<button name="action_view_stock_move_lines">`). Lihat BSL-013.
- `views/stock_history_view.xml`: search/pivot/graph/list untuk `stock.history.view` + 2 action dead code. Lihat BSL-012, BSL-010.
- Tidak ada Owl/JS aplikatif, tidak ada controller aktif. 1 tour test (`static/tests/tours/stock_history_tour.js`, `web.assets_tests`).

### Public/Frontend
- N/A.

## 7. Dependency Eksternal

### Eksplisit (manifest)
- `depends: ['base', 'stock']`

### Implisit/Inferred
- Tidak ada runtime check. Kolom SQL yang dipakai langsung (bypass ORM): `stock_move(id, product_id, state, location_id, location_dest_id, company_id)`, `stock_move_line(move_id, product_id, quantity, date, company_id)`, `stock_location(id, usage)`, `product_product(id, product_tmpl_id)`, `product_template(id, active, uom_id, categ_id)`.
- Lingkungan deploy kemungkinan Enterprise (jawaban dev 2026-09-24) — tidak mengubah behavior modul di 19.0 (tidak ada kode yang bercabang soal Enterprise).

## 8. Quirk / Behavior Non-Obvious

- `[BSL-009]` `[MATCH]` (ref: F-09 backfill) **[HARUS DIPERTAHANKAN — MF-04]** `recreate_view()` DROP+CREATE VIEW via SQL mentah, bypass invalidasi cache ORM — pemanggilan berulang dalam satu environment bisa menyajikan data basi. Aman di alur normal (request baru per klik).
- `[BSL-010]` `[MATCH]` (ref: Observasi Tambahan 01A) Dua `ir.actions.act_window` (`action_stock_history_graph2`, `action_stock_history_tree2`) dead code — tidak dirujuk menu/tombol manapun.
- `[BSL-011]` `[MATCH]` (ref: —, observasi 17→18) Import `from odoo.http import request` tidak dipakai di kedua file model — dead import. `controllers/` di-import tapi kosong.
- `[BSL-012]` `[NO-SPEC]` (ref: 01A "Yang Termasuk", tidak dirinci; AC-01-03 project 18→19) Konfigurasi view `stock.history.view`: **search** — field `date` + 4 filter group-by statis dalam `<group>` tanpa atribut: "By products" (`product_template_id`), "Date" (`date`), "Category" (`categ_id`), "UOM" (`uom_id`); **pivot** — kolom `date` interval month, measure Input/Output/"Stock Quantity UOM"; **graph** — tipe `bar`, `date` sebagai col, measure `qty` ("Quantity"); **list** — kolom date, product_template_id, categ_id, uom_id, income, outcome, qty. Graph jadi view pertama yang terbuka (urutan `view_mode`).
- `[BSL-013]` `[NO-SPEC]` (ref: BR-01, tampilan tidak dirinci) Tampilan stat button: `string="Stock History"`, `type="object"`, `name="action_open_stock_history"`, `class="oe_stat_button"`, `icon="fa-signal"` (ikon bar sinyal Font Awesome), tanpa `groups` sendiri — tapi berada di dalam blok `<t groups="stock.group_stock_user">` milik tombol anchor native, sehingga hanya terlihat bagi user Inventory. Di 19.0 tampil langsung di button box (tidak collapse ke menu "More", lihat DIFF-16 project 18→19).
- `[BSL-014]` `[NO-SPEC]` (ref: —) Label & presisi field view SQL: income "Input", outcome "Output", qty "Stock Quantity uom" (label field Python; pivot menimpa jadi "Stock Quantity UOM", graph jadi "Quantity"), ketiganya `digits=(8, 6)`. Model tanpa `_description` → Odoo mencatat warning "The model stock.history.view has no _description" saat load (perilaku 19.0, tidak berdampak fungsional).
- `[BSL-015]` `[NO-SPEC]` (ref: —) Manifest: `version` `19.0.1.0.0`, `category` `Warehouse`, `license` `LGPL-3`, `application` False, `images` `['static/description/banner.png']` (di `migration/19.0`; branch rilis `19.0` sudah `['static/description/banner.gif', 'static/description/icon.png']` — lihat `01a` §5 keputusan port aset store).

---

## Cara Pakai

Lihat `migration-tool/templates/01b_BASELINE_SPEC.md` §Cara Pakai. `BSL-001`..`BSL-011` nomor dipertahankan sama lintas project 17→18, 18→19, 19→20; `BSL-012`..`BSL-015` baru di project ini.
