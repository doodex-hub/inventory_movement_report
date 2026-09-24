# Migration Acceptance Criteria — product_history_report

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `01_intake/01b_BASELINE_SPEC.md` dan kode 19.0 yang berjalan (`migration/19.0`) — **bukan** `03_spec/03_MIGRATION_SPEC.md`
**Tanggal:** 2026-09-24
**Status:** ✅ Selesai (step non-gate)

> AC-01-01..AC-05-02 diwarisi dari project 18→19 (9/9 test nyata PASS di 19.0), ID dipertahankan, dipetakan ulang ke BSL versi 19.0 dan ditegaskan berlaku IDENTIK di 20.0. AC baru (AC-01-04, AC-01-05, AC-05-03, AC-05-04, AC-06-01) diturunkan dari BSL yang area-nya tersentuh perubahan 20.0 (DIFF-01, DIFF-02, DIFF-12/13) — tetap berbasis baseline 19.0, bukan dari rencana migrasi.
> Tanda **[RISIKO TINGGI]** = terkait item Critical Blocker/Sedang di `03_MIGRATION_SPEC.md` §2b.

---

## AC-01 — Tombol Stock History

**AC-01-01** (verifies `BSL-001`, `BSL-013`)
Given admin (user Inventory) membuka form `product.template` di 20.0
When form ter-render
Then tombol statistik "Stock History" (`name="action_open_stock_history"`) ada di arch form, diletakkan tepat setelah tombol In/Out (`action_view_stock_move_lines`) — identik dengan 19.0.

**AC-01-02** (verifies `BSL-001`, `BSL-003`)
Given user berada di form satu produk
When `action_open_stock_history()` dipanggil (klik tombol)
Then dikembalikan window action `res_model` `stock.history.view`, `view_mode` `graph,pivot,list`, dengan `domain` berisi id baris `date >= date_debut` — identik dengan 19.0.

**AC-01-03** (verifies `BSL-001`, `BSL-012`)
Given user Community membuka produk fixture lewat menu Inventory → Products (jalur navigasi tour 19.0)
When user klik "Stock History" lalu membuka dropdown search
Then breadcrumb berganti "Stocks Histories" (target `current`) dan filter group-by "By products" ada & bisa diklik — identik dengan 19.0.

**AC-01-04** (verifies `BSL-013`) **[RISIKO TINGGI — DIFF-02, silent visual]**
Given form `product.template` di 20.0
When arch & DOM tombol "Stock History" diperiksa
Then tombol memakai ikon bar sinyal yang benar-benar dirender web client 20.0: atribut arch `icon="android_cell_5_bar"` (tidak ada lagi `fa-signal`), dan DOM tombol memuat `<i class="o_button_icon oi" data-icon="android_cell_5_bar">`. **Perubahan teknis yang disengaja untuk mempertahankan UX 19.0** (tombol ber-ikon sinyal) — nama ikon berbeda karena sistem ikon berganti, tampilan setara.

**AC-01-05** (verifies `BSL-001`, `BSL-012`, `BSL-013`)
Given user (Community ATAU Enterprise) membuka langsung form produk fixture
When user klik "Stock History"
Then breadcrumb "Stocks Histories" muncul dan view pertama yang ter-render adalah graph (`view_mode` diawali `graph`) — identik dengan 19.0, di kedua edisi.

---

## AC-02 — Isi laporan per produk

**AC-02-01** (verifies `BSL-005`)
Given produk punya move done >13.2 bulan lalu (100) dan 10 hari lalu (5)
When view di-rebuild
Then `qty` baris terakhir = 105 (running sum mencakup saldo pembuka) — identik dengan 19.0.

**AC-02-02** (verifies `BSL-002` — **HARUS TETAP ADA**, `FINDINGS.md` MF-01)
Given dua user klik "Stock History" untuk produk berbeda hampir bersamaan
When request dieksekusi berdekatan
Then perilaku tetap tidak deterministik (SQL view global, tanpa locking) — sama seperti 19.0. Diverifikasi via code identity (`models/*.py` byte-identik dengan 19.0), bukan test konkurensi.

---

## AC-03 — Perhitungan income/outcome

**AC-03-01** (verifies `BSL-004`)
Given move done customer → internal (7)
When view di-rebuild
Then 7 masuk `income`, `outcome` 0 — identik dengan 19.0.

**AC-03-02** (verifies `BSL-004` — **HARUS TETAP ADA**, MF-02)
Given supplier → internal (20) lalu internal → internal (4)
When view di-rebuild
Then baris bulan berjalan `income >= 24` dan `outcome >= 4` (double-count tetap terjadi) — identik dengan 19.0.

---

## AC-04 — Filter multi-company

**AC-04-01** (verifies `BSL-006`, `BSL-009`)
Given move di company aktif (9)
When view di-rebuild dengan company yang benar → income > 0; di-rebuild ulang dengan company id yang tidak cocok (+ `invalidate_model()`, MF-04)
Then income total = 0 — identik dengan 19.0.

---

## AC-05 — Akses model report

**AC-05-01** (verifies `BSL-007` — **HARUS TETAP ADA**, MF-03) **[RISIKO TINGGI — DIFF-01]**
Given user internal hanya `base.group_user` (tanpa `stock.group_stock_user`)
When user search `stock.history.view`
Then baris terbaca (akses tidak dibatasi grup Inventory) — identik dengan 19.0.

**AC-05-02** (verifies `BSL-008`)
Given `create()` langsung ke `stock.history.view`
When dieksekusi
Then gagal di level database — identik dengan 19.0.

**AC-05-03** (verifies `BSL-007`) **[RISIKO TINGGI — DIFF-01]**
Given modul terinstal di 20.0
When record `ir.access` XML-ID `product_history_report.access_stock_history_view` diperiksa
Then `model_id` = `stock.history.view`, `group_id` = `base.group_everyone`, `operation` = `crud`, `domain` kosong, `kind` = `permission` — padanan persis ACL 19.0 tanpa grup (1,1,1,1). XML-ID sama dengan 19.0.

**AC-05-04** (verifies `BSL-007` — **HARUS TETAP ADA**, MF-03) **[RISIKO TINGGI — DIFF-01]**
Given user portal (`base.group_portal`, bukan user internal)
When user search `stock.history.view`
Then baris terbaca — identik dengan 19.0 (ACL `ir.model.access` tanpa grup di 19.0 berlaku untuk semua user termasuk portal). Kalau di 20.0 portal ditolak, itu regresi (ACL diperketat tanpa disengaja).

---

## AC-06 — Lingkungan Enterprise (MF-07)

**AC-06-01** (verifies `BSL-001`, `BSL-004`..`BSL-008`, `BSL-013`)
Given addons Enterprise 20.0 di path dan `stock_enterprise`, `quality_control`, `stock_barcode` terinstal bersama modul ini
When modul diinstal dan seluruh test suite modul dijalankan
Then instalasi sukses (view form produk gabungan `quality_control` + modul ini valid) dan semua test PASS — kecuali tour Community `stock_history_tour` yang di-skip eksplisit (DIFF-12, Home Menu Enterprise), digantikan AC-01-05 yang jalan di Enterprise.

---

## Catatan Traceability

| BSL | AC |
|---|---|
| BSL-001 | AC-01-01, 01-02, 01-03, 01-05, 06-01 |
| BSL-002 | AC-02-02 |
| BSL-003 | AC-01-02 |
| BSL-004 | AC-03-01, 03-02 |
| BSL-005 | AC-02-01 |
| BSL-006 | AC-04-01 |
| BSL-007 | AC-05-01, 05-03, 05-04 |
| BSL-008 | AC-05-02 |
| BSL-009 | AC-04-01 (efek samping metodologi test) |
| BSL-010, BSL-011 | Tidak actionable sebagai AC (dead code) — diverifikasi via code identity di Step 8 |
| BSL-012 | AC-01-03, 01-05 |
| BSL-013 | AC-01-01, 01-04, 01-05 |
| BSL-014 | Code identity `models/stock_history_view.py` (Step 8) |
| BSL-015 | Diverifikasi Step 8 (isi manifest) |

---

## AC-07 — Hardening keamanan 20.0 (SCOPE-02, disetujui dev 2026-09-24 — PERUBAHAN DISENGAJA, bukan identik 19.0)

**AC-07-01** (verifies `BSL-002` jalur tombol; MF-10)
Given modul terinstal di 20.0
When `recreate_view` diminta sebagai method publik (jalur RPC `call_kw` → `get_public_method`)
Then ditolak dengan `AccessError` — **berbeda dari 19.0 (disengaja)**; klik tombol "Stock History" (pemanggilan server-side) tetap mengembalikan action `stock.history.view` seperti 19.0.

**AC-07-02** (MF-10)
Given argumen `product_template_id` atau `companies` bukan integer
When `recreate_view` dipanggil
Then `ValueError` sebelum SQL apapun dieksekusi — **berbeda dari 19.0 (disengaja)**. Input sah (id integer, id company dipisah koma) tetap menghasilkan laporan identik (dibuktikan AC-02..AC-04).
