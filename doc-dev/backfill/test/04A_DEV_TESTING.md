# Dev Testing — product_history_report

**Step:** 04 — Developer Testing (backfill)
**Module:** `product_history_report`
**Spec ref:** `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`
**Last Updated:** 2026-08-07

---

## 1. Smoke Test (happy path)

### Cara Eksekusi

**Mode C** — AI (Claude Code CLI) menjalankan langsung lewat `docker-env/` (`docker compose up`,
Odoo 17.0 + Postgres 15, `--test-enable --test-tags=/product_history_report`), membaca
`docker-env/logs/odoo.log` sendiri, lalu `docker compose down` — bukan desk-review, bukan diserahkan
ke dev.

### Checklist

| # | Area/fitur | Happy path / edge case | Cara | Status |
|---|---|---|---|---|
| 1 | Tombol Stock History | Muncul di arch form produk | Mode C | ☑ Pass |
| 2 | Tombol Stock History | Klik → action window graph/pivot/tree domain benar | Mode C | ☑ Pass |
| 3 | Laporan qty | Running-sum termasuk saldo dari histori >13 bulan | Mode C | ☑ Pass |

---

## 2. Unit & Integration Test Specification

**File test:** `product_history_report/tests/test_product_history_report.py` (baru — modul belum
punya `tests/` sama sekali sebelum BACKFILL).

### 2a. `product.template.action_open_stock_history()`

#### TC-F-01 — Return value action window

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Integration | Panggil `action_open_stock_history()` pada produk manapun | `res_model='stock.history.view'`, `view_mode='graph,pivot,tree'`, key `domain` ada | `[HASIL-BACA]` |
| 02 | Integration | Baca arch form `product.template` | String `action_open_stock_history` muncul di arch (tombol ter-render) | `[HASIL-BACA]` |

### 2b. `stock.history.view.recreate_view()` — perhitungan income/outcome/qty

#### TC-SH-01 — Saldo awal dari histori >13 bulan (BR-04)

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Integration | Move masuk 100 unit >13 bulan lalu + 5 unit 10 hari lalu | Baris bulan terakhir jendela: `qty` (running-sum) = 105 | `[HASIL-BACA]` |

#### TC-SH-02 — Klasifikasi income/outcome berbasis lokasi (BR-03)

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Integration | Move customer→internal (return), 7 unit | `income=7`, `outcome=0` pada bulan itu | `[HASIL-BACA]` |
| 02 | Integration | Move internal→internal (transfer rak), 4 unit (setelah stok 20 unit masuk) | `income` DAN `outcome` KEDUANYA bertambah 4 pada bulan itu — **dikonfirmasi PERILAKU NYATA modul**, lihat `FINDINGS.md` F-02 | `[PERLU-KEPUTUSAN]` |

#### TC-SH-03 — Filter multi-company (BR-05)

| # | Tipe | Condition | Expected | Provenance |
|---|---|---|---|---|
| 01 | Integration | `recreate_view()` dengan `companies` = company asli | income tercatat (>0) | `[HASIL-BACA]` |
| 02 | Integration | `recreate_view()` dengan `companies` = id company yang tidak ada/tidak cocok | income = 0 (move company lain tidak ikut) — filter BEKERJA BENAR | `[HASIL-BACA]` |

### 2c. Edge Cases & Security

| # | Tipe | Kondisi | Expected | Provenance |
|---|---|---|---|---|
| 01 | Integration | User internal TANPA grup `stock.group_stock_user` search `stock.history.view` | `read` berhasil (ACL longgar, lihat `FINDINGS.md` F-04) — **dikonfirmasi PERILAKU NYATA** | `[HASIL-BACA]` |
| 02 | Integration | `create()` langsung ke `stock.history.view` (model SQL view, `_auto=False`) | Exception (gagal di level DB Postgres, tanpa `INSTEAD OF` trigger) — **dikonfirmasi PERILAKU NYATA** | `[HASIL-BACA]` |

### 2d. Test Matrix Summary

| Area | Unit | Integration | Provenance |
|---|---|---|---|
| Action window (product.template) | | ✓ (2 TC) | `[HASIL-BACA]` |
| Perhitungan income/outcome/qty (stock.history.view) | | ✓ (4 TC) | `[HASIL-BACA]`/`[PERLU-KEPUTUSAN]` |
| ACL & robustness | | ✓ (2 TC) | `[HASIL-BACA]` |

### 2e. Ringkasan

- Unit: 0 TC (tidak ada method yang murni logic tanpa `self.env`/ORM/SQL cursor — lihat
  `03B_TEST_PLAN.md`, tidak ada kandidat Mode D).
- Integration: 8 TC, **8/8 PASS** pada eksekusi real terakhir (`docker compose up`,
  `--test-enable --test-tags=/product_history_report`) — lihat §3 untuk log & lesson debugging.

### 2f. Override/Collision Check terhadap Odoo Core (WAJIB — ada method baru di model `_inherit`)

**Diverifikasi lewat grep NYATA ke source Odoo core** (`docker run --rm odoo:17.0 grep -rn "def action_open_stock_history" /usr/lib/python3/dist-packages/odoo/addons/`)
setelah image container tersedia di Step 04 — **0 match**, TIDAK ADA tabrakan nama. `FINDINGS.md`
F-07 (sebelumnya limitasi tool di Step 01) sekarang **RESOLVED**.

| # | Method | Model | Kelas yang mendefinisikan (`__mro__`) | Override total Odoo core? | Provenance |
|---|---|---|---|---|---|
| 01 | `action_open_stock_history` | `product.template` (`_inherit`) | Hanya `product_history_report.models.product_template` (grep core: 0 match) | ☐ Ya / ☑ Tidak (aman) | `[DIKONFIRMASI]` (grep source nyata, bukan dugaan) |

### 2g. Incoming Email

N/A — modul tidak override `message_process()`/`message_route()`, tidak punya `mail.alias` custom.

---

## 3. Eksekusi Nyata & Lesson Debugging (Mode C, CLI)

**Environment:** `docker-env/docker-compose.yml` (Odoo 17.0 + Postgres 15, image resmi, TANPA
Dockerfile custom — tidak butuh Chrome/Tour di Step 04). AI (Claude Code CLI) menjalankan
`docker compose up` di background, poll `docker-env/logs/odoo.log`, `docker compose down` setelah
selesai — sepenuhnya Mode C tanpa dev turun tangan.

**Hasil akhir:** `0 failed, 0 error(s) of 8 tests` — **8/8 PASS**.

**Riwayat debugging (5 iterasi sampai PASS penuh — dicatat supaya sesi BACKFILL berikutnya di
modul lain tidak mengulang siklus yang sama, lihat juga
`doc-dev-backfill/records/product_history_report/SUMMARY.md` untuk kandidat promosi ke
`knowledge/`):**

1. **Percobaan pertama** (`stock.move` dibuat lalu `_action_confirm()`→`_action_assign()`→set
   `move_line.quantity`→`_action_done()` LANGSUNG, tanpa `stock.picking`): semua test yang
   bergantung ke income/outcome/qty GAGAL (`0.0` alih-alih nilai yang diharapkan), 1 test
   (`test_ac_05_02`) ERROR (`TypeError` — `assertRaises` Odoo tidak menerima tuple exception,
   diperbaiki jadi `Exception` tunggal).
2. **Debug lapis 1** (log `move.state`/`move.move_line_ids.picked` via ORM tepat setelah
   `_action_done()`): tampak `state=done`, `picked=True` — TERLIHAT benar dari sisi ORM cache.
3. **Debug lapis 2** (query SQL MENTAH `SELECT ... FROM stock_move_line`/`stock_move` langsung,
   bypass ORM cache, DALAM transaksi test yang sama): **kontradiksi ditemukan** — kolom DB
   sebenarnya `stock_move.state = 'draft'` dan `stock_move_line.picked = False`, BUKAN `done`/`True`
   seperti yang ORM laporkan. Root cause: memanggil `_action_confirm()/_action_assign()/_action_done()`
   langsung pada `stock.move` TANPA `stock.picking.button_validate()` TIDAK benar-benar
   menuntaskan move di Odoo 17 — nilai ORM yang terbaca sesaat setelah `_action_done()` tidak
   mencerminkan apa yang benar-benar tersimpan di database.
4. **Fix:** ganti alur test jadi `stock.picking.create()` → `action_confirm()` → `action_assign()`
   → set `move_line.quantity` → **`picking.button_validate()`** (jalur resmi yang setara tombol
   "Validate" di UI Inventory) — 7 dari 8 test langsung PASS.
5. **Sisa 1 kegagalan** (`test_ac_04_01`, sanity-check company benar sempat PASS tapi assertion
   company-salah GAGAL dengan income tetap muncul): root cause KEDUA ditemukan — `recreate_view()`
   drop+create ulang tabel fisik `stock_history_view` lewat SQL mentah (bypass ORM), sehingga ORM
   `search()`/`read()` yang dipanggil DUA KALI dalam satu environment/transaksi yang sama bisa
   membaca cache lama (row `stock.history.view` punya PK deterministik `product_template_id`+
   `YYYYMMDD`, jadi id-nya PERSIS SAMA sebelum/sesudah `recreate_view()` kedua). Fix test:
   `self.env['stock.history.view'].invalidate_model()` sebelum `search()` kedua. **Ini murni
   artifact cara test memanggil `recreate_view()` dua kali di satu env** — TIDAK mensimulasikan bug
   produksi (setiap klik tombol di browser = request/environment baru) — TAPI mengonfirmasi lagi
   kerapuhan desain "SQL view fisik global" yang sudah dicatat di `FINDINGS.md` F-01 (kalau environment
   yang sama dipertahankan lintas panggilan — mis. `odoo shell` interaktif, server action berantai,
   RPC batch dari client yang menahan koneksi — staleness ini genuinely bisa terjadi juga di
   luar test).

**Kesimpulan:** setelah kedua fix di atas, seluruh 8 Integration TC PASS dengan DATA REAL (bukan
mock) — termasuk MENGKONFIRMASI dua `[PERLU-KEPUTUSAN]` di `FINDINGS.md` (F-02: transfer
internal→internal benar-benar dihitung ganda; F-04: user tanpa grup Inventory benar-benar bisa baca
data) sebagai perilaku NYATA, bukan cuma dugaan dari baca kode.
