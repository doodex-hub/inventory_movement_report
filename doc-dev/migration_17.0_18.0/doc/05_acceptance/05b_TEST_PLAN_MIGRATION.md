# Test Plan (Migrasi) — product_history_report

**Step:** 5 — Acceptance Criteria & Test Plan (satu paket dengan `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-24

---

## Step 9 — Dev Testing

> Eksekusi: `odoo-bin -i product_history_report --test-enable --test-tags /product_history_report --stop-after-init` di container Odoo 18.0. Modul tidak punya komponen Owl/JS (`01a_MIGRATION_INTAKE.md` §2b) — tidak ada Tour test.

**Audit kesiapan test (9a, dilakukan sekarang bukan asumsi):** `tests/test_product_history_report.py` dibawa dari `source-codebase` (hasil `doc-dev-backfill`), 8 method test, SEMUA berisi logika assertion nyata (bukan stub docstring) — dikonfirmasi baca isi tiap method langsung (§ini bukan sekadar `grep -c "def test_"`). 7/8 dijalankan tanpa modifikasi; 1/8 (`test_ac_01_02_...`) WAJIB diupdate 1 baris assertion (`view_mode` string) mengikuti fix `03_MIGRATION_SPEC.md` DIFF-02 — kalau tidak diupdate, test itu akan FAIL karena test-nya sendiri stale, bukan karena kode migrasi salah.

| AC | Deskripsi | Unit | Integration | Tour (Owl/JS) |
|---|---|---|---|---|
| AC-01-01 | Tombol Stock History ada di arch form | — | `test_ac_01_01_button_present_in_form_arch` | N/A — tidak ada Owl/JS |
| AC-01-02 | Klik tombol → action window benar | — | `test_ac_01_02_action_open_stock_history_returns_expected_action` (**wajib update baris 103**: `'graph,pivot,tree'`→`'graph,pivot,list'`) | N/A |
| AC-02-01 | qty running-sum mencakup saldo >13 bulan | — | `test_ac_02_01_qty_includes_pre_window_balance` | N/A |
| AC-02-02 | Race condition SQL view global (tetap ada, tidak ditest otomatis — sifat race condition tidak deterministik/tidak reliable di unit test) | — | — (tidak ada test — konsisten dengan status 17.0, `FINDINGS.md` MF-01 belum pernah ditest concurrency) | N/A |
| AC-03-01 | Move customer→internal = income saja | — | `test_ac_03_01_customer_return_is_income_only` | N/A |
| AC-03-02 | Move internal→internal = income DAN outcome (double-count dipertahankan) | — | `test_ac_03_02_internal_transfer_counted_as_both_income_and_outcome` | N/A |
| AC-04-01 | Filter multi-company | — | `test_ac_04_01_company_filter_excludes_other_company` | N/A |
| AC-05-01 | Read terbuka tanpa grup Inventory | — | `test_ac_05_01_read_open_for_user_without_inventory_group` | N/A |
| AC-05-02 | create/write/unlink ke view gagal di DB | — | `test_ac_05_02_create_on_view_fails` | N/A |

## Step 10 — QA Testing

> Modul backend murni tanpa UI kompleks (1 tombol + 1 window action graph/pivot/list) — cukup **Manual** per AC, tidak perlu AI+tool eksternal (tidak ada lintas sistem/browser matrix yang butuh Playwright).

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal (ref script) |
|---|---|---|---|---|
| AC-01-01, AC-01-02 | Klik tombol Stock History di form produk, verifikasi window `graph,pivot,list` terbuka dengan judul "Stocks Histories" | ✅ (dev/QA klik langsung di instance 18.0) | Opsional (Claude in Chrome kalau tersedia) | — |
| AC-02-01, AC-02-02, AC-03-01, AC-03-02, AC-04-01, AC-05-01, AC-05-02 | Sudah tercakup penuh oleh Integration test Step 9 (butuh data setup programatik — stock move history, multi-company, multi-user — tidak praktis diulang manual) | — (cukup Step 9) | — | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Laporan riwayat stok per produk | AC-01-01, AC-01-02, AC-02-01, AC-04-01 | Business user Inventory buka form produk apapun yang punya histori stok, klik "Stock History", verifikasi grafik/pivot/list tampil dan angkanya masuk akal dibanding Stock Moves bawaan |
| Bug/quirk yang dipertahankan (tidak untuk "lulus/gagal" — cukup dikonfirmasi paham) | AC-02-02, AC-03-02, AC-05-01 | Business user/PM diberi tahu eksplisit: race condition SQL view (jarang muncul, cuma saat 2 user klik hampir bersamaan), double-count transfer internal di income/outcome, dan ACL terbuka semua user internal — SEMUA ini SUDAH ADA di 17.0, bukan regresi baru dari migrasi |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer | Integration (8 test, 1 wajib update 1 baris) | Otomatis/background | 9 AC (AC-02-02 tidak ada test otomatis, by design) |
| 10 | QA | Manual | Manual, satu skenario utama + spot-check | 9 AC (8 sudah tercakup Step 9, 1 manual klik) |
| 11 | PM/FA/User | UAT | Manual (selalu) | 2 kelompok (fitur utama + transparansi bug yang dipertahankan) |
