# Migration Intake — product_history_report

**Step:** 1 — Intake & Scope
**Versi:** 19.0 → 20.0
**Tanggal:** 2026-09-24
**Status:** ✔️ Disetujui — jawaban intake dev via chat 2026-09-24 (AskUserQuestion, 4 pertanyaan), gate ditutup

---

## 0. Folder Referensi

Semua path sudah diketahui sejak conditioning (dicatat di `CLAUDE.md` §Folder) dan dicek ulang di sesi ini lewat `ls`/`git log -1` (read-only — git di repo native hanya dipakai untuk `log`, tidak ada operasi tulis):

- [x] `native-target` (Community 20.0) — `D:\Kuncoro\doodex\repo\odoo20`, branch `20.0`, HEAD `b0329e93ae8` (2026-09-20), `odoo/release.py` `version_info = (20, 0, 0, FINAL, 0, '')`. Repo Community penuh.
- [x] `native-source` (Community 19.0) — `D:\Kuncoro\doodex\repo\odoo19`, branch `19.0`.
- [x] **`native-target-enterprise`** — `D:\Kuncoro\doodex\repo\enterprise20`, branch `20.0`, HEAD `bbccc6bce1` (2026-09-20, sinkron dengan `odoo20`), addons-only (868 entri). **Dev menjawab (2026-09-24): "enterprise kemungkinan depend"** — manifest TIDAK mendeklarasikan modul Enterprise apapun (`depends: ['base', 'stock']`), tapi modul kemungkinan di-deploy di instance Enterprise. Konsekuensi yang AI ambil (asumsi terdokumentasi, bukan keputusan scope baru): (a) Step 2 WAJIB menganalisis modul Enterprise 20.0 yang menyentuh area yang sama (form `product.template` / view `stock.product_template_form_view_procurement_button`, tabel `stock_move`/`stock_move_line`) — kandidat awal dari scan: `quality_control` (meng-inherit view yang sama); (b) Step 9 menjalankan varian test tambahan dengan `enterprise20` di addons-path + modul Enterprise stock terkait terpasang, selain run Community murni.
- [x] `native-source-enterprise` — `D:\Kuncoro\doodex\repo\enterprise19`, branch `19.0`, addons-only. Dipakai untuk cross-check behavior 19.0 di instance Enterprise.
- [x] **`third-party-source`/`third-party-target`** — dev tidak menyebut dependency OCA/vendor apapun (jawaban dependency hanya menyebut Enterprise). Auto-scan juga tidak menemukan. **Dicatat: tidak ada.**

### 0a. Konfirmasi Branch/Versi

- [x] Source: branch `migration/19.0` (repo ini, hasil akhir migrasi 18→19 yang SELESAI, HEAD `f57dee4`). Dikonfirmasi dev di prompt kickoff ("Source branch: migration/19.0"). Tidak ada `source-codebase` folder terpisah — kode 19.0 dibaca via `git show migration/19.0:<path>`.
- [x] Target: branch `migration/20.0` (repo ini, dibuat saat conditioning dari `migration/19.0`). Dikonfirmasi dev di prompt kickoff ("target branch: migration/20.0 (sudah dibuat saat conditioning)").
- [x] Dua clone fisik terpisah: N/A — model single-repo dual-branch (sama seperti project `optional_field_save` 19→20), keputusan conditioning.
- [x] Versi Odoo semantik: **19.0 → 20.0**, eksplisit di prompt kickoff dev ("Lakukan migrasi 19→20").
- [x] Koreksi nama branch dari open item conditioning: dokumen lama menyebut `migration/19.0_target`, nama aktual `migration/19.0` (lokal = `origin/migration/19.0`). Semua dokumen 19→20 pakai nama aktual.

### 0b. Gate: Path Absolut di `.claude/settings.json`

- [x] `settings.json` varian Mode Git sudah memakai path absolut nyata (bukan placeholder `{{ABS_PATH_...}}`): deny `Edit` untuk `odoo19`, `enterprise19`, `odoo20`, `enterprise20`, `migration-tool/knowledge/**`, `migration-tool/templates/**`. Tidak ada placeholder literal tersisa.
- [x] `ABS_PATH_SOURCE_CODEBASE` — N/A (tidak ada folder source terpisah, source = branch `migration/19.0` di repo ini).
- [x] `ABS_PATH_THIRD_PARTY_*` — tidak dipakai, tidak ada baris deny (tidak ada dependency OCA).

---

## Ringkasan untuk Review — Perlu Konfirmasi User

1. **Sifat migrasi = port kode saja, source beku** — dikonfirmasi dev 2026-09-24. Step 7 N/A, `SYNC_POLICY.md` tidak dibuat.
2. **Aset App Store dari branch rilis `19.0` DI-PORT ke 20.0** — dikonfirmasi dev 2026-09-24. Lima commit pasca-migrasi di branch `19.0` (`0dd37fc` "cleaning", `c310886` banner.png→banner.gif, `a08a237` folder `assets` + `icon.png`, `7bd2a5b` update `index.html`, `9b88ff8` fix key `images` manifest) — hanya `product_history_report/static/description/**` + key `images` di `__manifest__.py` yang dibawa. File lain dari commit `cleaning` (penghapusan `doc-dev/`, `tests/`, `LICENSE`, `LISEZMOI.md`, dst di branch rilis) TIDAK dibawa — itu pembersihan paket rilis, bukan perubahan modul; `tests/` dan `doc-dev/` wajib tetap ada di branch migrasi. Ini **perubahan disengaja non-fungsional** (§5).
3. **Dependency Enterprise "kemungkinan"** — lihat §0: tidak ada di manifest, tapi Step 2 & Step 9 menambahkan cakupan Enterprise 20.0 sebagai jaring pengaman.
4. **Tiga breaking change 20.0 sudah terdeteksi saat intake (detail di Step 2):** (a) model `ir.model.access` DIHAPUS di 20.0, diganti `ir.access` (file `ir.access.csv`) — `security/ir.model.access.csv` modul ini akan gagal di-load; baris ACL tanpa grup wajib jadi `base.group_everyone` (konversi resmi Odoo, `odoo/upgrade_code/19.4-00-ir-access.py`); (b) ikon stat button pindah dari Font Awesome ke Material Symbols (`icon="fa-signal"` → Odoo sendiri memetakan ke `android_cell_5_bar` di modul `sale`); (c) `stock.move.product_uom` di-rename jadi `uom_id` (hanya dipakai test helper).
5. **4 bug/quirk warisan tetap dipertahankan identik** (`MF-01`..`MF-04`, `FINDINGS.md`) — race condition SQL view global, double-count transfer internal, ACL longgar, ORM cache stale. Tetap belum ada keputusan pemilik modul.
6. Mode eksekusi: **Mode C** (AI jalankan Docker, build Odoo 20 dari source `odoo20` karena belum ada image resmi `odoo:20.0`), GUI git client dikonfirmasi tertutup, auto-commit per step tanpa push. **Step 10 TIDAK dijalankan otomatis** — instruksi eksplisit dev: berhenti setelah Step 9 lulus gate dan lapor "siap Step 10, menunggu slot" (pembatasan kontensi browser/Docker lintas repo, MF-46 project lain).

---

## 1. Modul & Scope

- Modul yang dimigrasi: **product_history_report** (satu modul). Nama repo GitHub `inventory_movement_report`.
- Deskripsi singkat: laporan riwayat pergerakan stok bulanan (~13 bulan) per produk, dibuka lewat tombol statistik "Stock History" di form `product.template`. Backend murni: satu SQL view (`stock.history.view`, `_auto=False`) yang di-drop+recreate per klik lewat satu method Python.
- Modul-modul saling depend: N/A.

## 2. Dependency Map (auto-scan)

| Dependency | Tipe | Versi tersedia di target? | Catatan |
|---|---|---|---|
| `base` | Native Community | Ya | 20.0: unifikasi ACL `ir.model.access`+`ir.rule` → `ir.access` (breaking, lihat Ringkasan #4a) |
| `stock` | Native Community | Ya | 20.0: rename field uom logistik (`stock.move.product_uom`→`uom_id`, `stock.move.line.product_uom_id`→`uom_id`); ikon stat button form produk pindah ke Material Symbols |
| *(tidak dideklarasikan)* Modul Enterprise stock/quality | Native Enterprise | Ya (`enterprise20`) | Dev: "kemungkinan depend" — bukan dependency manifest, tapi lingkungan deploy. Dianalisis di Step 2 (`quality_control` meng-inherit view yang sama) |

Dependency opsional yang dicek runtime (`'x' in self.env`): tidak ada — dikonfirmasi ulang dari kode `migration/19.0`.

## 2b. Struktur & Fitur Modul (auto-scan)

| Fitur | Ada di modul? | Lokasi/bukti | Fase step 6 relevan |
|---|---|---|---|
| Controllers (route custom) | ☐ Tidak | `controllers/controllers.py` boilerplate scaffold, semua di-comment | D1 → N/A |
| Assets/CSS/JS custom | ☐ Tidak (aplikatif) — ADA 1 file JS test | `static/tests/tours/stock_history_tour.js` di `web.assets_tests` (tour test), bukan frontend aplikatif. Tidak ada `static/src/` | D2, E, F → N/A untuk kode aplikatif; tour dicek di Step 9 |
| Komponen Owl/JavaScript custom | ☐ Tidak | hanya tour test | E, F → N/A |
| Field JSON / relasi berantai / dynamic model | ☐ Tidak | — | B2 → N/A |
| View pakai `attrs=`/`states=`/domain dinamis | ☐ Tidak | domain statis `[]` + context group_by statis | C2 → N/A |

**Catatan tambahan 20.0 (tidak ada kolomnya di tabel template):** view XML memakai atribut `icon="fa-*"` pada `<button>` — di 20.0 ini masuk kategori perubahan view (Fase C1), bukan asset.

## 3. Sifat Migrasi

- [x] Port kode saja (belum ada data produksi) — dikonfirmasi dev 2026-09-24
- [ ] Upgrade instance

## 4. Baseline Spec / Characterization Test (gate)

- [x] Spec lama ada, tiga lapis di repo ini: `doc-dev/backfill/spec/01A_FUNCTIONAL_SPEC.md` (BR-01..06, 17.0), `doc-dev/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md`, `doc-dev/migration_18.0_19.0/doc/01_intake/01b_BASELINE_SPEC.md` (BSL-001..011, dokumentasi behavior 19.0 — basis utama project ini). Diperiksa ulang: semua BR-01..06 + AC-01-01..AC-05-02 backfill tercakup di BSL-001..011.
- [x] Test/characterization test lama: ada, lokasinya SAMA dengan source — `product_history_report/tests/test_product_history_report.py` (8 test Integration, asal backfill 17.0) + `tests/test_stock_history_tour.py` (1 Tour test, Step 9 project 17→18, diupdate 18→19). 9/9 PASS di 19.0 (`doc-dev/migration_18.0_19.0/doc/09_devtest/09_DEV_TESTING.md`). Dev tidak menyebut test lain di luar repo.
- [x] `01b_BASELINE_SPEC.md` sudah diisi — file terpisah. Cross-check ke kode `migration/19.0`: tidak ada drift sejak dokumen 18→19 (diff `migration/19.0` vs `migration/20.0` untuk `product_history_report/` kosong saat intake).

### 4a. Dokumen Pelengkap Lain

- [x] Ditanyakan eksplisit ke dev 2026-09-24 (pertanyaan "dependency Enterprise/OCA tersembunyi, atau dokumen/test pelengkap lain di luar repo"). Jawaban dev hanya menyebut kemungkinan Enterprise, tidak menyebut dokumen lain. **Dicatat: tidak ada dokumen pelengkap di luar repo.** Dokumen yang dibaca: seluruh `doc-dev/` di repo + `migration-tool/migration-records/product_history_report_18.0_19.0/SUMMARY.md` + record 19→20 project lain (`optional_field_save`, `pos-margin-sale`).

## 4b. Source Masih Aktif Dikembangkan?

- [x] Tidak — dikonfirmasi dev 2026-09-24.

## 5. Scope Boundary

- Yang harus tetap identik pasca migrasi: seluruh `BSL-001`..`BSL-015` (`01b_BASELINE_SPEC.md`), termasuk 4 bug/quirk warisan `MF-01`..`MF-04`.
- **Yang sengaja diubah (disetujui dev 2026-09-24):** port aset App Store dari branch rilis `19.0` — `static/description/**` (banner.gif, icon.png, `assets/{gifs,icons,screens}`, `index.html`) + key `images` manifest → `['static/description/banner.gif', 'static/description/icon.png']`. Non-fungsional, tidak menyentuh business logic.
- Perubahan wajib kompatibilitas (bukan perubahan scope): ACL → `ir.access.csv`, ikon Material Symbols, rename field test — detail Step 2/3.

## 6. Constraint

- Deadline: tidak disebutkan.
- Eksekusi: jalan otomatis Step 1→9; **STOP WAJIB sebelum Step 10** sampai dev memberi slot (maks 2 repo kecil bersamaan di Step 10, atau 1 repo besar sendirian).
- Docker: dua container project lain sedang jalan di host (`pos_margin_sale_migration_20` di 8078/8182) — project ini pakai compose name `product_history_report_migration_20` dan port host 8093 supaya tidak bentrok.
