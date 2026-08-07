# Findings — product_history_report

> Satu file konsolidasi — pemilik modul cukup baca file ini untuk tahu semua hal yang butuh
> keputusan manusia. Diisi terus sepanjang proses Step 01→07.
>
> **Prinsip:** begitu ditemukan spot ambigu/bug, catat di sini dan LANJUT — jangan berhenti
> menunggu resolusi satu per satu.
>
> **Dokumen hidup:** kalau pemilik modul memperbaiki kode berdasarkan finding di sini, update
> entry terkait jadi `✅ RESOLVED` + tanggal + bukti test, jangan dihapus.

---

## Ringkasan

| ID | Judul | Tag | Prioritas |
|---|---|---|---|
| F-01 | SQL view global `stock_history_view` di-drop+recreate per klik, race condition antar user | `[PERLU-KEPUTUSAN]` | Tinggi |
| F-02 | Transfer internal→internal dihitung ganda di income DAN outcome | `[PERLU-KEPUTUSAN]` | Sedang |
| F-03 | `action_open_stock_history` tidak `ensure_one()` sebelum `self.id` | `[PERLU-KEPUTUSAN]` | Rendah |
| F-04 | ACL `stock.history.view` beri write/create/unlink=1 pada model SQL view (`_auto=False`) tanpa `group_id` | `[PERLU-KEPUTUSAN]` | Rendah |
| F-05 | Dua `ir.actions.act_window` (`*2`) tidak terhubung menu manapun — kemungkinan sisa dev | `[HASIL-BACA]` | Rendah |
| F-06 | Import `odoo.http.request` tidak terpakai di `stock_history_view.py` | `[HASIL-BACA]` | Rendah |
| F-07 | Verifikasi tabrakan nama method `action_open_stock_history` vs Odoo core belum bisa digrep (belum ada container hidup) | `[HASIL-BACA]` | — (limitasi tool, lihat §Limitasi) |

---

## Detail

### F-01 — SQL view global di-drop+recreate per klik, race condition antar user
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `product_history_report/models/stock_history_view.py:24-26`, dipanggil dari `product_history_report/models/product_template.py:19`
**Ref:** BR-02, AC-02-02
**Deskripsi:** `recreate_view()` memanggil `tools.drop_view_if_exists(self._cr, 'stock_history_view')`
lalu `CREATE VIEW stock_history_view AS (...)` dengan filter `product_template_id`/`companies`
di-hardcode ke dalam SQL lewat f-string. Nama view (`stock_history_view`) GLOBAL — satu nama untuk
seluruh instance Odoo, dipakai bergantian oleh setiap klik tombol dari user manapun. Tidak ada
locking/isolasi transaksi eksplisit di sekitar drop+create+select.
**Dampak:** Kalau dua request (dua user, atau satu user klik dua kali cepat untuk produk berbeda)
tumpang tindih waktu eksekusinya, kemungkinan konkret: (a) user A membaca hasil `SELECT` yang
sebenarnya sudah di-scope ke produk milik user B (kalau `CREATE VIEW` B selesai sebelum `SELECT` A
jalan), (b) error transient "relation stock_history_view does not exist" kalau `SELECT` menyentuh
window waktu tepat setelah `DROP` tapi sebelum `CREATE` selesai. Risiko meningkat sebanding jumlah
user concurrent yang memakai fitur ini bersamaan.
**Rekomendasi:** opsional, bukan keputusan BACKFILL — kandidat: scope view per session/company ke
nama unik (mis. sertakan `self._cr.dbname`+txn id atau ganti pendekatan jadi query langsung tanpa
view fisik/pakai temp table per transaksi), atau serialize akses lewat advisory lock.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-02 — Transfer internal→internal dihitung ganda di income DAN outcome
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `product_history_report/models/stock_history_view.py:29-33`
**Ref:** BR-03, AC-03-02
**Deskripsi:** `income` = 1 kalau `location_dest_id.usage = 'internal'`, `outcome` = 1 kalau
`location_id.usage = 'internal'` — dievaluasi independen per baris move, bukan mutually exclusive.
Move internal→internal (mis. antar rak/lokasi dalam warehouse yang sama-sama `internal`) memenuhi
KEDUA kondisi sekaligus.
**Dampak:** Kolom `income`/`outcome` bulanan menghitung SEMUA aktivitas gudang (termasuk transfer
internal yang secara neto tidak menambah/mengurangi stok), bukan murni "barang masuk dari luar" vs
"barang keluar ke luar". `qty` (net, lewat running sum) tetap benar karena income-outcome saling
meniadakan untuk move jenis ini — tapi kalau tujuan laporan adalah mengukur throughput
in/out gudang murni (mis. untuk purchasing/sales decision), angka ini bisa disalahartikan lebih
tinggi dari aktivitas eksternal sebenarnya.
**Rekomendasi:** opsional — tambah kondisi eksplisit exclude kalau `sl_dest.usage = 'internal' AND
sl_src.usage = 'internal'` dari kedua kolom, KALAU memang dimaksudkan hanya throughput eksternal.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-03 — `action_open_stock_history` tidak `ensure_one()` sebelum `self.id`
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `product_history_report/models/product_template.py:13-19`
**Ref:** BR-01
**Deskripsi:** Method memanggil `self.id` langsung tanpa `self.ensure_one()`. Selama dipanggil dari
tombol statistik form view (context single-record baku Odoo), ini aman. Kalau suatu saat dipanggil
dari konteks lain (server action massal, list-view multi-select, dsb.) yang mengirim recordset
>1 record, `self.id` pada multi-record recordset akan melempar `ValueError` bawaan ORM
("Expected singleton") — pesan generik, bukan pesan error yang ramah user.
**Dampak:** Rendah selama tetap dipakai sebagai tombol statistik form single-record saja (satu-
satunya cara pakai yang teramati di kode).
**Rekomendasi:** opsional — tambah `self.ensure_one()` di awal method untuk pesan error lebih jelas
kalau suatu saat dipanggil dari konteks lain.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-04 — ACL `stock.history.view` beri write/create/unlink=1 tanpa `group_id`, pada model SQL view
**Tag:** `[PERLU-KEPUTUSAN]`
**Lokasi:** `product_history_report/security/ir.model.access.csv:2`
**Ref:** BR-06, AC-05-01, AC-05-02
**Deskripsi:** `access_stock_history_view` memberi `perm_read,perm_write,perm_create,perm_unlink =
1,1,1,1`, kolom `group_id` KOSONG (berlaku semua user dengan akses model apapun, tidak dibatasi
grup Inventory/dsb.). Model ini `_auto=False` (SQL view, bukan tabel Odoo biasa).
**Dampak:** (a) VISIBILITAS: `read` terbuka untuk semua user internal, bukan hanya yang punya hak
lihat data stok — ini yang paling relevan secara bisnis, karena data pergerakan stok/quantity
bocor ke user yang mungkin seharusnya tidak berhak (mis. HR/Sales tanpa akses Inventory). (b)
WRITE/CREATE/UNLINK: kemungkinan besar tidak berefek nyata karena Postgres VIEW tanpa `INSTEAD OF`
trigger menolak DML langsung — TAPI ini belum dikonfirmasi eksekusi nyata (lihat AC-05-02, akan
diverifikasi Step 04).
**Rekomendasi:** opsional — pertimbangkan batasi `group_id` ke grup Inventory (mis.
`stock.group_stock_user`) kalau visibilitas data stok memang dimaksud terbatas.
**Keputusan pemilik modul:** *(kosong — diisi manusia)*

---

### F-05 — Dua `ir.actions.act_window` tidak terhubung menu manapun
**Tag:** `[HASIL-BACA]`
**Lokasi:** `product_history_report/views/stock_history_view.xml:63-74`
**Deskripsi:** `action_stock_history_graph2` dan `action_stock_history_tree2` didefinisikan tapi
tidak ada `<menuitem>` di modul ini yang mereferensikannya, dan tombol Stock History (satu-satunya
entry point aktif) membuat action window-nya sendiri secara dinamis dari Python
(`product_template.py:24-32`), tidak memakai action XML ini. Kemungkinan sisa iterasi
development/debug yang tidak dibersihkan.
**Dampak:** Tidak ada dampak fungsional (dead code, bukan bug aktif) — cuma clutter database
(`ir.actions.act_window` yang tidak pernah dipakai).
**Keputusan pemilik modul:** *(kosong — diisi manusia, opsional dihapus atau dibiarkan)*

---

### F-06 — Import `odoo.http.request` tidak terpakai
**Tag:** `[HASIL-BACA]`
**Lokasi:** `product_history_report/models/product_template.py:3`, `product_history_report/models/stock_history_view.py:3`
**Deskripsi:** Kedua file model meng-import `from odoo.http import request` tapi tidak pernah
memakai `request` di isi file. Dead import, tidak berefek fungsional.
**Keputusan pemilik modul:** *(kosong — diisi manusia, opsional dibersihkan)*

---

## Limitasi Tool

- **F-07 — Cek tabrakan nama method vs Odoo core belum diverifikasi lewat grep source nyata.**
  Step 01 ditulis sebelum container Mode B/C (Step 04) hidup, jadi tidak ada checkout Odoo
  core/image Docker ter-connect untuk `grep -rn "def action_open_stock_history"`. Nama method
  dinilai unik/spesifik modul ini (menyebut konsep "stock_history" yang modul ini perkenalkan
  sendiri), risiko dinilai rendah secara `[HASIL-BACA]` — TAPI belum dikonfirmasi definitif.
  **WAJIB re-cek begitu container Step 04 hidup** sebelum finding ini dianggap tuntas.
