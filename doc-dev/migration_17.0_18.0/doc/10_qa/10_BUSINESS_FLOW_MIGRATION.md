# Business Flow — Migrasi product_history_report

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-08-24

> Port kode saja (bukan upgrade instance) — dijalankan lewat install bersih + data demo, bukan clone data produksi (step 7 N/A).

**Mode eksekusi:** Dicoba **AI-interaktif** dulu (Claude Browser pane, instance Odoo 18.0 nyata sudah hidup) — **GAGAL karena limitasi environment, bukan bug modul** (lihat "Catatan Teknis" di bawah). Semua skenario di bawah jadi **Manual** — instance tetap dibiarkan hidup untuk dev/QA klik langsung.

## Catatan Teknis — Kegagalan AI-interaktif

Login ke `http://localhost:8091` sukses (request `/odoo/inventory`, `/web/webclient/load_menus`, `/mail/data` semua 200 OK, menu ter-load di level server). Tapi Owl webclient tidak pernah merender apapun ke DOM — `.o_web_client` ada di DOM tapi isinya kosong (24 karakter whitespace), tidak ada error JS yang tertangkap console selain kegagalan registrasi Service Worker (tidak fatal). Kemungkinan root cause: Browser pane sesi ini tidak "displayed"/compositing (dikonfirmasi terpisah lewat error `computer screenshot` — "the Browser pane is not displayed, so the page is not compositing frames"), dan Owl app kemungkinan menunggu tick render yang tidak pernah terpicu tanpa compositing aktif. **Ini limitasi tooling sesi ini, bukan gap pengujian genuinely dibutuhkan** — server-side (yang sebenarnya diuji Step 9 lewat automated test) sudah terbukti benar. Tidak dieksplorasi lebih lanjut supaya tidak menghabiskan waktu di luar scope modul.

**Instance tetap hidup untuk dev** (lihat langkah serah-terima di akhir dokumen).

---

## Level skenario

## Skenario

- [x] Skenario dari AC risiko tinggi — S-01 (AC-01), S-05 (AC-03-02, quirk MF-02)
- [x] Perbandingan side-by-side versi asal vs target — N/A untuk port kode saja (tidak ada instance 17.0 produksi berjalan paralel untuk dibandingkan; kesetaraan sudah diverifikasi via `01b_BASELINE_SPEC.md`/test otomatis Step 9)
- [x] Spot-check integritas data pasca migrasi — N/A, step 7 tidak dijalankan (port kode saja)
- [x] **Cek multi-dialog dari satu aksi** — **N/A, dikonfirmasi tidak ada kasus multi-dialog.** Satu-satunya aksi user (klik tombol "Stock History") membuka SATU window action (`graph,pivot,list`), tidak ada dialog/wizard kedua yang terbuka bersamaan/di belakang.

### S-01: Buka laporan Stock History dari form produk
**Level:** Smoke
**Precondition:** Login sebagai admin (atau user apapun), ada produk apapun di database (demo data sudah terisi).
**Mode eksekusi:** Manual
**Steps:**
1. Buka `http://localhost:8091`, login `admin`/`admin`.
2. Buka app Inventory → Products → pilih produk apapun.
3. Di form produk, cari tombol statistik "Stock History" (icon sinyal), tepat setelah tombol "Stock Moves" bawaan.
4. Klik tombol tersebut.
**Expected:** Window baru terbuka, judul "Stocks Histories", menampilkan view **list** (bukan error "Invalid view type"), bisa switch ke pivot/graph.
**Actual:** *(diisi dev saat eksekusi)*
**Status:** [ ] Pass / [ ] Fail

### S-02: Verifikasi income-only untuk stok masuk dari luar (customer/supplier)
**Level:** Main Flow
**Precondition:** Produk dengan minimal satu stock move dari lokasi Customer/Supplier ke lokasi Internal (state Done).
**Mode eksekusi:** Manual
**Steps:**
1. Buka Stock History produk tersebut (S-01).
2. Switch ke view pivot atau list, cari bulan terjadinya move itu.
**Expected:** Kolom "Input" (income) bertambah sesuai qty move, kolom "Output" (outcome) TIDAK bertambah untuk move ini.
**Actual:** *(diisi dev saat eksekusi)*
**Status:** [ ] Pass / [ ] Fail

### S-03: Verifikasi qty kumulatif mencakup histori lebih dari jendela tampil 12 bulan
**Level:** Main Flow
**Precondition:** Produk dengan histori stok lebih dari 12 bulan (bisa pakai produk demo Odoo yang sudah lama, atau produk hasil test AC-02-01 kalau DB test masih ada).
**Mode eksekusi:** Manual
**Steps:**
1. Buka Stock History produk tersebut.
2. Bandingkan kolom "Stock Quantity uom" (qty) baris pertama jendela dengan quantity on-hand aktual produk itu (menu Inventory → Reporting, atau field on-hand di form produk).
**Expected:** qty baris pertama TIDAK dimulai dari 0 kalau produk punya histori sebelum jendela 12 bulan — sudah mencakup saldo pembuka (BSL-005).
**Actual:** *(diisi dev saat eksekusi)*
**Status:** [ ] Pass / [ ] Fail

### S-04: Filter multi-company — data company lain tidak ikut terhitung
**Level:** Detail
**Precondition:** Instance multi-company (atau cukup dikonfirmasi lewat AC-04-01 yang sudah PASS di Step 9 — skenario ini opsional kalau instance QA cuma single-company).
**Mode eksekusi:** Manual
**Steps:**
1. Login sebagai user dengan company aktif = Company A.
2. Buka Stock History produk yang punya move di Company B juga.
**Expected:** Hanya move Company A yang terhitung di income/outcome/qty.
**Actual:** *(diisi dev saat eksekusi — atau tandai "sudah dikonfirmasi test otomatis Step 9" kalau instance QA single-company)*
**Status:** [ ] Pass / [ ] Fail

### S-05: Verifikasi bug source DIPERTAHANKAN — transfer internal→internal dihitung ganda
**Level:** Detail
**Precondition:** Produk dengan stock move transfer internal→internal (dua-duanya lokasi usage `internal`).
**Mode eksekusi:** Manual
**Steps:**
1. Lakukan transfer stok internal→internal untuk suatu produk (mis. antar rak dalam warehouse yang sama).
2. Buka Stock History produk itu, cek bulan terjadinya transfer.
**Expected:** Baik kolom "Input" MAUPUN "Output" bertambah sejumlah qty transfer itu (double-count) — ini BUG YANG SENGAJA DIPERTAHANKAN (`FINDINGS.md` MF-02), BUKAN kegagalan migrasi. Kalau angkanya TIDAK double-count (cuma satu kolom bertambah), itu justru tanda regresi/perubahan behavior tak sengaja — wajib dilaporkan.
**Actual:** *(diisi dev saat eksekusi)*
**Status:** [ ] Pass / [ ] Fail

### S-06: create/write/unlink langsung ke model report ditolak di level database
**Level:** Negative
**Precondition:** Mode developer aktif, akses ke Odoo shell atau RPC console.
**Mode eksekusi:** Manual (butuh developer mode/technical access, bukan klik UI biasa)
**Steps:**
1. Aktifkan mode developer.
2. Coba `create()` record baru langsung ke model `stock.history.view` (lewat Odoo shell atau technical menu).
**Expected:** Operasi GAGAL dengan error database (bukan error ACL Odoo yang ramah pesan) — konsisten `AC-05-02`, model ini SQL view tanpa `INSTEAD OF` trigger.
**Actual:** Sudah dikonfirmasi lewat automated test Step 9 (`test_ac_05_02_create_on_view_fails`, PASS). Skenario ini opsional untuk re-konfirmasi manual, tidak wajib diulang kalau dev percaya hasil test otomatis.
**Status:** [x] Pass (dikonfirmasi test otomatis Step 9)

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01 | 1 |
| Main Flow | S-02, S-03 | 2 |
| Detail | S-04, S-05 | 2 |
| Negative | S-06 | 1 |

## Human QA Checklists

Lihat folder `human_qa/` (`00_README.md`, `01_SMOKE.md`, `02_MAIN_FLOW.md`, `03_DETAIL.md`, `04_NEGATIVE.md`).

## Loop-back

Tidak ada skenario Fail yang tercatat sejauh ini (S-06 sudah pass lewat test otomatis; S-01..S-05 menunggu eksekusi manual dev — lihat "Serah-terima" di bawah).

## Serah-terima ke Dev — Langkah Konkret

Instance QA Odoo 18.0 **sudah hidup sekarang** di `docker-env/`, siap diklik langsung:

1. Buka browser ke:
```
http://localhost:8091
```
2. Login dengan:
```
Email: admin
Password: admin
```
3. Jalankan S-01 sampai S-05 di atas (Inventory → Products → pilih produk → tombol "Stock History"). Isi kolom "Actual" dan centang Status tiap skenario di `10_BUSINESS_FLOW_MIGRATION.md` ini langsung.
4. Kalau semua Pass, beri tahu balik supaya gate Step 10 bisa ditutup dan lanjut ke Step 11 (UAT). Kalau ada yang Fail, sebutkan skenario mana — balik ke Step 9 dulu.
5. Setelah selesai QA, matikan instance (opsional, boleh dibiarkan hidup kalau masih dipakai):
```bash
cd docker-env && docker compose down
```

## Verdict

- [ ] ✅ Lulus — lanjut ke step 11 (**menunggu konfirmasi dev untuk S-01..S-05 di atas — S-06 sudah pass lewat test otomatis**)
- [ ] ❌ Ada kegagalan: ...
