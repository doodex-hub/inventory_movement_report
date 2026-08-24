# Migration Intake — product_history_report

**Step:** 1 — Intake & Scope
**Versi:** 17.0 → 18.0
**Tanggal:** 2026-08-24
**Status:** 🔄 Sedang dikerjakan — menunggu review user untuk menutup gate

---

## 0. Folder Referensi

- [x] `native-target` (Community, checkout 18.0) — sudah ada di disk. Path: `D:/Kuncoro/doodex/repo/odoo18`
- [x] `native-source` (Community, checkout 17.0) — sudah ada di disk. Path: `D:/Kuncoro/doodex/repo/odoo17`
- [x] `native-target-enterprise` — **dikonfirmasi dev tidak dipakai.** Manifest cuma `depends: ['base', 'stock']`, keduanya Community. Baris deny terkait sudah dihapus dari `.claude/settings.json`.
- [x] `third-party-source`/`third-party-target` — **dikonfirmasi dev tidak dipakai.** Tidak ada dependency OCA/vendor.

### 0a. Konfirmasi Branch/Versi `source-codebase` & `target-codebase`

- [x] Folder `source-codebase` — branch `migration/17.0_source`. Dikonfirmasi dev: dibuat sebagai copy dari `backfill/17.0` (commit `44ad208`, hasil kerja `doc-dev-backfill` sebelumnya di modul ini, Step 01-07 selesai). Path: `D:/Kuncoro/doodex/repo/inventory-movement-report-migration-18-source`
- [x] Folder `target-codebase` — branch `migration/18.0`, juga dibuat dari `backfill/17.0` (commit dasar sama, `44ad208`). Path: `D:/Kuncoro/doodex/repo/inventory-movement-report-migration-18` (repo ini)
- [x] Dikonfirmasi dua clone fisik terpisah (bukan symlink/alias) — diverifikasi via `ls` panggilan tool terpisah setelah `git clone`.
- [x] Versi Odoo semantik: **17.0 → 18.0**, dikonfirmasi eksplisit dev.

### 0b. Gate: Path Absolut di `.claude/settings.json`

- [x] `ABS_PATH_SOURCE_CODEBASE` → `D:/Kuncoro/doodex/repo/inventory-movement-report-migration-18-source`
- [x] `ABS_PATH_MIGRATION_TOOL` → `D:/Kuncoro/doodex/repo/migration-tool-project/migration-tool`
- [x] `ABS_PATH_NATIVE_TARGET` → `D:/Kuncoro/doodex/repo/odoo18`, `ABS_PATH_NATIVE_SOURCE` → `D:/Kuncoro/doodex/repo/odoo17` (diisi juga meski tidak wajib di checklist minimum, path sudah diketahui)
- [x] `ABS_PATH_NATIVE_TARGET_ENTERPRISE`/`ABS_PATH_NATIVE_SOURCE_ENTERPRISE`/`ABS_PATH_THIRD_PARTY_SOURCE`/`ABS_PATH_THIRD_PARTY_TARGET` — baris deny dihapus seluruhnya (tidak dipakai, dikonfirmasi dev).

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Nama repo GitHub vs nama modul berbeda** — repo `doodex-hub/inventory_movement_report` isinya modul teknis bernama `product_history_report`. Dikonfirmasi dev bukan kesalahan — modul yang dimigrasi memang `product_history_report`, repo dinamai sesuai fungsi bisnisnya (laporan pergerakan inventory).
2. **Baseline spec bukan dari nol** — modul ini sudah pernah lewat `doc-dev-backfill` (2026-08-07, Step 01-07 selesai, 8/8 integration test PASS nyata). Baseline spec Step 1 migrasi ini (`01b_BASELINE_SPEC.md`) dibangun dari `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` + `FINDINGS.md` lama (cross-check ke kode, bukan disalin buta) — diarsipkan di `doc-dev/backfill/`.
3. **4 bug/quirk source WAJIB dipertahankan identik di 18.0** (bukan diperbaiki, sesuai `CLAUDE_TEMPLATE.md` §Source of Truth) — dibawa dari `doc-dev/backfill/FINDINGS.md`, sudah dicatat ulang sebagai `MF-01`..`MF-04` di `FINDINGS.md` project ini:
   - Race condition SQL view global `stock_history_view` (prioritas Tinggi, F-01 lama)
   - Transfer internal→internal dihitung ganda di income+outcome (F-02 lama, sudah dikonfirmasi lewat test eksekusi nyata)
   - ACL `stock.history.view` terbuka semua user internal tanpa `group_id` (F-04 lama, juga dikonfirmasi test)
   - ORM cache stale kalau `recreate_view()` dipanggil >1x dalam environment sama (F-09 lama)
4. Sifat migrasi: **port kode saja** (belum ada data produksi di 18.0) — step 7 (Data Migration Scripts) di-skip, dikonfirmasi dev.
5. Source dibekukan selama migrasi (tidak aktif dikembangkan) — `SYNC_POLICY.md` tidak diperlukan.
6. Tidak ada dependency Enterprise/OCA — dependency modul cuma `base`+`stock` (Community core), keduanya dipastikan tetap ada di 18.0 (validasi API-level menyusul di Step 2).
7. Modul tidak punya Controllers aktif, assets/JS/Owl custom, field JSON/dynamic model, atau `attrs=`/`states=`/domain dinamis di view — lihat §2b, ini menyederhanakan Step 6 (beberapa fase langsung N/A).

---

## 1. Modul & Scope

- Modul yang dimigrasi: **product_history_report** (satu modul, tidak multi-module)
- Deskripsi singkat: menambah laporan riwayat pergerakan stok (~13 bulan) per produk, diakses lewat tombol statistik "Stock History" di form `product.template`. Backend murni SQL view (`stock.history.view`, `_auto=False`) + satu method Python yang drop+recreate view itu per klik.
- Modul-modul saling depend: N/A, hanya satu modul.

## 2. Dependency Map (auto-scan)

| Dependency | Tipe | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `base` | Native Community | Ya (core, selalu ada) | — |
| `stock` | Native Community | Ya (core, selalu ada) | Validasi breaking change API (`stock.move`, `stock.move.line`, lokasi) jadi fokus utama Step 2 |

Dependency opsional yang dicek runtime (mis. `'hr.employee' in self.env`): tidak ditemukan — modul tidak melakukan runtime dependency check apapun.

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak | `controllers/controllers.py` murni boilerplate scaffold (`http.Controller` di-comment semua), tidak expose route | D1 → N/A |
| Assets/CSS/JS custom | ☐ Tidak | Tidak ada `static/src/`, tidak ada key `assets` di manifest. `static/description/` cuma marketing asset (icon/banner) | D2, E, F → N/A |
| Komponen Owl/JavaScript custom | ☐ Tidak | Tidak ada file `.js` di modul | E, F → N/A |
| Field JSON, relasi berantai (>2 level), atau dynamic model creation | ☐ Tidak | Tidak ditemukan di `models/product_template.py`/`models/stock_history_view.py` | B2 → N/A |
| View pakai `attrs=`/`states=`/domain=/context= dinamis | ☐ Tidak (domain statis) | `views/stock_history_view.xml:11-14` cuma `domain="[]"` + `context="{'group_by':...}"` statis untuk filter groupby — bukan `attrs=`/`states=`, bukan domain computed | C2 → N/A |

**Kesimpulan:** fase D1, D2, E, F, B2, C2 di Step 6 langsung dinyatakan N/A pada Applicability Check — modul ini murni backend (model Python + SQL view + security ACL + dua file view XML statis), tidak ada aspek frontend/JS/dynamic yang butuh treatment khusus.

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi — instalasi baru di versi target)
- [ ] Upgrade instance (ada data produksi — step 7 wajib jalan)

## 4. Baseline Spec / Characterization Test (gate)

- [x] Cek dulu: apakah modul punya `FUNCTIONAL_SPEC.md` lama di `source-codebase`? **Ya** — hasil kerja `doc-dev-backfill` sebelumnya, sekarang diarsipkan di `doc-dev/backfill/` (root `target-codebase`, bukan di dalam `source-codebase` — tapi isinya membahas kode yang identik dengan `source-codebase` saat ini, commit dasar sama `44ad208`).
  - Proses: dibaca `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` + `01B_ACCEPTANCE_CRITERIA.md` sebagai draft awal, cross-check tiap klaim ke kode aktual di `source-codebase`. Semua BR-01..BR-06 di spec lama cocok dengan kode saat ini (tidak ada penyimpangan ditemukan — commit dasarnya sama persis, `44ad208`, jadi tidak ada drift). Hasil: seluruh klaim ditandai `[MATCH]` di `01b_BASELINE_SPEC.md`, bukan `[GAP]`.
- [x] `01b_BASELINE_SPEC.md` sudah diisi — lihat file terpisah.

### 4a. Dokumen Pelengkap Lain

- [x] Ditanyakan ke dev secara implisit lewat konteks bootstrap — dokumen pelengkap yang tersedia: `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`, `01B_ACCEPTANCE_CRITERIA.md`, `doc-dev/backfill/test/03B_TEST_PLAN.md`, `04A_DEV_TESTING.md`, `07_QA_TESTING.md`, dan `doc-dev/backfill/FINDINGS.md` (9 finding, 5 `[PERLU-KEPUTUSAN]`). Semua sudah dibaca dan dipakai sebagai input `01b_BASELINE_SPEC.md`/`FINDINGS.md` project ini. Tidak ada dokumen lain (manual guide/PRD/Confluence) yang disebutkan dev.

**Tidak boleh lanjut ke step 2 sebelum `01b_BASELINE_SPEC.md` terisi** — sudah terpenuhi, lihat file terpisah.

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — source module dibekukan selama migrasi berjalan.

## 5. Scope Boundary

- Yang harus tetap identik pasca migrasi: seluruh business rule BR-01..BR-06 (`01b_BASELINE_SPEC.md`), termasuk 4 bug/quirk yang harus dipertahankan (`MF-01`..`MF-04` di `FINDINGS.md`) — race condition SQL view, double-count transfer internal, ACL longgar, ORM cache stale.
- Yang sengaja diubah/di-drop: tidak ada — port kode saja, tidak ada perubahan scope yang disepakati di intake ini.

## 6. Constraint

- Deadline: belum disebutkan dev — belum relevan/tidak urgent untuk tahap intake ini.
- Owner tiap step: belum disebutkan dev — akan ditanyakan kalau/ketika relevan (mis. sebelum Step 10 QA/Step 11 UAT butuh penunjukan QA/PM).
