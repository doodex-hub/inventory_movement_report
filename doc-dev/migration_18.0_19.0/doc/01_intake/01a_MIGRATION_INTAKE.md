# Migration Intake — product_history_report

**Step:** 1 — Intake & Scope
**Versi:** 18.0 → 19.0
**Tanggal:** 2026-08-26
**Status:** 🔄 Sedang dikerjakan — menunggu review user untuk menutup gate

---

## 0. Folder Referensi

- [x] `native-target` (19.0) — sudah ada di disk. Path: `D:/Kuncoro/doodex/repo/enterprise19.0` — **BUKAN addons-only**, ini folder Odoo 19.0 penuh (`odoo/`, `setup.py`, `MANIFEST.in`) dengan modul Community DAN Enterprise sudah tergabung di dalam `odoo/addons/` yang sama (lesson `advanced_sales_analysis` 18.0→19.0, project 18→19 pertama lewat `migration-tool`). Dipakai sekaligus sebagai `native-target-enterprise` (path sama). Juga BUKAN git repo (hasil extract, tidak ada `.git/`).
- [x] `native-source` (Community, checkout 18.0) — sudah ada di disk. Path: `D:/Kuncoro/doodex/repo/odoo18`
- [ ] **`native-target-enterprise`/`native-source-enterprise` — dependency Enterprise?** Auto-scan §2 di bawah TIDAK menemukan apapun (manifest cuma `depends: ['base', 'stock']`, sama seperti project 17→18). **Perlu dikonfirmasi eksplisit ke dev:** apakah ada dependency Enterprise yang tidak kelihatan dari manifest (runtime check dsb)? Belum ditanyakan di sesi ini — dicatat sebagai open item, TIDAK menghalangi gate step 1 (modul ini historically tidak pernah punya dependency Enterprise di 17→18).
- [ ] **`third-party-source`/`third-party-target`** — auto-scan tidak menemukan dependency OCA/vendor. Sama seperti di atas, belum dikonfirmasi eksplisit ke dev — open item, tidak menghalangi gate.

### 0a. Konfirmasi Branch/Versi `source-codebase` & `target-codebase`

- [x] Folder `source-codebase` — branch `migration/18.0`. Dikonfirmasi dari instruksi dev di chat ("source copy dari migration/18.0"). Ini branch project migrasi 17.0→18.0 SEBELUMNYA yang sudah SELESAI (semua 11 step lulus gate, commit `978a384`) — jadi kode di sini adalah kode `product_history_report` versi 18.0 yang sudah matang/lulus UAT, bukan versi 17.0. Path: `D:/Kuncoro/doodex/repo/inventory-movement-report-migration-19-source`
- [x] Folder `target-codebase` — branch `migration/19.0_target` (baru dibuat 2026-08-26 dari `origin/migration/18.0`, sesuai instruksi dev). Path: `D:/Kuncoro/doodex/repo/inventory-movement-report-migration-19` (repo ini)
- [x] Dikonfirmasi dua clone fisik terpisah (bukan symlink/alias) — diverifikasi via `ls` di panggilan tool terpisah setelah `git clone` (lesson `advanced_sales_analysis`: verifikasi clone WAJIB di panggilan terpisah, jangan percaya laporan sukses di panggilan yang sama).
- [x] Versi Odoo semantik: **18.0 → 19.0**, dikonfirmasi eksplisit dev di chat.

### 0b. Gate: Path Absolut di `.claude/settings.json`

- [x] `ABS_PATH_SOURCE_CODEBASE` → `D:/Kuncoro/doodex/repo/inventory-movement-report-migration-19-source`
- [x] `ABS_PATH_MIGRATION_TOOL` → `D:/Kuncoro/doodex/repo/migration-tool-project/migration-tool`
- [x] `ABS_PATH_NATIVE_TARGET`/`ABS_PATH_NATIVE_TARGET_ENTERPRISE` → `D:/Kuncoro/doodex/repo/enterprise19.0` (path sama, folder gabungan)
- [x] `ABS_PATH_NATIVE_SOURCE` → `D:/Kuncoro/doodex/repo/odoo18`
- [ ] `ABS_PATH_NATIVE_SOURCE_ENTERPRISE`/`ABS_PATH_THIRD_PARTY_SOURCE`/`ABS_PATH_THIRD_PARTY_TARGET` — baris deny TIDAK ditambahkan (tidak ada indikasi dipakai), tapi belum ada konfirmasi eksplisit "tidak dipakai" dari dev untuk project ini (lihat open item §0 di atas).

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **2 open item belum dikonfirmasi eksplisit dev** (tidak menghalangi gate, tapi perlu jawaban sebelum Step 2 dianggap benar-benar tuntas): (a) ada dependency Enterprise/OCA yang tidak kelihatan dari manifest? (b) folder referensi Enterprise/third-party memang tidak diperlukan? Auto-scan mengindikasikan "tidak ada" (konsisten dengan project 17→18), tapi belum jawaban eksplisit dev untuk project INI.
2. **Baseline spec bukan dari nol** — modul ini sudah lulus penuh migrasi 17.0→18.0 (`doc-dev/migration_17.0_18.0/doc/`, 9/9 test PASS termasuk Tour test, UAT disetujui dev 2026-08-24). `01b_BASELINE_SPEC.md` project ini dibangun dari `01b_BASELINE_SPEC.md` project 17→18 (yang mendokumentasikan behavior versi 18.0 — versi SOURCE project ini sekarang) + cross-check langsung ke kode `source-codebase`/`target-codebase` (identik, sama-sama dari commit `978a384`).
3. **4 bug/quirk source WAJIB dipertahankan identik di 19.0** (bukan diperbaiki) — dibawa dari `doc-dev/migration_17.0_18.0/doc/FINDINGS.md` (`MF-01`..`MF-04`, aslinya `F-01`/`F-02`/`F-04`/`F-09` dari `doc-dev/backfill/FINDINGS.md`), dicatat ulang di `FINDINGS.md` project ini:
   - Race condition SQL view global `stock_history_view` (prioritas Tinggi)
   - Transfer internal→internal dihitung ganda di income+outcome (prioritas Sedang, dikonfirmasi test eksekusi nyata)
   - ACL `stock.history.view` terbuka semua user internal tanpa `group_id` (prioritas Rendah, dikonfirmasi test)
   - ORM cache stale kalau `recreate_view()` dipanggil >1x dalam environment sama (prioritas Rendah)
   - Ketiganya belum pernah ada "Keputusan pemilik modul" — masih terbuka sejak `doc-dev-backfill` (2026-08-07).
4. Sifat migrasi: **port kode saja** (belum ada data produksi) — **dikonfirmasi dev 2026-08-26**, step 7 (Data Migration Scripts) di-skip.
5. Source dibekukan selama migrasi — **dikonfirmasi dev 2026-08-26**, `SYNC_POLICY.md` tidak diperlukan.
6. Modul tidak punya Controllers aktif, dynamic model/field JSON, atau `attrs=`/`states=`/domain dinamis di view — lihat §2b. Ada 1 file JS (`static/tests/tours/stock_history_tour.js`, ditambahkan Step 9 project 17→18) tapi itu **test tour script** (`web.assets_tests`), bukan asset frontend aplikatif — lihat catatan §2b.
7. **Ini project 18→19 KEDUA lewat `migration-tool`** (pertama: `advanced_sales_analysis`, selesai 2026-08-26) — `knowledge/version-diffs/18-to-19.md` sudah punya 1 entry terverifikasi dari project nyata (rename `sale.order.line.tax_id`→`tax_ids`), tapi modul ini tidak depend ke `sale`, jadi entry itu kemungkinan tidak relevan langsung — tetap dicek ulang di Step 2 untuk breaking change spesifik `base`/`stock`.

---

## 1. Modul & Scope

- Modul yang dimigrasi: **product_history_report** (satu modul, tidak multi-module)
- Deskripsi singkat: menambah laporan riwayat pergerakan stok (~13 bulan) per produk, diakses lewat tombol statistik "Stock History" di form `product.template`. Backend murni SQL view (`stock.history.view`, `_auto=False`) + satu method Python yang drop+recreate view itu per klik.
- Modul-modul saling depend: N/A, hanya satu modul.

## 2. Dependency Map (auto-scan)

| Dependency | Tipe (Native Community / Native Enterprise / OCA / Custom) | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `base` | Native Community | Ya (core, selalu ada) | — |
| `stock` | Native Community | Ya (core, selalu ada) | Validasi breaking change API (`stock.move`, `stock.move.line`, lokasi) di Odoo 19.0 jadi fokus utama Step 2 |

Dependency opsional yang dicek runtime (mis. `'hr.employee' in self.env`): tidak ditemukan — modul tidak melakukan runtime dependency check apapun (sama seperti temuan project 17→18, dikonfirmasi ulang dari kode `source-codebase` saat ini).

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak | `controllers/controllers.py` murni boilerplate scaffold (`http.Controller` di-comment semua), tidak expose route | D1 → N/A |
| Assets/CSS/JS custom | ☐ Tidak (aplikatif) — ADA 1 file JS test | `static/tests/tours/stock_history_tour.js`, terdaftar di manifest key `assets` → `web.assets_tests` (test tour, ditambahkan Step 9 project 17→18, BUKAN frontend aplikatif). Tidak ada `static/src/` | D2, E, F → N/A untuk kode aplikatif; tour test perlu dicek ulang di Step 9 project ini kalau API tour Odoo 19 berubah |
| Komponen Owl/JavaScript custom | ☐ Tidak | Tidak ada file `.js` aplikatif (hanya test tour di atas) | E, F → N/A |
| Field JSON, relasi berantai (>2 level), atau dynamic model creation (`self.env[var]`) | ☐ Tidak | Tidak ditemukan di `models/product_template.py`/`models/stock_history_view.py` | B2 → N/A |
| View pakai `attrs=`/`states=`/`domain=`/`context=` dinamis | ☐ Tidak (domain statis) | `views/stock_history_view.xml` cuma `domain="[]"` + `context` group_by statis — bukan `attrs=`/`states=`, bukan domain computed. `views/views.xml` sudah pakai `<list>` (bukan `<tree>` lagi, sudah difix di migrasi 17→18) | C2 → N/A |

**Kesimpulan:** fase D1, D2, E, F, B2, C2 di Step 6 kemungkinan besar N/A lagi pada Applicability Check — modul ini murni backend (model Python + SQL view + security ACL + dua file view XML statis), satu-satunya elemen JS adalah test tour (bukan kode aplikatif yang butuh treatment migrasi frontend). Perlu dikonfirmasi ulang di Step 6 sendiri, bukan diasumsikan otomatis dari tabel ini.

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi — instalasi baru di versi target) — dikonfirmasi dev 2026-08-26
- [ ] Upgrade instance (ada data produksi — step 7 wajib jalan)

## 4. Baseline Spec / Characterization Test (gate)

- [x] Cek dulu: apakah modul punya `FUNCTIONAL_SPEC.md` lama di `source-codebase`? **Ya** — dua lapis: `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` (asli, 17.0) dan `doc-dev/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md` (hasil rekonsiliasi project 17→18, sudah didokumentasikan untuk versi 18.0 — ini yang jadi source of truth utama project INI, karena SOURCE_VERSION project ini adalah 18.0).
  - Proses: `01b_BASELINE_SPEC.md` (17→18) dibaca sebagai draft awal, cross-check langsung ke kode `product_history_report/models/*.py` di `target-codebase` saat ini (yang identik dengan `source-codebase`, sama-sama commit `978a384`). Semua klaim `BSL-001`..`BSL-011` dikonfirmasi masih cocok — tidak ada drift kode sejak dokumen itu ditulis (2026-08-24, dua hari sebelum sesi ini).
- [x] `01b_BASELINE_SPEC.md` sudah diisi — lihat file terpisah.

### 4a. Dokumen Pelengkap Lain

- [x] Tidak ditanyakan ulang secara eksplisit ke dev di sesi ini (implisit dari konteks: dev memberi instruksi bootstrap singkat, bukan sesi intake penuh) — dokumen pelengkap yang tersedia dan sudah dibaca: `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md`, `doc-dev/backfill/FINDINGS.md`, `doc-dev/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md`, `doc-dev/migration_17.0_18.0/doc/FINDINGS.md`, `doc-dev/migration_17.0_18.0/doc/CLAUDE.md` (status akhir project 17→18). **Open item:** perlu ditanyakan eksplisit ke dev apakah ada dokumen pelengkap LAIN (di luar repo) sebelum Step 2/3 mulai — belum dikonfirmasi.

**Tidak boleh lanjut ke step 2 sebelum `01b_BASELINE_SPEC.md` terisi** — sudah terpenuhi, lihat file terpisah.

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — source module dibekukan selama migrasi berjalan. Dikonfirmasi dev 2026-08-26.

## 5. Scope Boundary

- Yang harus tetap identik pasca migrasi: seluruh business rule `BSL-001`..`BSL-011` (`01b_BASELINE_SPEC.md`), termasuk 4 bug/quirk yang harus dipertahankan (`MF-01`..`MF-04` di `FINDINGS.md`) — race condition SQL view, double-count transfer internal, ACL longgar, ORM cache stale.
- Yang sengaja diubah/di-drop: tidak ada — port kode saja, tidak ada perubahan scope yang disepakati di intake ini.

## 6. Constraint

- Deadline: belum disebutkan dev — belum relevan/tidak urgent untuk tahap intake ini.
- Owner tiap step: belum disebutkan dev — akan ditanyakan kalau/ketika relevan (mis. sebelum Step 10 QA/Step 11 UAT butuh penunjukan QA/PM).
