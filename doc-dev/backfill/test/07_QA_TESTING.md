# QA Testing — product_history_report

**Step:** 07 — QA Testing (backfill, TANPA UAT — BACKFILL berhenti di sini)
**Ref:** `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`, `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md`, `03B_TEST_PLAN.md`
**Tanggal:** 2026-08-07

---

## 1. Area / AC yang Harus Dicakup

- [x] AC-01-01/01-02 — Tombol Stock History tampil & membuka window action yang benar
- [x] AC-02-01 — Angka qty/income/outcome di pivot/graph masuk akal (saldo awal + running-sum)
- [x] AC-04-01 — Filter multi-company: ganti company aktif, angka berubah sesuai
- [x] AC-05-01 — User non-Inventory tetap bisa lihat data (ACL longgar, F-04)

**Cek wajib "hanya satu dialog/wizard disentuh":** **N/A** — modul ini TIDAK PERNAH membuka
dialog/wizard perantara. Tombol "Stock History" langsung memanggil `action_open_stock_history()`
yang mengembalikan SATU `ir.actions.act_window` (graph/pivot/tree) secara langsung — tidak ada
dialog native Odoo maupun dialog custom yang terpicu bersamaan dari aksi yang sama. `[HASIL-BACA]`

---

## 2. Format Skenario

Lihat `doc-dev-backfill/templates/test/07_QA_TESTING.md` §2 untuk format standar.

---

## 3. Skenario

### S-01: Tombol Stock History tampil & membuka laporan yang benar
**Precondition:** Produk apapun dibuka di form `product.template`.
**Mode eksekusi:** Mode B/C (docker, real) — dieksekusi ULANG lewat Integration test Step 04
(`test_ac_01_01_button_present_in_form_arch`, `test_ac_01_02_action_open_stock_history_returns_expected_action`),
bukan browser visual. Lihat "Keputusan Scope" di §4 untuk alasan tidak memakai Tour headless (Mode E).
**Steps:**
1. Buka form produk manapun.
2. Klik tombol statistik "Stock History".
**Expected:** Tombol muncul setelah tombol "Stock Moves" bawaan `stock`; klik membuka window
action "Stocks Histories" (`res_model=stock.history.view`, `view_mode=graph,pivot,tree`), domain
di-scope ke produk yang sedang dibuka.
**Actual:** Dikonfirmasi lewat 2 Integration test REAL (`docker compose up`, Odoo 17.0) — PASS
penuh. Arch form mengandung `action_open_stock_history`; pemanggilan method mengembalikan action
dict persis sesuai Expected.
**Status:** ☑ Pass
**Provenance:** `[DIKONFIRMASI]` (eksekusi nyata, bukan baca kode saja)

---

### S-02: Angka laporan mencerminkan histori pergerakan stok yang benar
**Precondition:** Produk dengan riwayat `stock.move` (done) — sebagian >13 bulan lalu, sebagian
dalam 12 bulan terakhir.
**Mode eksekusi:** Mode B/C (docker, real) — `test_ac_02_01_qty_includes_pre_window_balance`.
**Steps:**
1. Buat move 100 unit masuk (>13 bulan lalu) dan 5 unit masuk (10 hari lalu).
2. Klik/panggil Stock History untuk produk itu.
**Expected:** Baris bulan terbaru menampilkan `qty` kumulatif 105 (menggabungkan saldo dari histori
lama + pergerakan baru) — BUKAN cuma mulai menghitung dari awal jendela 12 bulan.
**Actual:** Dikonfirmasi PASS — `qty` baris terakhir = 105.0 sesuai perhitungan manual.
**Status:** ☑ Pass
**Provenance:** `[DIKONFIRMASI]`

---

### S-03: Ganti company aktif mengubah angka yang ditampilkan
**Precondition:** User dengan akses ke company yang berbeda; produk punya move di company X.
**Mode eksekusi:** Mode B/C (docker, real) — `test_ac_04_01_company_filter_excludes_other_company`
(disimulasikan lewat variasi parameter `companies` ke `recreate_view()`, setara efek ganti company
aktif di UI karena `action_open_stock_history()` selalu memakai `self.env.companies.ids` — company
yang SEDANG aktif di sesi user).
**Steps:**
1. Dengan company aktif = company asli move (company X): buka Stock History → catat income.
2. Simulasikan filter company lain (company yang TIDAK punya move ini): buka Stock History lagi.
**Expected:** Langkah 1 menampilkan income > 0; langkah 2 menampilkan income = 0 (move company X
tidak ikut terhitung saat company aktif berbeda).
**Actual:** Dikonfirmasi PASS untuk kedua sisi (kontrol company benar → income 9.0; company salah →
income 0.0, setelah `invalidate_model()` — lihat `04A_DEV_TESTING.md` §3 poin 5 untuk catatan
teknis kenapa langkah invalidate ini perlu di TEST, bukan indikasi bug produksi).
**Status:** ☑ Pass
**Provenance:** `[DIKONFIRMASI]`

---

### S-04: User tanpa grup Inventory tetap bisa melihat data stock history (ACL longgar — F-04)
**Precondition:** User baru dibuat, hanya grup `base.group_user` (TANPA `stock.group_stock_user`
atau grup Inventory manapun).
**Mode eksekusi:** Mode B/C (docker, real) — `test_ac_05_01_read_open_for_user_without_inventory_group`.
**Steps:**
1. Login/emulasikan sesi sebagai user tanpa grup Inventory.
2. Coba `search()`/baca `stock.history.view`.
**Expected (SEKARANG, bukan idealnya):** `read` BERHASIL — ACL model ini tidak membatasi per grup
(`ir.model.access.csv` tanpa `group_id`, lihat BR-06/F-04).
**Actual:** Dikonfirmasi PASS — user tanpa grup Inventory berhasil membaca data pergerakan stok.
Ini **bukan bug teknis** (tidak crash/error) tapi kandidat masalah KEBIJAKAN akses data yang
dicatat di `FINDINGS.md` F-04 untuk keputusan pemilik modul.
**Status:** ☑ Pass (secara teknis) — lihat `FINDINGS.md` F-04 untuk status `[PERLU-KEPUTUSAN]`
**Provenance:** `[DIKONFIRMASI]`

---

### S-05: Transfer internal→internal dihitung ganda di income dan outcome (F-02)
**Precondition:** Produk dengan stok tersedia di satu lokasi internal, ditransfer ke lokasi
internal lain (dalam warehouse yang sama).
**Mode eksekusi:** Mode B/C (docker, real) — `test_ac_03_02_internal_transfer_counted_as_both_income_and_outcome`.
**Steps:**
1. Isi stok 20 unit (supplier → internal).
2. Transfer 4 unit (internal → internal lain).
3. Buka Stock History.
**Expected (SEKARANG):** Baris bulan berjalan menampilkan `income >= 24` (20+4) DAN `outcome >= 4`
— transfer internal ikut dihitung di KEDUA kolom, bukan diabaikan.
**Actual:** Dikonfirmasi PASS sesuai Expected — perilaku BR-03 terbukti nyata, bukan cuma dugaan
baca kode.
**Status:** ☑ Pass (secara teknis, sesuai kode SEKARANG) — status disengaja/bug tetap
`[PERLU-KEPUTUSAN]` di `FINDINGS.md` F-02
**Provenance:** `[DIKONFIRMASI]`

---

## 4. Status Sub-file & Rekap Eksekusi

| File | Isi | Status | Dieksekusi? | Mode |
|---|---|---|---|---|
| §3 di file ini | 5 skenario (S-01..S-05) | ✅ Selesai | Ya | Mode B/C (docker, real) |
| `07B_QA_AI_BROWSER.md` | Verifikasi browser AI | N/A | Tidak | — (lihat "Keputusan Scope" di bawah) |

**Keputusan Scope — Tour headless (Mode E)/browser AI TIDAK dipakai untuk modul ini:**
`product_history_report` **tidak punya satu file JS custom pun** (`static/description/` cuma berisi
banner/icon untuk App Store listing, tidak ada `static/src/js/`). Tombol "Stock History" adalah
tombol `type="object"` standar Odoo (`<button ... type="object" name="action_open_stock_history"/>`)
— seluruh mekanisme klik→panggil-method→buka-window-action ditangani MURNI oleh web client Odoo
CORE, bukan kode modul ini. Nilai tambah Tour headless (Mode E, biasanya untuk membuktikan "JS
modul benar-benar jalan di browser nyata") jadi RENDAH di sini — tidak ada JS modul yang perlu
dibuktikan. Sebagai gantinya, Step 07 memakai Integration test REAL (Step 04, `docker compose up`
sungguhan, bukan mock) sebagai bukti utama — method yang sama persis yang dipanggil tombol UI
sudah diverifikasi nyata dengan data end-to-end (stock move → SQL view → hasil laporan). Keputusan
ini konsisten dengan prinsip BACKFILL "jangan bangun proses tambahan sebelum terbukti perlu"
(`OVERVIEW.md` §2).

**Keterbatasan eksekusi:** Tidak ada verifikasi visual browser sungguhan (screenshot UI nyata) —
seluruh bukti berasal dari Integration test level ORM/SQL, bukan render UI. Untuk modul ini
risikonya dinilai rendah (tidak ada custom JS/CSS/layout kompleks yang bisa salah render), tapi
dicatat eksplisit sebagai keterbatasan, bukan disamarkan sebagai "sudah dites visual".

---

## 5. Rekap Findings

| Tag | Jumlah |
|---|---|
| `[PERLU-KEPUTUSAN]` | 5 (F-01, F-02, F-03, F-04, F-09) |
| `[DIKONFIRMASI]` | 1 (F-07 — resolved, no collision) |
| `[HASIL-BACA]` (tanpa masalah/lesson metodologi) | 3 (F-05, F-06, F-08) |

**Verdict:** Backfill dokumentasi selesai sampai Step 07 (QA Testing). **Tidak ada sign-off** — ini
bukan release gate. Keputusan atas item `[PERLU-KEPUTUSAN]` di `FINDINGS.md` ada di tangan pemilik
modul (lihat khususnya F-01 dan F-02 sebagai prioritas Tinggi/Sedang).

---

## 6. Bug / Perlu Perbaikan

Tidak ada skenario **Fail** di §3 — kelima skenario Pass sesuai perilaku kode SEKARANG. "Bug" yang
ditemukan (F-01, F-02, F-04) adalah soal DESAIN/KEBIJAKAN yang butuh keputusan pemilik modul
(apakah disengaja atau perlu diperbaiki), bukan crash/error teknis — lihat `FINDINGS.md` untuk
detail lengkap dan rekomendasi.

---

## 7. Slot Metode Masa Depan

- `07B_QA_AI_BROWSER.md`/Tour headless — TIDAK dibuat untuk modul ini (lihat "Keputusan Scope" di
  §4). Revisit HANYA kalau modul ini di masa depan menambah JS custom (`static/src/js/`) yang
  butuh dibuktikan jalan di browser nyata.
