# Business Flow — Migrasi product_history_report

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-26

> Port kode saja (bukan upgrade instance) — dijalankan lewat install bersih + data test/demo, bukan clone data produksi (step 7 N/A).

**Mode eksekusi:** Berdasarkan lesson project migrasi 17.0→18.0 sebelumnya (`doc-dev/migration_17.0_18.0/doc/10_qa/10_BUSINESS_FLOW_MIGRATION.md`) — AI-interaktif via browser automation eksternal (Claude Browser pane / Claude in Chrome) TERBUKTI GAGAL total di environment ini (root cause: `odoo.isReady` macet karena tab otomasi selalu `document.hidden=true`, bukan sesuatu yang bisa diperbaiki dari sisi modul). **Tidak diulang lagi di project ini** — langsung pakai jalur yang TERBUKTI jalan: Tour test Odoo native (`HttpCase.start_tour`, headless Chrome dikelola Odoo SENDIRI, bukan automation eksternal) + Integration test Step 9. Kombinasi keduanya menutup **SEMUA** skenario di bawah secara otomatis — tidak ada yang genuinely butuh klik manual dev.

---

## Level skenario

## Skenario

- [x] Skenario dari AC risiko tinggi — S-01 (AC-01), S-05 (AC-03-02, quirk MF-02)
- [x] Perbandingan side-by-side versi asal vs target — N/A untuk port kode saja (kesetaraan sudah diverifikasi via `01b_BASELINE_SPEC.md`/test otomatis Step 9)
- [x] Spot-check integritas data pasca migrasi — N/A, step 7 tidak dijalankan (port kode saja)
- [x] **Cek multi-dialog dari satu aksi** — **N/A, dikonfirmasi tidak ada kasus multi-dialog.** Satu-satunya aksi user (klik tombol "Stock History") membuka SATU window action (`graph,pivot,list`), tidak ada dialog/wizard kedua yang terbuka bersamaan/di belakang — tidak berubah dari 18.0.

### S-01: Buka laporan Stock History dari form produk
**Level:** Smoke
**Precondition:** Login sebagai admin (atau user apapun), ada produk apapun di database.
**Mode eksekusi:** **AI-otomatis (Tour test)**
**Steps:**
1. Buka Odoo 19.0, login `admin`/`admin`.
2. Buka app Inventory → Products → pilih produk apapun.
3. Di form produk, cari tombol statistik "Stock History" (icon sinyal) — tampil LANGSUNG di button box di 19.0 (tidak collapse ke "More" lagi seperti 18.0, lihat DIFF-16).
4. Klik tombol tersebut.
**Expected:** Window baru terbuka, judul "Stocks Histories", menampilkan view list (bukan error), bisa switch ke pivot/graph.
**Actual:** Tour `stock_history_tour` PASS 12/12 langkah (`static/tests/tours/stock_history_tour.js`, `HttpCase.start_tour`) — apps menu, buka app, buka Products, search produk fixture, klik kartu kanban, klik "Stock History" langsung, breadcrumb konfirmasi "Stocks Histories" muncul. Detail: `09_devtest/09_DEV_TESTING.md`.
**Status:** [x] Pass (dikonfirmasi Tour test otomatis, 2026-08-26)

### S-02: Verifikasi income-only untuk stok masuk dari luar (customer/supplier)
**Level:** Main Flow
**Precondition:** Produk dengan minimal satu stock move dari lokasi Customer/Supplier ke lokasi Internal (state Done).
**Mode eksekusi:** **AI-otomatis (Integration test Step 9)**
**Steps:**
1. Buka Stock History produk tersebut (S-01).
2. Switch ke view pivot atau list, cari bulan terjadinya move itu.
**Expected:** Kolom "Input" (income) bertambah sesuai qty move, kolom "Output" (outcome) TIDAK bertambah untuk move ini.
**Actual:** Dikonfirmasi `test_ac_03_01_customer_return_is_income_only` PASS — assertion presisi ke nilai income/outcome.
**Status:** [x] Pass (dikonfirmasi test otomatis Step 9)

### S-03: Verifikasi qty kumulatif mencakup histori lebih dari jendela tampil 12 bulan
**Level:** Main Flow
**Precondition:** Produk dengan histori stok lebih dari 12 bulan.
**Mode eksekusi:** **AI-otomatis (Integration test Step 9)**
**Steps:**
1. Buka Stock History produk tersebut.
2. Bandingkan kolom "Stock Quantity uom" (qty) baris pertama jendela dengan quantity on-hand aktual produk.
**Expected:** qty baris pertama TIDAK dimulai dari 0 kalau produk punya histori sebelum jendela 12 bulan — sudah mencakup saldo pembuka (BSL-005).
**Actual:** Dikonfirmasi `test_ac_02_01_qty_includes_pre_window_balance` PASS — `assertAlmostEqual` ke nilai qty kumulatif (100 + 5 = 105), termasuk move >13 bulan lalu.
**Status:** [x] Pass (dikonfirmasi test otomatis Step 9)

### S-04: Filter multi-company — data company lain tidak ikut terhitung
**Level:** Detail
**Precondition:** Instance multi-company (atau cukup dikonfirmasi lewat AC-04-01 yang sudah PASS di Step 9).
**Mode eksekusi:** **AI-otomatis (Integration test Step 9)**
**Steps:**
1. Login sebagai user dengan company aktif = Company A.
2. Buka Stock History produk yang punya move di Company B juga.
**Expected:** Hanya move Company A yang terhitung di income/outcome/qty.
**Actual:** Dikonfirmasi `test_ac_04_01_company_filter_excludes_other_company` PASS — kontrol (company benar, income>0) vs kandidat (company palsu, income=0).
**Status:** [x] Pass (dikonfirmasi test otomatis Step 9)

### S-05: Verifikasi bug source DIPERTAHANKAN — transfer internal→internal dihitung ganda
**Level:** Detail
**Precondition:** Produk dengan stock move transfer internal→internal.
**Mode eksekusi:** **AI-otomatis (Integration test Step 9)**
**Steps:**
1. Lakukan transfer stok internal→internal untuk suatu produk.
2. Buka Stock History produk itu, cek bulan terjadinya transfer.
**Expected:** Baik kolom "Input" MAUPUN "Output" bertambah sejumlah qty transfer itu (double-count) — ini BUG YANG SENGAJA DIPERTAHANKAN (`FINDINGS.md` MF-02), BUKAN kegagalan migrasi.
**Actual:** Dikonfirmasi `test_ac_03_02_internal_transfer_counted_as_both_income_and_outcome` PASS — income>=24 (20+4) DAN outcome>=4 pada bulan yang sama, double-count terbukti tetap terjadi identik dengan 18.0.
**Status:** [x] Pass (dikonfirmasi test otomatis Step 9)

### S-06: create/write/unlink langsung ke model report ditolak di level database
**Level:** Negative
**Precondition:** Mode developer aktif, akses ke Odoo shell atau RPC console.
**Mode eksekusi:** Manual (butuh developer mode/technical access) — TAPI sudah dikonfirmasi lewat automated test
**Steps:**
1. Aktifkan mode developer.
2. Coba `create()` record baru langsung ke model `stock.history.view`.
**Expected:** Operasi GAGAL dengan error database (bukan error ACL Odoo yang ramah pesan).
**Actual:** Sudah dikonfirmasi lewat automated test Step 9 (`test_ac_05_02_create_on_view_fails`, PASS). Skenario ini opsional untuk re-konfirmasi manual, tidak wajib diulang.
**Status:** [x] Pass (dikonfirmasi test otomatis Step 9)

### S-07: Search panel groupby tetap berfungsi pasca hapus atribut `<group expand=/string=>` (DIFF-01)
**Level:** Detail
**Precondition:** Window "Stocks Histories" sudah terbuka (lanjutan S-01).
**Mode eksekusi:** **AI-otomatis (Tour test, DIPERPANJANG di Step 9/10 — lihat addendum `09_DEV_TESTING.md`)**
**Steps:**
1. Dari window "Stocks Histories", klik ikon dropdown search options (`.o_searchview_dropdown_toggler`).
2. Cek daftar filter Group By yang muncul: "By products", "Date", "Category", "UOM".
**Expected:** Keempat filter groupby tetap tampil dan bisa diklik — atribut `expand`/`string` yang dihapus dari tag `<group>` (DIFF-01, dipaksa platform 19.0) TIDAK menghilangkan filter-nya sendiri, cuma atribut kosmetik tag pembungkus.
**Actual:** Dikonfirmasi extended Tour test (2 step baru ditambahkan ke `stock_history_tour`) PASS — dropdown terbuka, filter "By products" (`.o_group_by_menu .o_menu_item:contains("By products")`) ditemukan & clickable. Investigasi source (`addons/web/static/src/search/search_bar_menu/search_bar_menu.xml`) mengonfirmasi heading "Group By" sendiri di-hardcode komponen JS generik, tidak pernah berasal dari atribut `string=` arch modul — jadi secara desain TIDAK ADA dampak visual dari DIFF-01 sama sekali.
**Status:** [x] Pass (dikonfirmasi extended Tour test, 2026-08-26 — lihat `09_devtest/09_DEV_TESTING.md` "Addendum")

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01 | 1 |
| Main Flow | S-02, S-03 | 2 |
| Detail | S-04, S-05, S-07 | 3 |
| Negative | S-06 | 1 |

## Human QA Checklists

Lihat folder `human_qa/` (`00_README.md`, `01_SMOKE.md`, `02_MAIN_FLOW.md`, `03_DETAIL.md`, `04_NEGATIVE.md`).

## Loop-back

Tidak ada skenario Fail — S-01 s/d S-07, semuanya PASS lewat kombinasi Tour test (S-01, S-07) + Integration test Step 9 (S-02..S-06). Tidak ada yang perlu balik ke step sebelumnya.

## Instance QA

Docker instance sudah **dimatikan** (`docker compose down -v`) setelah semua bukti otomatis terkumpul — tidak ada lagi skenario yang butuh klik manual. Kalau dev ingin re-verifikasi visual sendiri kapan saja (opsional, bukan gate requirement), jalankan:
```bash
cd docker-env && docker compose up --build
```
lalu buka `http://localhost:8092` (login `admin`/`admin`) — instance akan otomatis reinstall modul + rerun seluruh test (termasuk Tour) sebelum server siap dipakai.

## Verdict

- [x] ✅ **Lulus** — S-01 & S-07 (Tour test otomatis) + S-02..S-06 (Integration test Step 9) semua PASS. Lanjut ke step 11 (UAT).
