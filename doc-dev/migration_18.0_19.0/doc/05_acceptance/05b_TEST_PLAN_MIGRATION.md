# Test Plan (Migrasi) — product_history_report

**Step:** 5 — Acceptance Criteria & Test Plan (satu paket dengan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-26

---

## Step 9 — Dev Testing

> Eksekusi: `odoo-bin -i product_history_report --test-enable --test-tags /product_history_report --stop-after-init` di container Odoo 19.0. Modul punya 1 Tour test (`static/tests/tours/stock_history_tour.js` + `tests/test_stock_history_tour.py`, ditambahkan Step 9 project 17→18 lewat `HttpCase.start_tour`) — WAJIB dijalankan juga, bukan cuma integration test backend.

**Audit kesiapan test (9a, dilakukan sekarang bukan asumsi):** `tests/test_product_history_report.py` dibawa apa adanya dari `source-codebase` (hasil project 17→18, sudah lulus 8/8 di 18.0), 8 method test, SEMUA berisi logika assertion nyata (bukan stub docstring) — dikonfirmasi baca isi tiap method langsung (bukan sekadar `grep -c "def test_"`). 7/8 dijalankan tanpa modifikasi; 1/8 (`test_ac_05_01_read_open_for_user_without_inventory_group`) WAJIB diupdate 1 baris (`groups_id`→`group_ids`, `03_MIGRATION_SPEC.md` DIFF-02) — kalau tidak diupdate, test itu akan FAIL karena field-nya sendiri sudah di-rename di 19.0, bukan karena kode migrasi salah. `tests/test_stock_history_tour.py` (1 method) tidak butuh modifikasi terdeteksi dari review statis.

**Item kontinjensi WAJIB dicek PERTAMA saat G1 (`03_MIGRATION_SPEC.md` DIFF-10, belum pasti gagal/tidak):** `setUpClass`/`_picking_type_for()` resolve `env.ref('stock.stock_location_stock'/'_customers'/'_suppliers', 'stock.picking_type_in'/'_out'/'_internal')` — SEMUA 6 method test yang memanggil `_make_move()` (AC-02-01, AC-02-02 N/A, AC-03-01, AC-03-02, AC-04-01, AC-05-01) bergantung pada `setUpClass` ini lolos. Kalau G1 menunjukkan `env.ref()` gagal resolve, ini jadi blocker baru yang harus difix SEBELUM lanjut test manapun — dokumentasikan hasilnya (gagal/tidak) di `09_DEV_TESTING.md`, JANGAN diasumsikan aman dari dokumen ini semata.

| AC | Deskripsi | Unit | Integration | Tour (Owl/JS) |
|---|---|---|---|---|
| AC-01-01 | Tombol Stock History ada di arch form | — | `test_ac_01_01_button_present_in_form_arch` | Tercakup juga lewat `stock_history_tour` (klik nyata) |
| AC-01-02 | Klik tombol → action window benar | — | `test_ac_01_02_action_open_stock_history_returns_expected_action` (tidak butuh update — `view_mode` sudah `graph,pivot,list` sejak 18.0) | Tercakup juga lewat `stock_history_tour` |
| AC-01-03 | Search panel groupby tetap berfungsi pasca hapus atribut `<group>` | — | Tidak ada test otomatis existing untuk ini — **WAJIB dicek manual/AI-interaktif di Step 10** (klik dropdown filter, verifikasi 4 opsi groupby masih ada & berfungsi) | Opsional — bisa ditambah ke tour kalau mau, tidak wajib |
| AC-02-01 | qty running-sum mencakup saldo >13 bulan | — | `test_ac_02_01_qty_includes_pre_window_balance` (bergantung fix DIFF-10 kalau ternyata gagal) | N/A |
| AC-02-02 | Race condition SQL view global (tetap ada, tidak ditest otomatis — sifat race condition tidak deterministik) | — | — (tidak ada test — konsisten dengan status 18.0) | N/A |
| AC-03-01 | Move customer→internal = income saja | — | `test_ac_03_01_customer_return_is_income_only` (bergantung DIFF-10) | N/A |
| AC-03-02 | Move internal→internal = income DAN outcome (double-count dipertahankan) | — | `test_ac_03_02_internal_transfer_counted_as_both_income_and_outcome` (bergantung DIFF-10) | N/A |
| AC-04-01 | Filter multi-company | — | `test_ac_04_01_company_filter_excludes_other_company` (bergantung DIFF-10) | N/A |
| AC-05-01 | Read terbuka tanpa grup Inventory | — | `test_ac_05_01_read_open_for_user_without_inventory_group` (**wajib update**: `groups_id`→`group_ids`, DIFF-02; juga bergantung DIFF-10 untuk setup datanya) | N/A |
| AC-05-02 | create/write/unlink ke view gagal di DB | — | `test_ac_05_02_create_on_view_fails` (tidak bergantung DIFF-10 — tidak butuh `_make_move()`) | N/A |

## Step 10 — QA Testing

> Modul backend murni tanpa UI kompleks (1 tombol + 1 window action graph/pivot/list) — cukup **Manual** per AC, tidak perlu AI+tool eksternal. AC-01-03 (BARU, dipicu DIFF-01) butuh sedikit perhatian ekstra karena tidak tercakup test otomatis.

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal (ref script) |
|---|---|---|---|---|
| AC-01-01, AC-01-02 | Klik tombol Stock History di form produk, verifikasi window `graph,pivot,list` terbuka dengan judul "Stocks Histories" | ✅ (dev/QA klik langsung di instance 19.0) | Opsional (Claude in Chrome kalau tersedia) | — |
| AC-01-03 | Buka dropdown filter di window Stocks Histories, verifikasi 4 opsi groupby (product/date/category/UOM) masih ada & berfungsi meski label "Group By" mungkin hilang | ✅ (WAJIB — satu-satunya jalur verifikasi, tidak ada test otomatis) | Opsional | — |
| AC-02-01, AC-02-02, AC-03-01, AC-03-02, AC-04-01, AC-05-01, AC-05-02 | Sudah tercakup penuh oleh Integration test Step 9 (butuh data setup programatik) | — (cukup Step 9) | — | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Laporan riwayat stok per produk | AC-01-01, AC-01-02, AC-01-03, AC-02-01, AC-04-01 | Business user Inventory buka form produk apapun yang punya histori stok, klik "Stock History", verifikasi grafik/pivot/list tampil, filter groupby masih bisa dipakai, dan angkanya masuk akal dibanding Stock Moves bawaan |
| Bug/quirk yang dipertahankan (tidak untuk "lulus/gagal" — cukup dikonfirmasi paham) | AC-02-02, AC-03-02, AC-05-01 | Business user/PM diberi tahu eksplisit: race condition SQL view, double-count transfer internal, dan ACL terbuka semua user internal — SEMUA ini SUDAH ADA sejak 17.0/18.0, bukan regresi baru dari migrasi 19.0 |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Integration (9 test — 8 existing + 1 Tour, 1 wajib update 1 baris) | Otomatis/background | 10 AC (AC-02-02 tidak ada test otomatis by design, AC-01-03 tidak ada test otomatis — didorong ke Step 10) |
| 10 | QA | Manual | Manual, dua skenario (fitur utama + groupby DIFF-01) + spot-check | 10 AC (8 sudah tercakup Step 9, 2 manual klik) |
| 11 | PM/FA/User | UAT | Manual (selalu) | 2 kelompok (fitur utama + transparansi bug yang dipertahankan) |
