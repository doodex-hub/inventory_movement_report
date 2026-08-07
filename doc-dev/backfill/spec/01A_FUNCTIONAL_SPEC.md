# Functional Spec — product_history_report

**Module:** `product_history_report`
**Odoo Version:** 17.0
**Depends:** base, stock
**Last Updated:** 2026-08-07
**Status:** Backfill retroaktif — dibaca dari kode existing, bukan requirement baru
**Provenance:** lihat `doc-dev-backfill/templates/CLAUDE_TEMPLATE.md` §Provenance Tag untuk arti `[HASIL-BACA]`/`[DIKONFIRMASI]`/`[PERLU-KEPUTUSAN]`

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **F-01 (Tinggi)** — SQL view `stock_history_view` bersifat GLOBAL (satu nama tabel view untuk
   semua user/produk), tapi isinya di-drop+recreate ulang tiap kali tombol "Stock History" diklik,
   di-scope ke SATU `product_template_id` + daftar company tertentu. Kalau dua user klik tombol ini
   ber-dekatan untuk produk yang beda, ada race condition: user A bisa membaca data produk B (atau
   error) tergantung timing `DROP`/`CREATE`/`SELECT`. Lihat BR-02, `FINDINGS.md` F-01.
2. **F-02 (Sedang)** — Perhitungan `income`/`outcome` menghitung transfer internal↔internal
   (source DAN destination sama-sama `usage='internal'`, mis. transfer antar lokasi dalam satu
   warehouse) sebagai `income` SEKALIGUS `outcome` pada tanggal yang sama — bukan diabaikan. Efek ke
   `qty` (net) tetap benar (saling meniadakan), tapi angka `income`/`outcome` per-bulan yang
   ditampilkan akan lebih besar dari sekadar stock masuk/keluar gudang murni. Belum jelas ini
   disengaja (mengukur "aktivitas gudang total") atau bug. Lihat BR-03, `FINDINGS.md` F-02.
3. **F-03 (Rendah)** — `action_open_stock_history` tidak memanggil `self.ensure_one()` sebelum
   `self.id` — kalau dipanggil dari konteks yang kebetulan multi-record (bukan stat-button biasa),
   akan error `ValueError` bawaan ORM, bukan pesan yang jelas untuk user. Lihat `FINDINGS.md` F-03.

---

## Latar Belakang & Tujuan

Modul ini menambah laporan riwayat pergerakan stok (~13 bulan terakhir, lihat BR-04) per produk,
diakses lewat tombol statistik "Stock History" di form `product.template`. Tujuannya membantu
melihat tren stok masuk/keluar/quantity bulanan tanpa perlu membuka Inventory Valuation/Stock Moves
mentah satu per satu. `[HASIL-BACA]`

---

## Scope

### Yang Termasuk (disimpulkan dari kode)

- Tombol statistik "Stock History" pada form `product.template` (setelah tombol
  "Stock Moves" bawaan `stock`). `[HASIL-BACA]`
- Model report `stock.history.view` (SQL view, `_auto=False`) berisi baris bulanan: tanggal
  (akhir bulan), income, outcome, quantity kumulatif, kategori produk, UoM. `[HASIL-BACA]`
- View list/pivot/graph untuk `stock.history.view`, plus dua `ir.actions.act_window` mandiri
  (`action_stock_history_graph2`, `action_stock_history_tree2`) yang TIDAK terhubung ke menu
  manapun di `views/*.xml` (tidak ada `<menuitem>` di modul ini). `[HASIL-BACA]`
- Filter multi-company: hanya menghitung `stock.move`/`stock.move.line` milik
  `self.env.companies.ids` (company yang aktif di sesi user). `[HASIL-BACA]`

### Yang Tidak Termasuk

Tidak ada indikasi eksplisit dari kode soal apa yang sengaja TIDAK dibuat — tidak ada TODO/comment
yang menyiratkan scope. Satu observasi: `controllers/controllers.py` isinya murni boilerplate
scaffold Odoo (`http.Controller` di-comment semua) — modul ini tidak expose route HTTP apapun,
kemungkinan sisa `odoo-bin scaffold` yang tidak dibersihkan, bukan fitur yang sengaja
dihilangkan. `[HASIL-BACA]`

---

## User Stories (rekonstruksi)

> Ditulis dari sudut pandang kode, bukan wawancara user asli.

### US-01 — Melihat riwayat stok satu produk
Sebagai user Inventory, saya ingin membuka form sebuah produk dan mengklik tombol "Stock History"
untuk melihat grafik/pivot/tree pergerakan stok (masuk, keluar, quantity) produk itu selama kurang
lebih setahun terakhir, supaya saya bisa menilai tren tanpa membuka laporan stock move mentah.
`[HASIL-BACA]`

---

## Business Rules

> **Cek wajib tabrakan nama method dengan Odoo core** (`doc-dev-backfill/ai-doc/PLAYBOOK.md`
> §"Cek tabrakan nama method dengan Odoo core"): method baru yang didefinisikan modul ini pada
> model `_inherit` (`product.template`) adalah `action_open_stock_history` — nama ini sangat
> spesifik/unik untuk modul ini (menyebut "stock_history", konsep yang modul ini sendiri
> perkenalkan). **Verifikasi grep langsung ke source Odoo core TIDAK bisa dilakukan** dari sesi ini
> (tidak ada checkout Odoo core/image Docker ter-connect saat Step 01 ditulis — baru tersedia nanti
> di Step 04 lewat container) — dicatat sebagai limitasi sementara, RE-VERIFIKASI begitu container
> Mode B/C hidup di Step 04 (`docker compose exec odoo grep -rn "def action_open_stock_history"
> /usr/lib/python3/dist-packages/odoo/addons/`). Risiko dinilai RENDAH berdasarkan keunikan nama,
> bukan nol. `[HASIL-BACA]`

### BR-01 — Tombol "Stock History" pada form produk
Form `product.template` (inherit `stock.product_template_form_view_procurement_button`) mendapat
tombol statistik baru "Stock History" (icon `fa-signal`), diletakkan setelah tombol
`action_view_stock_move_lines` bawaan `stock`. Klik tombol memanggil
`action_open_stock_history()`. `[HASIL-BACA]`
**Lokasi kode:** `product_history_report/views/views.xml:9-14`, `product_history_report/models/product_template.py:13`

### BR-02 — Rebuild SQL view per klik, di-scope ke satu produk + company aktif
`action_open_stock_history()` menghitung `date_debut` (12 bulan sebelum tanggal 1 bulan berjalan,
di sisi Python) dan `companies` (gabungan `self.env.companies.ids`, dipisah koma), lalu memanggil
`stock.history.view.recreate_view(self.id, companies)` yang **DROP lalu CREATE ULANG** SQL view
bernama `stock_history_view` (nama tabel fisik di database, satu-satunya, tidak per-user/per-sesi),
di-filter `WHERE ... pt.id = {product_template_id} AND ... company_id IN ({companies})` lewat
f-string SQL langsung (bukan parameterized query). Setelah view dibuat ulang, Odoo mem-`search()`
`stock.history.view` dengan domain `date >= date_debut` dan menampilkan hasilnya di action window
graph/pivot/tree. `[HASIL-BACA]`
**Lokasi kode:** `product_history_report/models/product_template.py:13-32`, `product_history_report/models/stock_history_view.py:24-110`
**Catatan risiko:** karena nama view GLOBAL dan proses DROP+CREATE+SELECT tidak atomik/tidak
di-lock, dua klik ber-dekatan (user berbeda, produk berbeda) berpotensi race condition — lihat
`FINDINGS.md` F-01. `product_template_id`/`companies` sendiri berasal dari `self.id`
(integer record id ORM) dan `self.env.companies.ids` (integer), BUKAN input string bebas dari
user — jadi risiko SQL injection klasik rendah, tapi pola f-string-ke-SQL tetap rapuh (lihat
`FINDINGS.md` F-01 juga mencakup ini sebagai code-quality note, bukan cuma race condition).

### BR-03 — Definisi income/outcome berbasis lokasi internal
Satu baris `stock.move` (state `done`) dihitung sebagai `income` kalau lokasi TUJUAN
(`location_dest_id`) usage-nya `internal`, dan sebagai `outcome` kalau lokasi ASAL
(`location_id`) usage-nya `internal`. Move internal→internal (transfer antar lokasi dalam
warehouse yang sama-sama `internal`) akan tercatat SEBAGAI KEDUANYA (income dan outcome) pada
tanggal yang sama — net ke `qty` tetap nol/benar (saling meniadakan di running sum), tapi angka
`income`/`outcome` mentah per bulan jadi lebih besar dari "stok masuk/keluar gudang murni".
`[HASIL-BACA]` — belum jelas disengaja atau bug, lihat `FINDINGS.md` F-02.
**Lokasi kode:** `product_history_report/models/stock_history_view.py:32-33`

### BR-04 — Window waktu 13.2 bulan dengan agregasi "saldo awal"
Baris paling awal di jendela ditampilkan adalah SATU baris agregat yang menjumlahkan SEMUA
`income`/`outcome` sebelum `date_trunc('MONTH', (CURRENT_DATE - INTERVAL '1.1 year'))` (kira-kira
13.2 bulan ke belakang) — bertindak sebagai "saldo pembuka" supaya kolom `qty` (running sum lewat
`SUM(...) OVER (PARTITION BY product_id ORDER BY date)`) tetap mencerminkan quantity kumulatif yang
benar sejak awal riwayat stok, bukan cuma kumulatif dari awal jendela 12 bulan. Sisi Python
(`date_debut`, pakai `relativedelta(months=12)` persis) dipakai HANYA untuk memfilter baris yang
ditampilkan ke user (`search([('date', '>=', date_debut)])`) — SQL sendiri tetap menghitung
lebih jauh ke belakang (1.1 tahun) untuk memastikan baris "saldo pembuka" itu benar. `[HASIL-BACA]`
**Lokasi kode:** `product_history_report/models/stock_history_view.py:51-74`, `product_history_report/models/product_template.py:14-22`

### BR-05 — Filter multi-company
Baik subquery `stock_move_line` (`sml.company_id`) maupun CTE utama (`sm.company_id`) difilter ke
`company_id IN (companies aktif user)` — konsisten dengan histori commit `improve multi company`
di repo ini. `[HASIL-BACA]`
**Lokasi kode:** `product_history_report/models/stock_history_view.py:40,48`

### BR-06 — Akses model `stock.history.view` terbuka untuk semua user internal
`ir.model.access.csv` memberi `perm_read/write/create/unlink = 1,1,1,1` pada
`access_stock_history_view` TANPA `group_id` (kolom kosong = berlaku untuk semua user yang punya
akses model, tidak dibatasi grup tertentu seperti Inventory User). Karena model ini `_auto=False`
(SQL view, bukan tabel biasa), `write`/`create`/`unlink` yang diizinkan di ACL kemungkinan besar
akan gagal di level database kalau benar-benar dicoba (Postgres VIEW tanpa `INSTEAD OF` trigger
tidak menerima INSERT/UPDATE/DELETE langsung) — jadi izin `1,1,1` untuk write/create/unlink secara
praktis tidak berefek nyata, tapi tetap longgar/tidak presisi sebagai definisi ACL. `[HASIL-BACA]`
**Lokasi kode:** `product_history_report/security/ir.model.access.csv:2`

---

## Observasi Tambahan (bukan Business Rule, tapi relevan)

- Dua `ir.actions.act_window` (`action_stock_history_graph2`, `action_stock_history_tree2`) di
  `views/stock_history_view.xml` tidak direferensikan `<menuitem>` apapun di modul ini — satu-satunya
  entry point yang benar-benar terpakai adalah tombol statistik `BR-01` (yang membuat action window
  secara dinamis lewat Python, bukan lewat action XML manapun di atas). Kedua action XML ini
  kemungkinan sisa development/debug. `[HASIL-BACA]`
- `stock_history_view.py` meng-import `from odoo.http import request` tapi tidak pernah
  memakainya — import mati. `[HASIL-BACA]`
