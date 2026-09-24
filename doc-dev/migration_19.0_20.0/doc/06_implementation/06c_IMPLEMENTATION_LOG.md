# Implementation Log — product_history_report

**Step:** 6 — Code Migration
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-24
**Status:** ✅ Selesai (step non-gate) — G2 PASS
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `migration-tool/templates/06a_CODE_MIGRATION_PHASES.md`

---

## Aturan

Disiplin per fase A1→G2 (`06a`). Mode eksekusi G1/G2: **C (AI jalankan langsung)**, dipilih dev di intake 2026-09-24. Environment: `docker-env/` baru untuk 20.0 — `Dockerfile` (python:3.12-slim-bookworm + dependency `odoo20/requirements.txt` + Google Chrome), `docker-compose.yml` (compose name `product_history_report_migration_20`, port host 8093, `odoo20`/`enterprise20` di-mount read-only), `run-test.sh` (wajib: `down -v` sebelum/sesudah, `MSYS_NO_PATHCONV=1`, sanity-check jumlah test, param `EDITION`/`NO_TESTS`). `docker-env/Dockerfile.target` (19.0) dihapus — versi lama tetap ada di branch `migration/19.0`.

## Applicability Check

| Fase | Relevan? | Bukti/alasan (dari `01a` §2b) |
|---|---|---|
| C1 | ☑ Ya | `views/views.xml` atribut `icon` (DIFF-02) |
| B2 | ☐ Tidak | Tidak ada field JSON/relasi berantai/dynamic model |
| C2 | ☐ Tidak | Domain/context statis |
| D1 | ☐ Tidak | `controllers/` boilerplate di-comment |
| D2 | ☐ Tidak | Tidak ada asset aplikatif (hanya `web.assets_tests`, glob tidak berubah) |
| E | ☐ Tidak | Tidak ada Owl/JS aplikatif (tour = test code, dicatat di G2) |
| F | ☐ Tidak | Otomatis N/A (E N/A) |

## Tabel Ringkas Status Fase

| Fase | Status | Tanggal |
|---|---|---|
| A1 | ✅ `version` → `20.0.1.0.0` | 2026-09-24 |
| A2 | ✅ N/A de facto — tidak ada `<tree>` (sudah `<list>` sejak 17→18); G1 #1 tetap dijalankan | 2026-09-24 |
| G1 (checkpoint Fase A) | ✅ #1 FAIL (ekspektasi, DIFF-01) → #2 PASS | 2026-09-24 |
| A3 | ✅ `ir.model.access.csv` → `ir.access.csv` (`base.group_everyone`, `crud`) | 2026-09-24 |
| A4 | ✅ Tidak ada perubahan (folder `security/` tetap, isi baru) | 2026-09-24 |
| A5 | ✅ Tidak ada perubahan (`models/*.py` byte-identik 19.0) | 2026-09-24 |
| A6 | ✅ README/LISEZMOI modul "Odoo version 17.0" → "20.0" | 2026-09-24 |
| SCOPE-01 | ✅ `static/description/**` = branch `19.0` (59 file), key `images` | 2026-09-24 |
| B1 | ✅ Tidak ada perubahan | 2026-09-24 |
| B2 | N/A — dikonfirmasi Applicability Check | — |
| C1 | ✅ `icon="fa-signal"` → `icon="android_cell_5_bar"` | 2026-09-24 |
| C2, D1, D2, E, F | N/A — dikonfirmasi Applicability Check | — |
| G2 (validasi akhir/runtime) | ✅ PASS — 13/13 test modul (Run C) | 2026-09-24 |

## Riwayat Percobaan G1 (Install Test)

| # | Dijalankan setelah fase | Mode | Hasil | Error (kalau fail) | Tanggal |
|---|---|---|---|---|---|
| 1 | A1 (A2 N/A) | C | ☑ Fail (ekspektasi) | `KeyError: 'ir.model.access'` saat `loading product_history_report/security/ir.model.access.csv` → "Failed to initialize database" (log `docker-env/logs/run-community-20260924-141056.log`). Membuktikan DIFF-01 empiris: nama file lama tidak diterima, tidak ada backward-compat. Warning `--without-demo: since 19.0, invalid boolean value: 'all'` → `run-test.sh` diperbaiki ke `--without-demo=true` (default 19.0+ memang tanpa demo). | 2026-09-24 |
| 2 | A3 | C | ☑ Pass | Exit 0, `ir.access.csv` + 2 view ter-load, "Modules loaded." Sisa log: `WARNING The model stock.history.view has no _description` (warisan, DIFF-09) + `ERROR Model stock.history.view has no table.` ×2 (lihat MF-09 — perilaku warisan `_auto=False` + view baru dibuat saat tombol diklik; logika pengecekan identik di `odoo19/odoo/orm/registry.py:996`) | 2026-09-24 |

## Entri

### [A1] Manifest Bootstrap
- **Scope:** `__manifest__.py`
- **Aksi:** `version` `19.0.1.0.0` → `20.0.1.0.0` (DIFF-04).
- **Risiko:** rendah.
- **Status:** ✅

### [A2] XML Tree → List
- **Aksi:** tidak ada — grep `<tree` 0 match. G1 #1 dijalankan di titik ini sesuai `06a`.
- **Status:** ✅

### [A3] Security Hardening — `ir.access` (DIFF-01)
- **Scope:** `security/`, `__manifest__.py` `data`
- **Aksi:** hapus `security/ir.model.access.csv`; buat `security/ir.access.csv`:
  ```
  id,name,model_id,group_id/id,operation,domain
  access_stock_history_view,stock_history_view,stock.history.view,base.group_everyone,crud,
  ```
  Manifest `data[0]` → `'security/ir.access.csv'` (posisi sama seperti sebelumnya).
- **Verifikasi silang (resmi):** skrip Odoo `odoo-bin upgrade_code --script 19.4-00-ir-access` dijalankan di container terhadap salinan `git archive migration/19.0 product_history_report` (scratchpad, bukan repo). Output skrip: `updated: security/ir.access.csv`, `deleted: security/ir.model.access.csv`, `updated: __manifest__.py` — isi `ir.access.csv` **identik byte-per-byte** dengan file di atas (`diff` kosong). Satu-satunya beda: skrip menaruh entry manifest di AKHIR `data`; kita pertahankan di posisi pertama (disengaja, `03_MIGRATION_SPEC.md` §2).
- **Risiko:** tinggi → rendah (dua bukti: skrip resmi + G1 #2 + test AC-05-01/03/04).
- **Status:** ✅

### [A4] Skeleton — tidak ada perubahan. ✅
### [A5] Python API — tidak ada perubahan; `git diff migration/19.0 -- product_history_report/models product_history_report/controllers product_history_report/__init__.py` kosong. ✅

### [A6] Housekeeping README
- **Aksi:** `product_history_report/README.md:71` "Odoo version: 17.0" → "20.0"; `product_history_report/LISEZMOI.md:69` "Version d'Odoo : 17.0" → "20.0" (basi sejak 17→18). README/LISEZMOI di root repo (salinan) tidak disentuh — di luar scope A6 (level modul), dicatat MF-08.
- **Status:** ✅

### [SCOPE-01] Aset App Store (disetujui dev, MF-06)
- **Aksi:** `git checkout 19.0 -- product_history_report/static/description` + `git rm` 5 file yang sudah dihapus di branch 19.0 (`banner.png`, `assets/doodex_odoo.png`, `assets/image_inventory_move{,2,3}.png`). Verifikasi: `git diff --cached --name-only 19.0 -- product_history_report/static/description` = 0 file, total 59 file. Key `images` → `['static/description/banner.gif', 'static/description/icon.png']` — setelah ini `git diff 19.0 -- __manifest__.py` hanya `version` + path ACL. `index.html` tidak diedit manual (MF-08).
- **Status:** ✅

### [B1] Model Risiko Rendah — tidak ada perubahan. ✅

### [C1] View Sederhana — ikon (DIFF-02)
- **Aksi:** `views/views.xml` `icon="fa-signal"` → `icon="android_cell_5_bar"` (1 atribut).
- **Status:** ✅ (dibuktikan arch + DOM di G2)

### [G2] Validasi Akhir — penyesuaian test + run penuh
- **Test diubah:** `tests/test_product_history_report.py` `_make_move`: `'product_uom'` → `'uom_id'` (DIFF-03).
- **Test baru:** `test_ac_01_04_button_icon_is_material_signal`, `test_ac_05_03_acl_record_is_group_everyone_crud`, `test_ac_05_04_read_open_for_portal_user` (+ import `lxml.etree`); `tests/test_stock_history_tour.py`: `setUp` menyimpan `self.product`, `test_stock_history_tour` di-skip hanya jika `web_enterprise` terinstal (DIFF-12), test baru `test_stock_history_form_tour`; tour baru `static/tests/tours/stock_history_form_tour.js` (4 step). Tour lama `stock_history_tour.js` tidak diubah.
- **Run C (Community):** `./run-test.sh` → exit 0, log `docker-env/logs/run-community-20260924-142152.log`: `0 failed, 0 error(s) of 15 tests` — 13 method modul ini ter-start (11 Integration + 2 Tour) + `WebSuite.test_unit_desktop`/`MobileWebSuite.test_unit_mobile` milik `web` (selesai ~2 ms, modul tidak punya test hoot). Tour `stock_history_form_tour` **4/4 step "tour succeeded"** (step 1 = selector `button[name="action_open_stock_history"] i.o_button_icon[data-icon="android_cell_5_bar"]` ketemu → ikon Material benar-benar dirender); tour `stock_history_tour` **12/12 "tour succeeded"** (selector navigasi 19.0 semua masih valid di 20.0).
- **Status:** ✅ PASS

## Temuan di Luar Spec

- MF-09 (baru) — `ERROR Model stock.history.view has no table.` saat install/registry load (lihat `FINDINGS.md`) — perilaku warisan, dikonfirmasi di baseline 19.0 pada Step 9.
- `--without-demo=all` di template `run-test.sh.template`/docker-compose sudah tidak valid sejak 19.0 (Odoo log warning, tetap "assume True") — kandidat perbaikan template (migration record).

## Kontribusi ke Knowledge Base

Dicatat di `migration-tool/migration-records/product_history_report_19.0_20.0/SUMMARY.md` (bukan langsung ke `knowledge/`): verifikasi empiris G1 #1 untuk entry `ir.access`, cara memakai `odoo-bin upgrade_code --script 19.4-00-ir-access` sebagai oracle konversi, gotcha `--without-demo=all`.
