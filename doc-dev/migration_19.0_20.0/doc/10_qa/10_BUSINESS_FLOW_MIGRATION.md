# Business Flow — Migrasi product_history_report

**Step:** 10 — QA Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `09_devtest/09_DEV_TESTING.md`
**Tanggal:** 2026-09-24
**Status:** ✔️ Lulus gate
**Slot:** diberikan dev 2026-09-24 ("lanjut step 10").

> Port kode saja (tanpa data produksi, Step 7 N/A) → dijalankan di install bersih dengan data QA yang dibuat skrip, bukan clone produksi.

**Mode eksekusi (per skenario, lihat kolom Mode):**
- **Tour + Integration (Step 9)** — jalur yang terbukti reliable di environment ini (lesson 17→18/18→19).
- **AI-interaktif = Playwright MCP headless** (default CLI, keputusan 2026-08-27) terhadap server QA live. **Berjalan normal** — tidak ada silent-fail `document.hidden` seperti engine browser lama; satu kegagalan klik (timeout navigasi setelah login, karena bundle aset pertama kali dibuat) diatasi dengan navigasi ulang, sesuai STOP-rule (retry sekali dengan pendekatan berbeda).
- **Cross-Version Compare** (wajib — kriteria "ada dependency Enterprise", MF-07; prosedur `templates/CROSS_VERSION_COMPARE.md`): dua instance hidup berdampingan dengan data identik.

**Environment QA live:**

| Instance | Port | Kode | Addons | Modul terinstal |
|---|---|---|---|---|
| 20.0 | 8093 | `migration/20.0` (commit `f29bbe4` + fix helper test) | `odoo20` + `enterprise20` | `product_history_report`, `stock_enterprise`, `quality_control` |
| 19.0 | 8094 | `git archive migration/19.0` (source of truth) | image Odoo 19.0 + `enterprise19` | sama |

Data dibuat oleh skrip yang SAMA di kedua instance (`evidence/cvc_seed.py`): 1 produk, 6 move done dengan tanggal mundur — supplier→stock 100 (450 hari lalu, saldo pembuka), 40 (200 hari), stock→customer 15 (100 hari), customer→stock 7 (40 hari, retur), stock→shelf internal 4 (5 hari, MF-02), supplier→stock 5 (3 hari). Bukti mentah di `evidence/`.

---

## Skenario

- [x] Skenario dari AC risiko tinggi (AC-01-04, AC-05-01/03/04, AC-07) — S-05, S-09, S-11.
- [x] **Cross-Version Compare** — DIJALANKAN (kriteria Enterprise). Hasil: S-03, S-04, S-12 + §Cross-Version Compare di bawah.
- [x] Spot-check integritas data pasca migrasi — N/A (Step 7 N/A, port kode saja).
- [x] Multi-dialog/wizard dari satu aksi — **N/A — dikonfirmasi tidak ada kasus multi-dialog**: satu-satunya aksi modul (tombol Stock History) membuka satu window action `target: current`, tanpa dialog/wizard.

### S-01: Buka laporan Stock History dari form produk
**Level:** Smoke
**Precondition:** user Inventory (admin), produk ada.
**Mode eksekusi:** Tour (Step 9, Community + Enterprise) + AI-interaktif Playwright (20.0 Enterprise live)
**Steps:** buka form produk → klik "Stock History" (di Enterprise: lewat dropdown More) → action terbuka.
**Expected:** breadcrumb "Stocks Histories", target current, graph sebagai view pertama (BSL-001).
**Actual:** live 20.0: URL `/odoo/action-301/5/stock.history.view`, breadcrumb `QA20 CVC Product / Stocks Histories`, view aktif `o_graph`, canvas ter-render; switcher Graph → Pivot → List. Tour `stock_history_tour` 12/12 (Community) + `stock_history_form_tour` 5/5 (Community & Enterprise) "tour succeeded".
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

### S-02: Modul terinstal bersih di Odoo 20.0 (Community & Enterprise)
**Level:** Smoke
**Precondition:** DB baru tanpa demo.
**Mode eksekusi:** AI-otomatis (G1/Run C/Run E) + server QA live
**Steps:** install `product_history_report` (+ `stock_enterprise`, `quality_control` untuk Enterprise).
**Expected:** install sukses; `security/ir.access.csv` ter-load.
**Actual:** Run C/Run E exit 0; server QA 20.0 & 19.0 "Modules loaded". Satu-satunya ERROR: `Model stock.history.view has no table.` — identik di 19.0 (MF-09, warisan).
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

### S-03: Isi laporan bulanan identik 19.0 vs 20.0 (Cross-Version Compare)
**Level:** Main Flow
**Precondition:** data seed identik di kedua instance.
**Mode eksekusi:** AI-otomatis (skrip seed + `recreate_view` via `odoo-bin shell` di kedua versi)
**Steps:** seed → rebuild view → cetak semua baris `stock.history.view` produk → `diff`.
**Expected:** baris (tanggal, income, outcome, qty) identik.
**Actual:** **15/15 baris identik** (`evidence/cvc_rows_19.txt` vs `cvc_rows_20.txt`, `diff` kosong): saldo pembuka 100 di baris 2025-08-31, +40 (Mar 2026), −15 (Jun), +7 retur (Aug), Sep in 9 / out 4, qty akhir 137.
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

### S-04: Graph, Pivot, List menampilkan angka yang sama dengan 19.0
**Level:** Main Flow
**Precondition:** S-03.
**Mode eksekusi:** AI-interaktif Playwright (19.0 & 20.0 live)
**Steps:** dari laporan: lihat graph → pindah ke List (ambil semua baris) → Pivot (header & baris).
**Expected:** 13 baris dalam jendela 12 bulan (`date >= date_debut`), kolom & label seperti BSL-012/014.
**Actual:** List 20.0: 13 baris, kolom `Date | Product | Category | Uom | Input | Output | Stock Quantity uom`, 6 desimal (`digits=(8,6)`) — **identik baris-per-baris dengan List 19.0** (`evidence/qa19_list.json` vs `qa20_list.json`). Graph 20.0 (`evidence/qa20_graph.png`): bar qty Sep 2025 → Sep 2026 (100…140…125…132…137). Pivot 20.0: kolom per bulan (Sep 2025–Sep 2026), measure Input/Output/"Stock Quantity UOM" (`evidence/qa20_pivot.json`). Kolom Category kosong di KEDUA versi (produk seed tanpa kategori) — bukan regresi.
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

### S-05: Ikon tombol Stock History tampil (Font Awesome → Material Symbols)
**Level:** Detail
**Precondition:** form produk.
**Mode eksekusi:** AI-interaktif Playwright (visual, kedua versi) + tour form (DOM)
**Steps:** buka form → buka dropdown More → periksa ikon & screenshot.
**Expected:** ikon bar sinyal ter-render (bukan kosong/teks liar) — UX setara 19.0 (BSL-013, DIFF-02).
**Actual:** 20.0: `<i class="o_button_icon oi me-1" data-icon="android_cell_5_bar">`, font `Material Symbols Outlined`, `::before` = ligature, kotak 26×21 px (satu glyph). 19.0: `fa fa-fw fa-signal`, font FontAwesome, 27×21 px. Screenshot `evidence/qa19_more_dropdown.png` vs `qa20_more_dropdown.png` — sama-sama ikon bar sinyal.
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

### S-06: Filter Group By pada laporan
**Level:** Detail
**Precondition:** laporan terbuka.
**Mode eksekusi:** AI-interaktif Playwright (20.0) + Tour (Community)
**Steps:** buka dropdown search → pilih "By products".
**Expected:** 4 filter group-by (By products, Date, Category, UOM) ada & berfungsi (BSL-012).
**Actual:** opsi `By products, Date, Category, UOM` (+ Custom Group native); klik "By products" → facet aktif, grup `QA20 CVC Product 13 records`. Tour step 12/12 juga memverifikasi "By products".
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

### S-07: Transfer internal→internal tetap dihitung ganda (bug warisan dipertahankan)
**Level:** Detail
**Precondition:** move stock→shelf internal 4 unit bulan ini.
**Mode eksekusi:** AI-otomatis (CVC) + Integration `test_ac_03_02`
**Steps:** lihat baris bulan berjalan.
**Expected:** 4 unit masuk income DAN outcome (MF-02), sama seperti 19.0.
**Actual:** baris Sep 2026 di kedua versi: `in=9` (5 supplier + 4 internal) / `out=4` (internal) — identik.
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

### S-08: Filter multi-company
**Level:** Detail
**Precondition:** move di company aktif.
**Mode eksekusi:** AI-otomatis (Integration `test_ac_04_01`)
**Steps:** rebuild dengan company benar vs company id tidak cocok.
**Expected:** income 0 untuk company tidak cocok (BSL-006).
**Actual:** PASS di Run C & Run E (log `run-community-20260924-153554.log`, `run-enterprise-20260924-154035.log`) dengan fixture tanggal yang kini terverifikasi (MF-11).
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI] (automated test, Step 9)

### S-09: Akses baca terbuka untuk semua user (ACL warisan dipertahankan)
**Level:** Negative
**Precondition:** user internal tanpa grup Inventory; user portal.
**Mode eksekusi:** AI-otomatis (Integration `test_ac_05_01/03/04`) + baseline 19.0
**Steps:** search `stock.history.view` sebagai kedua user; cek record `ir.access`.
**Expected:** keduanya BISA baca — perilaku 19.0 (MF-03), bukan diperketat/dilonggarkan.
**Actual:** PASS di 20.0 (Run C/E); test portal yang sama PASS di kode 19.0 (baseline Step 9) → padanan `base.group_everyone` `crud` terbukti.
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI] (automated test, Step 9)

### S-10: Create/write langsung ke model laporan ditolak database
**Level:** Negative
**Mode eksekusi:** AI-otomatis (Integration `test_ac_05_02`)
**Expected:** gagal di level DB (VIEW Postgres), BSL-008.
**Actual:** PASS Run C/E.
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI] (automated test, Step 9)

### S-11: `recreate_view` tidak bisa dipanggil lewat RPC & menolak argumen non-integer (fix keamanan 20.0)
**Level:** Negative
**Mode eksekusi:** AI-otomatis (Integration `test_ac_07_01/02`)
**Expected:** RPC ditolak `AccessError`; argumen non-integer → `ValueError`; tombol tetap jalan (SCOPE-02, MF-10 — **perubahan disengaja, berbeda dari 19.0**).
**Actual:** PASS Run C/E. Tombol tetap jalan di live 20.0 (S-01).
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI] (automated test, Step 9)

### S-12: Posisi tombol di instance Enterprise (dropdown More) sama dengan 19.0
**Level:** Detail
**Mode eksekusi:** AI-interaktif Playwright (kedua versi live)
**Steps:** buka form produk di Enterprise, catat stat button yang terlihat & isi dropdown More.
**Expected:** layout sama dengan 19.0 Enterprise.
**Actual:** kedua versi: terlihat `On Hand/Forecasted`, `Documents`, `Reordering Rules`, `In/Out`, lalu **More** berisi `Stock History` + `Quality Points` — identik. (Overflow `ButtonBox` identik 19/20, lihat `09_DEV_TESTING.md` loop #1.)
**Status:** [x] Pass
**Provenance:** [DIKONFIRMASI]

---

## Cross-Version Compare (prosedur `templates/CROSS_VERSION_COMPARE.md`)

1. **Static diff dulu:** `git diff migration/19.0 migration/20.0 -- product_history_report/models` = hanya SCOPE-02 (`@api.private` + casting integer; body SQL identik). Kandidat regresi dari diff: tidak ada selain yang disengaja.
2. **Live, data identik:** S-03 (data), S-04 (tiga view), S-05 (ikon), S-12 (layout Enterprise).

| Temuan | Klasifikasi | Keterangan |
|---|---|---|
| Ikon `fa-signal` → `android_cell_5_bar` | Disengaja (DIFF-02) | Visual setara |
| Breadcrumb 20.0 memendekkan jadi `… / QA20 CVC Product / Stocks Histories` (19.0: `Products / QA20 CVC Product / Stocks Histories`) | `NATIVE-DIFF` | UI web client 20.0, bukan modul |
| Angka laporan, jumlah baris, kolom, label, presisi | Identik | — |
| RPC `recreate_view` ditolak | Disengaja (SCOPE-02) | Tidak terlihat di UI |
| Helper test menimpa tanggal fixture di 20.0 | Test-harness (MF-11) | Diperbaiki di test, bukan kode modul |
| `RecursionError` OdooBot saat bootstrap web client pertama di 20.0 Enterprise | `NATIVE-DIFF` (bug native) | MF-12 — tidak menyentuh modul, sekali terjadi |

## Loop-back ke Step 9

| Temuan | Tindakan |
|---|---|
| **MF-11:** di 20.0 `UPDATE stock_move_line SET date` di helper `_make_move` tertimpa write ORM tertunda setelah `button_validate()` (dibuktikan probe shell: 19.0 tanggal tersimpan `2025-07-01`, 20.0 jadi `2026-09-24`). Akibatnya test AC-02-01/AC-03-01 di 20.0 sempat hijau tanpa menguji tanggal lama. | Helper diperbaiki: `env.flush_all()` sebelum UPDATE + assert tanggal benar-benar tersimpan. Re-run Run C `0 failed of 17`, Run E `0 failed of 17` — test kini benar-benar menguji saldo pembuka. |

## Ringkasan per Level

| Level | Skenario | Jumlah |
|---|---|---|
| Smoke | S-01, S-02 | 2 |
| Main Flow | S-03, S-04 | 2 |
| Detail | S-05, S-06, S-07, S-08, S-12 | 5 |
| Negative | S-09, S-10, S-11 | 3 |

## Rekap Provenance

| Provenance | Jumlah | Skenario |
|---|---|---|
| `[DIKONFIRMASI]` | 12 | S-01..S-12 (S-08..S-11 via automated test Step 9) |
| `[HASIL-BACA]` | 0 | — |
| `[HASIL-BACA-MURNI]` | 0 | — |
| `[PERLU-KEPUTUSAN]` | 0 | — |

## Human QA Checklists

Digenerate di `human_qa/` (`00_README.md`, `01_SMOKE.md`, `02_MAIN_FLOW.md`, `03_DETAIL.md`, `04_NEGATIVE.md`).

## Verdict

- [x] ✅ Lulus — 12/12 skenario `[DIKONFIRMASI]`, 0 Fail, Cross-Version Compare 19.0↔20.0 tanpa regresi. Lanjut ke Step 11.
- [ ] ⚠️ Lulus Bersyarat
- [ ] ❌ Ada kegagalan
