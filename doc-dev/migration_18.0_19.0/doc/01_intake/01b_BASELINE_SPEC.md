# Baseline Spec — product_history_report

**Step:** 1 — Intake & Scope (pelengkap `01a_MIGRATION_INTAKE.md`)
**Tujuan:** dokumentasikan APA yang modul lakukan (behavior as-is) di 18.0.
**Tanggal:** 2026-08-26
**Sumber:** Direkonsiliasi dari `doc-dev/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md` (hasil project migrasi 17.0→18.0 SEBELUMNYA, sudah SELESAI + lulus UAT 2026-08-24) + cross-check langsung ke kode `source-codebase`/`target-codebase` saat ini (identik, sama-sama commit `978a384` — tidak ada drift).

---

## Ringkasan untuk Review — Perlu Konfirmasi User

Tally provenance: 11 klaim `[MATCH]` (semua diwarisi dari `01b_BASELINE_SPEC.md` 17→18, yang sendiri sudah 100% `[MATCH]` terhadap spec `doc-dev-backfill` asli), 0 `[GAP]`, 0 `[NO-SPEC]`. Cross-check ulang di sesi ini: seluruh `BSL-001`..`BSL-011` dikonfirmasi masih cocok dengan kode `models/product_template.py` dan `models/stock_history_view.py` saat ini — tidak ada perubahan kode antara commit `978a384` (akhir project 17→18) dan sekarang.

1. **BSL-002 (Tinggi, harus DIPERTAHANKAN)** — SQL view global `stock_history_view` di-drop+recreate setiap klik tombol, tanpa locking. Race condition antar user nyata secara teori. Jangan diperbaiki saat migrasi kecuali dev eksplisit minta — lihat `FINDINGS.md` MF-01.
2. **BSL-004 (Sedang, harus DIPERTAHANKAN, dikonfirmasi test eksekusi nyata)** — transfer stok internal→internal dihitung sebagai income DAN outcome sekaligus, bukan mutually exclusive. `qty` net tetap benar. Lihat `FINDINGS.md` MF-02.
3. **BSL-007 (Rendah, harus DIPERTAHANKAN, dikonfirmasi test eksekusi nyata)** — ACL `stock.history.view` tidak membatasi grup — semua user internal bisa baca data pergerakan stok apapun grupnya. Lihat `FINDINGS.md` MF-03.
4. **BSL-009 (Rendah, harus DIPERTAHANKAN)** — `recreate_view()` (SQL mentah, bypass ORM) rawan ORM cache stale kalau dipanggil >1x dalam environment yang sama. Lihat `FINDINGS.md` MF-04.
5. Modul murni backend: satu model regular (`product.template`, extend) + satu SQL view (`stock.history.view`, `_auto=False`) + 2 file view XML statis + 1 baris ACL. Tidak ada JS/Owl/controller aktif — kecuali 1 test tour (`static/tests/tours/stock_history_tour.js`, ditambahkan Step 9 project 17→18, bukan kode aplikatif).
6. Window waktu laporan: filter tampilan 12 bulan (Python), tapi SQL menghitung 13.2 bulan ke belakang untuk baris "saldo pembuka" — detail ini penting dipertahankan persis di 19.0, jangan disederhanakan jadi 12 bulan murni.
7. **Beda dari baseline 17→18:** view XML sudah pakai `<list>` (bukan `<tree>`) — sudah difix di migrasi 17→18, bukan lagi item kerja untuk project ini. `action_open_stock_history()` sudah `view_mode: 'graph,pivot,list'`.

---

## 1. Tujuan Modul

Modul menambah laporan riwayat pergerakan stok bulanan (~13 bulan terakhir) per produk, diakses lewat tombol statistik "Stock History" pada form `product.template`. Tujuannya membantu user melihat tren stok masuk/keluar/quantity kumulatif tanpa membuka Stock Moves/Inventory Valuation mentah satu per satu.

## 2. Model & Tanggung Jawab

| Model | Tanggung Jawab |
|---|---|
| `product.template` (extend) | Menambah method `action_open_stock_history()` + tombol statistik pemicunya |
| `stock.history.view` (baru, `_auto=False`, SQL view) | Baris laporan bulanan: tanggal (akhir bulan), income, outcome, quantity kumulatif, kategori produk, UoM — per `product_template_id` |

## 3. Field dengan Makna Bisnis

### stock.history.view
- **Identitas:** `date` (akhir bulan, atau baris agregat "saldo pembuka"), `product_template_id`, `categ_id`, `uom_id`
- **Struktur:** `income` (qty masuk bulan itu), `outcome` (qty keluar bulan itu), `qty` (running sum kumulatif via window function `SUM(...) OVER (PARTITION BY product_id ORDER BY date)`)
- **Desain:** `_auto=False`, isi tabel = hasil `CREATE VIEW` SQL mentah, dibuat ulang tiap kali dibutuhkan (bukan materialized/persistent antar klik)

## 4. Business Workflow / State Transition

### Tombol Stock History (form produk)
- `[BSL-001]` `[MATCH]` Form `product.template` mendapat tombol statistik "Stock History" (icon `fa-signal`), diletakkan setelah tombol `action_view_stock_move_lines` bawaan `stock`. Klik memanggil `action_open_stock_history()`, yang membuka window action (judul "Stocks Histories", `view_mode` `graph,pivot,list`) berisi baris `stock.history.view` untuk produk itu, `date >= date_debut` (12 bulan sebelum awal bulan berjalan).
- `[BSL-002]` `[MATCH]` **[HARUS DIPERTAHANKAN, lihat FINDINGS.md MF-01]** `action_open_stock_history()` menghitung `date_debut` + `companies` (gabungan `self.env.companies.ids`), lalu memanggil `stock.history.view.recreate_view(self.id, companies)` yang **DROP lalu CREATE ULANG** SQL view fisik bernama `stock_history_view` — nama GLOBAL, satu untuk seluruh instance, di-scope ke satu `product_template_id`+`companies` lewat f-string SQL langsung. Tidak ada locking/isolasi transaksi. Dua klik ber-dekatan (user berbeda, produk berbeda) berpotensi race condition: user A bisa membaca data produk B, atau error transient "relation does not exist".
- `[BSL-003]` `[MATCH]` `self.id` dipanggil tanpa `self.ensure_one()` — aman selama dipanggil dari tombol form single-record (satu-satunya cara pakai yang teramati), tapi akan error `ValueError` generik kalau dipanggil dari konteks multi-record.

## 5. Server-Side Logic dengan Side Effect

### stock.history.view.recreate_view()
- `[BSL-004]` `[MATCH]` **[HARUS DIPERTAHANKAN, lihat FINDINGS.md MF-02, dikonfirmasi test eksekusi nyata]** Satu baris `stock.move` (state `done`) dihitung `income` kalau `location_dest_id.usage='internal'`, dan `outcome` kalau `location_id.usage='internal'` — dievaluasi independen, bukan mutually exclusive. Move internal→internal (source DAN dest sama-sama `internal`) tercatat sebagai KEDUANYA pada tanggal yang sama. `qty` (net, running sum) tetap benar karena saling meniadakan, tapi `income`/`outcome` mentah per bulan jadi lebih besar dari "stok masuk/keluar gudang murni".
- `[BSL-005]` `[MATCH]` Baris paling awal jendela adalah SATU baris agregat "saldo pembuka" — menjumlahkan SEMUA income/outcome sebelum `date_trunc('MONTH', CURRENT_DATE - INTERVAL '1.1 year')` (~13.2 bulan ke belakang), supaya `qty` (running sum) mencerminkan kumulatif sejak awal riwayat stok, bukan cuma dari awal jendela tampil 12 bulan. Filter tampil ke user tetap 12 bulan (`relativedelta(months=12)`, sisi Python) — SQL sendiri menghitung lebih jauh untuk memastikan baris saldo pembuka benar.
- `[BSL-006]` `[MATCH]` Baik subquery `stock_move_line` maupun CTE utama difilter `company_id IN (companies aktif user)` — move dari company lain (yang tidak aktif di sesi user) tidak ikut dihitung.
- `[BSL-007]` `[MATCH]` **[HARUS DIPERTAHANKAN, lihat FINDINGS.md MF-03, dikonfirmasi test eksekusi nyata]** `ir.model.access.csv` memberi `perm_read/write/create/unlink=1,1,1,1` pada `access_stock_history_view` TANPA `group_id` — berlaku semua user internal manapun, tidak dibatasi grup Inventory. `read` benar-benar terbuka (dikonfirmasi test: user tanpa `stock.group_stock_user` berhasil baca).
- `[BSL-008]` `[MATCH]` `create()` langsung ke `stock.history.view` GAGAL di level database (Postgres VIEW tanpa `INSTEAD OF` trigger menolak DML) — dikonfirmasi test eksekusi nyata, bukan diblokir ACL (yang justru mengizinkan secara nominal).

## 6. Client-Side Behavior (Views, JS, Owl)

### Backend
- Form view `product.template`: tambah tombol statistik saja (`views/views.xml`), tidak ada widget custom.
- `views/stock_history_view.xml`: view list/pivot/graph untuk `stock.history.view` (sudah `<list>`, bukan `<tree>` — fix dari migrasi 17→18), plus filter groupby statis (by product, date, category, UoM — `domain="[]"`, `context` group_by saja, bukan dinamis). Dua `ir.actions.act_window` (`action_stock_history_graph2`, `action_stock_history_tree2`) di file ini TIDAK terhubung `<menuitem>` manapun dan TIDAK dipakai tombol Stock History (yang membuat action window-nya sendiri secara dinamis dari Python) — dead/unused XML, bukan bug aktif.
- Tidak ada komponen Owl/JavaScript custom aplikatif, tidak ada RPC route/controller aktif (`controllers/controllers.py` murni boilerplate scaffold, di-comment semua). Ada 1 file test tour (`static/tests/tours/stock_history_tour.js`, key manifest `web.assets_tests`) — hasil kerja Step 9 project 17→18 (`HttpCase.start_tour`), bukan bagian business logic, tapi perlu dicek ulang kompatibilitasnya dengan API tour Odoo 19.0 di Step 9 project ini.

### Public/Frontend
- N/A — modul ini murni backend Inventory, tidak ada widget publik.

## 7. Dependency Eksternal

### Eksplisit (manifest)
- `depends: ['base', 'stock']`

### Implisit/Inferred
- Tidak ditemukan dependency implisit (tidak ada runtime check `'x' in self.env` ke modul lain).

## 8. Quirk / Behavior Non-Obvious

- `[BSL-009]` `[MATCH]` **[HARUS DIPERTAHANKAN kecuali dev minta fix, lihat FINDINGS.md MF-04]** `recreate_view()` melakukan DROP+CREATE VIEW lewat SQL mentah (bypass ORM cache invalidation). Kalau dipanggil >1x dalam SATU environment/transaksi yang bertahan lama (mis. `odoo shell`, server action batch, RPC yang menahan koneksi) — ORM `search()`/`read()` berikutnya bisa menyajikan field value dari cache lama (data basi, silent, tanpa error). Di alur produksi normal (klik tombol = request/environment baru tiap kali) tidak bermasalah.
- `[BSL-010]` `[MATCH]` Dua `ir.actions.act_window` di `views/stock_history_view.xml` (`*2`) adalah dead code — tidak direferensikan `<menuitem>` apapun, tidak dipakai jalur aktif manapun. Kemungkinan sisa development, tidak berdampak fungsional.
- `[BSL-011]` `[MATCH]` Import `from odoo.http import request` di `product_template.py` dan `stock_history_view.py` tidak pernah dipakai — dead import, tidak berdampak fungsional. Aman dibersihkan saat migrasi (bukan business logic).

---

## Cara Pakai

Lihat `migration-tool/templates/01b_BASELINE_SPEC.md` §Cara Pakai untuk aturan lengkap penomoran `BSL-NNN` dan provenance. Semua `BSL-NNN` di sini merujuk balik ke `01b_BASELINE_SPEC.md` project 17.0→18.0 (yang sendiri merujuk ke `BR-NN`/`AC-NN-NN` di `doc-dev/backfill/spec/` dan `F-NN` di `doc-dev/backfill/FINDINGS.md`) — jangan buat ID baru untuk klaim yang sudah punya `BSL-NNN` di sini, nomor dipertahankan sama lintas project supaya rujukan silang tidak ambigu.
