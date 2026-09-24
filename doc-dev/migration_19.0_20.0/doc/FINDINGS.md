# Findings — product_history_report (migrasi 19.0 → 20.0)

**Modul:** product_history_report
**Migrasi:** 19.0 → 20.0
**Terakhir update:** 2026-09-24

---

## Ringkasan

| ID | Judul | Ditemukan di Step | Tag | Prioritas | Status |
|---|---|---|---|---|---|
| MF-01 | SQL view global `stock_history_view` di-drop+recreate per klik, race condition antar user | 1 | `[DIWARISI-SOURCE]` | Tinggi | 🔓 Terbuka — pertahankan identik |
| MF-02 | Transfer internal→internal dihitung ganda di income DAN outcome | 1 | `[DIWARISI-SOURCE]` | Sedang | 🔓 Terbuka — pertahankan identik |
| MF-03 | ACL `stock.history.view` tanpa grup — terbuka untuk semua user | 1 | `[DIWARISI-SOURCE]` + `[GAP-MIGRASI]` | Rendah | 🔓 Terbuka — pertahankan identik; bentuk ACL wajib dikonversi ke `ir.access` (DIFF-01) |
| MF-04 | ORM cache stale kalau `recreate_view()` dipanggil >1x dalam environment sama | 1 | `[DIWARISI-SOURCE]` | Rendah | 🔓 Terbuka — pertahankan identik |
| MF-05 | Ikon stat button `fa-signal` tidak dirender di 20.0 (Font Awesome → Material Symbols) | 1 | `[GAP-MIGRASI]` | Sedang | ✅ Diputuskan AI (low-risk, preseden native): `android_cell_5_bar` — lihat detail |
| MF-06 | Aset App Store branch rilis `19.0` tidak ada di `migration/19.0` | 1 | `[PERLU-KEPUTUSAN]` | Rendah | ✅ Diputuskan dev 2026-09-24: port ke 20.0 |
| MF-07 | Dependency Enterprise "kemungkinan" — tidak di manifest | 1 | `[PERLU-KEPUTUSAN]` | Sedang | ✅ Dijawab dev 2026-09-24 ("enterprise kemungkinan depend") — ditangani lewat analisis Step 2 + varian test Step 9 |
| MF-08 | Konten store `index.html` (port dari 19.0) masih menyebut "Odoo 19"; README/LISEZMOI ROOT repo masih "17.0" (README modul sudah diperbaiki A6) | 3 | `[PERLU-KEPUTUSAN]` | Rendah | ✅ Disesuaikan atas permintaan dev 2026-09-24 (index.html + README/LISEZMOI root → 20.0); sinkron `tools/variant.py` = DI LUAR SCOPE (task publish, keputusan dev) |
| MF-09 | `ERROR Model stock.history.view has no table.` di log install (model `_auto=False` tanpa `init()`) | 6 | `[DIWARISI-SOURCE]` | Rendah | 🔓 Terbuka — pertahankan identik; ✅ DIKONFIRMASI ada di 19.0 (baseline run Step 9) |
| MF-10 | **SQL injection via RPC**: `recreate_view()` publik + argumen di-f-string ke SQL — user login mana pun (termasuk portal) bisa eksekusi SQL arbitrer | 8 | `[DIWARISI-SOURCE]` + `[PERLU-KEPUTUSAN]` | **Kritis** | ✅ DIPERBAIKI di 20.0 (disetujui dev 2026-09-24) — 17.0/18.0/19.0 BELUM diperbaiki |
| MF-11 | Helper test `_make_move`: tanggal fixture tertimpa diam-diam di 20.0 (write ORM tertunda setelah `button_validate()`) → AC-02-01/03-01 sempat hijau tanpa menguji tanggal lama | 10 | `[GAP-MIGRASI]` (test-harness) | Sedang | ✅ Diperbaiki di test (flush + assert tanggal), re-run PASS |
| MF-12 | `RecursionError` native (mail_bot OdooBot → `discuss.channel._compute_member_indices`) saat bootstrap web client pertama admin di 20.0 Enterprise | 10 | `[GAP-MIGRASI]` (native, bukan modul) | Rendah | 🔓 Info — sekali terjadi, reload normal; tidak menyentuh modul |

MF-01..MF-04 carry-over persis dari `doc-dev/migration_18.0_19.0/doc/FINDINGS.md` (aslinya `F-01`/`F-02`/`F-04`/`F-09` di `doc-dev/backfill/FINDINGS.md`, 2026-08-07). ID dipertahankan sama lintas project.

> Catatan konsistensi: `CLAUDE.md` project ini menyebut "MF-01 (SQL f-string warisan, sengaja tidak diubah by design)". MF-01 di dokumen 18→19 sebenarnya berjudul race condition SQL view global — f-string SQL adalah bagian dari mekanisme yang sama (`recreate_view()` menyusun SQL lewat f-string), jadi keduanya merujuk hal yang sama. Tidak ada MF terpisah untuk f-string.

---

## Detail

### MF-01 — SQL view global di-drop+recreate per klik, race condition antar user
**Ditemukan di:** Step 1 (2026-09-24), diwarisi dari MF-01 18→19 / 17→18, aslinya `F-01` backfill
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-002`
**Lokasi:** `product_history_report/models/stock_history_view.py:24-110` (`recreate_view`), dipanggil dari `models/product_template.py:19`
**Deskripsi:** DROP+CREATE VIEW global `stock_history_view` tanpa locking, di-scope ke satu produk+company lewat f-string SQL. Di alur tombol, nilai yang disisipkan (`self.id`, `env.companies.ids`) berupa integer. **KOREKSI Step 8:** klaim awal "bukan input user bebas" SALAH — `recreate_view()` adalah method publik yang bisa dipanggil langsung lewat RPC dengan argumen string sembarang → lihat MF-10 (SQL injection).
**Dampak di 20.0:** identik dengan 19.0 — dipertahankan.
**Rekomendasi:** tidak ada tindakan saat migrasi.
**Keputusan pemilik modul:** *(kosong — belum pernah diputuskan sejak F-01 2026-08-07)*

---

### MF-02 — Transfer internal→internal dihitung ganda di income DAN outcome
**Ditemukan di:** Step 1 (2026-09-24), diwarisi (`F-02` backfill)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-004`
**Lokasi:** `product_history_report/models/stock_history_view.py:32-33`
**Deskripsi:** income/outcome dievaluasi independen per move; internal→internal masuk keduanya.
**Dampak di 20.0:** identik — dipertahankan.
**Keputusan pemilik modul:** *(kosong)*

---

### MF-03 — ACL `stock.history.view` tanpa grup, terbuka untuk semua user
**Ditemukan di:** Step 1 (2026-09-24), diwarisi (`F-04` backfill)
**Tag:** `[DIWARISI-SOURCE]` + `[GAP-MIGRASI]` (bentuk teknisnya wajib berubah di 20.0)
**Ref:** `BSL-007`, `DIFF-01` (`02_DIFF_ANALYSIS.md`)
**Lokasi:** `product_history_report/security/ir.model.access.csv:2`
**Deskripsi:** `access_stock_history_view` 1,1,1,1 tanpa `group_id` — di 19.0 berlaku semua user.
**Dampak di 20.0:** model `ir.model.access` DIHAPUS di 20.0 (diganti `ir.access`). Di `ir.access`, baris TANPA grup adalah *restriction* (di-AND, tidak memberi akses apapun) — port mentah akan membuat model ini tidak bisa diakses siapapun kecuali superuser (regresi total). Padanan behavior-preserving: baris `ir.access` dengan grup `base.group_everyone` (grup "Role / Everyone", di-imply oleh `base.group_user`, `base.group_portal`, `base.group_public`) dan `operation=crud`. Ini persis konversi resmi Odoo (`odoo20/odoo/upgrade_code/19.4-00-ir-access.py` baris 517-519: "ir.model.access without group, base.group_everyone instead").
**Rekomendasi:** konversi ke `security/ir.access.csv` dengan `base.group_everyone` — mempertahankan keterbukaan akses identik 19.0 (bukan diperketat).
**Keputusan pemilik modul:** *(kosong — soal apakah akses perlu dibatasi ke grup Inventory tetap keputusan terpisah dari migrasi)*

---

### MF-04 — ORM cache stale kalau `recreate_view()` dipanggil >1x dalam environment sama
**Ditemukan di:** Step 1 (2026-09-24), diwarisi (`F-09` backfill)
**Tag:** `[DIWARISI-SOURCE]`
**Ref:** `BSL-009`
**Lokasi:** `product_history_report/models/stock_history_view.py:24-110`
**Dampak di 20.0:** identik — dipertahankan.
**Keputusan pemilik modul:** *(kosong)*

---

### MF-05 — Ikon stat button `fa-signal` tidak dirender di 20.0
**Ditemukan di:** Step 1 (2026-09-24, analisis awal `native-target`)
**Tag:** `[GAP-MIGRASI]`
**Ref:** `BSL-013`, `DIFF-02`
**Lokasi:** `product_history_report/views/views.xml` (atribut `icon="fa-signal"`)
**Deskripsi:** Di 20.0 `ViewButton` (`addons/web/static/src/views/view_button/view_button.js` `iconFromString`) merender atribut `icon` sebagai `<i class="o_button_icon oi" data-icon="...">` yang digambar lewat ligature font Material Symbols (`addons/web/static/src/webclient/icons.scss`, `content: attr(data-icon)`). String `fa-signal` bukan nama ikon Material → tombol tampil tanpa ikon yang benar. Semua stat button native di view yang sama sudah dikonversi (`fa-exchange`→`sync_alt`, `fa-refresh`→`cached`, dst). Font yang dimuat adalah SUBSET (`addons/web/tooling/icons/icons_wishlist.txt`, 479 nama) — pengganti wajib ada di subset.
**Keputusan (AI, prinsip "jalan terus" USAGE_GUIDE — satu opsi jelas paling aman):** `android_cell_5_bar`. Alasan: Odoo sendiri memetakan `fa-signal` → `android_cell_5_bar` untuk stat button produk di modul `sale` (commit native `5d739f24054` "[IMP] mrp,*: icon update"), dan nama itu ada di subset font. Ini mempertahankan UX (ikon bar sinyal) — bukan redesign.
**Keputusan pemilik modul:** *(opsional — dev boleh koreksi nama ikon kalau mau yang lain)*

---

### MF-06 — Aset App Store branch rilis `19.0` tidak ada di `migration/19.0`
**Ditemukan di:** Conditioning (2026-09-24), diputuskan Step 1
**Tag:** `[PERLU-KEPUTUSAN]`
**Ref:** `01a_MIGRATION_INTAKE.md` §5, `BSL-015`
**Deskripsi:** branch `19.0`/`staging/19.0` punya 5 commit pasca-migrasi (banner.gif, icon.png, `assets/`, `index.html`, key `images`).
**Keputusan pemilik modul:** ✅ Dev 2026-09-24 (AskUserQuestion): **port aset store ke 20.0**. Hanya `static/description/**` + key `images` yang dibawa; hasil `cleaning` lain (hapus tests/doc-dev) tidak dibawa.

---

### MF-07 — Dependency Enterprise "kemungkinan"
**Ditemukan di:** Step 1 (2026-09-24)
**Tag:** `[PERLU-KEPUTUSAN]`
**Ref:** `01a_MIGRATION_INTAKE.md` §0
**Deskripsi:** manifest hanya `base`, `stock`; dev menjawab "enterprise kemungkinan depend".
**Tindakan:** Step 2 analisis `enterprise20` untuk modul yang menyentuh form `product.template`/tabel stock (kandidat awal `quality_control`); Step 9 run tambahan dengan addons Enterprise terpasang.
**Keputusan pemilik modul:** ✅ jawaban dev di atas (2026-09-24). Kalau ternyata ada modul Enterprise spesifik yang dimaksud, dev bisa menyebutkannya kapan saja.

---

### MF-10 — SQL injection via RPC pada `stock.history.view.recreate_view()`
**Ditemukan di:** Step 8 (2026-09-24), sweep skill `odoo-security`
**Tag:** `[DIWARISI-SOURCE]` + `[PERLU-KEPUTUSAN]`
**Ref:** `BSL-002`, `08_CODE_REVIEW.md` CR-01, MF-01
**Lokasi:** `product_history_report/models/stock_history_view.py:24-110`
**Deskripsi:** method publik (tanpa `_`/`@api.private`) → dapat dipanggil via `/web/dataset/call_kw` (`auth="user"`). Argumen `product_template_id` dan `companies` diinterpolasi f-string ke SQL `CREATE VIEW` lalu `self._cr.execute(query)` tanpa parameter. User login mana pun (internal maupun portal — model ini bahkan tidak butuh ACL untuk pemanggilan method) bisa mengirim string berisi SQL tambahan → dieksekusi dengan hak DB owner Odoo (baca/ubah/hapus data apapun). Kode byte-identik sejak 17.0 → bukan regresi migrasi.
**Dampak di 20.0:** identik dengan 19.0 (masih rentan). Berbasis analisis kode statis (CR-01); probe eksploitasi sengaja tidak dijalankan.
**Rekomendasi (menunggu keputusan dev — tidak dikerjakan AI tanpa persetujuan):** fix minimal tanpa mengubah hasil laporan: (1) tandai `@api.private` (atau rename `_recreate_view` + update pemanggil di `product_template.py`), DAN (2) paksa integer sebelum interpolasi (`int(product_template_id)`, `','.join(str(int(c)) for c in ...)`) atau pakai `odoo.tools.SQL` berparameter. Tambah test regresi RPC.
**Keputusan pemilik modul:** ✅ Dev 2026-09-24 via chat: "ok kerjakan dan nanti catat baru di fixing di 20, versi sebelumnya belum". **Dikerjakan di 20.0 (perubahan disengaja SCOPE-02):** `recreate_view()` diberi `@api.private` (tidak bisa dipanggil lewat RPC; pemanggilan server-side dari tombol tetap jalan) + kedua argumen dipaksa integer sebelum masuk teks SQL. Hasil laporan untuk input sah identik. Test regresi `test_ac_07_01`/`test_ac_07_02`. Run C 15/15, Run E 14+1 skip (`09_DEV_TESTING.md` §Re-run). **Branch `migration/19.0`, `19.0`, `18.0`, `17.0` TETAP rentan** — fix hanya di 20.0 sesuai keputusan dev.

---

### MF-09 — `ERROR Model stock.history.view has no table.` di log install/registry load
**Ditemukan di:** Step 6 G1 #2 (2026-09-24)
**Tag:** `[DIWARISI-SOURCE]` — ✅ DIKONFIRMASI 2026-09-24: baseline run kode `migration/19.0` di Odoo 19.0 juga mencatat ERROR ini ×2 (`09_DEV_TESTING.md` §Baseline)
**Ref:** `BSL-002`, `BSL-014`, `06c_IMPLEMENTATION_LOG.md` G1 #2
**Lokasi:** `product_history_report/models/stock_history_view.py` (`_auto = False`, tidak ada `init()`); pesan dari `odoo20/odoo/orm/registry.py:1059` (logika identik `odoo19/odoo/orm/registry.py:996`)
**Deskripsi:** model `_auto=False` tanpa `init()` → registry tidak menemukan tabel/view `stock_history_view` sampai tombol "Stock History" pertama kali diklik (`recreate_view()`), lalu mencatat ERROR tiap registry load. Tidak memblokir install/test (G1/G2 exit 0).
**Dampak di 20.0:** identik — log noise, bukan kegagalan. Dipertahankan (menambah `init()` = perubahan behavior/refactor di luar scope).
**Keputusan pemilik modul:** *(kosong)*

---

### MF-08 — Konten store & README masih menyebut versi lama
**Ditemukan di:** Step 3 (2026-09-24)
**Tag:** `[PERLU-KEPUTUSAN]`
**Ref:** `SCOPE-01`, `03_MIGRATION_SPEC.md` §4
**Lokasi:** `product_history_report/static/description/index.html` (port dari branch `19.0`, baris 7, 10, 15, 429, 441, 1027: "Odoo 19"/"Odoo 19.0"/"module version 19.0.1.0.0"); `README.md:71`, `LISEZMOI.md:69` di ROOT repo ("17.0"). *(Update Step 6: `product_history_report/README.md`/`LISEZMOI.md` level modul sudah diperbaiki ke "20.0" di Fase A6 sesuai `06a` — hanya salinan root yang tersisa.)*
**Deskripsi:** header komentar `index.html` sendiri menyatakan file itu "DERIVED, NOT HAND-WRITTEN — Generated from the 17.0 source with tools/variant.py. Edit the 17.0 source and re-derive; do not patch this file by hand". Karena itu AI port apa adanya (sesuai persetujuan dev "port aset store") dan TIDAK mengedit manual. README/LISEZMOI di luar scope yang disetujui.
**Dampak:** non-fungsional — listing App Store 20.0 akan menampilkan "Odoo 19" sampai varian 20.0 di-derive.
**Rekomendasi:** dev menjalankan `tools/variant.py` (di luar repo ini) untuk varian 20.0 dan mengganti `index.html`; sekaligus perbarui baris "Odoo version" di README/LISEZMOI kalau diinginkan.
**Keputusan pemilik modul:** ✅ Dev 2026-09-24 via chat: "sesuaikan". **Dikerjakan (SCOPE-03):** `index.html` — hanya penanda versi modul ini (judul, meta description, header komentar, chip "Odoo 20.0", tagline, "20.0 build", Requirements, entri Releases `20.0.1.0.0`) + kalimat jumlah test disesuaikan ("thirteen automated integration tests and two browser tour tests"). Link cross-sell ke modul lain (`/apps/modules/19.0/...`) dan teks "Flow Survey Reader 19.0" TIDAK diubah (merujuk versi modul lain yang memang ada di store). Header komentar diberi catatan "ADJUSTED BY HAND FROM THE 19.0 VARIANT … Port the same edits into the 17.0 source / tools/variant.py before the next re-derive" — **dev perlu menyinkronkan `tools/variant.py` supaya perubahan ini tidak hilang saat re-derive**. `README.md`/`LISEZMOI.md` root → "20.0" (sekarang identik dengan salinan di modul).

---

## Cara Pakai

Lihat `migration-tool/templates/FINDINGS.md` §Cara Pakai.

---

### MF-11 — Tanggal fixture test tertimpa diam-diam di 20.0
**Ditemukan di:** Step 10 (2026-09-24), saat Cross-Version Compare (seed pertama menunjukkan semua move menumpuk di bulan berjalan di 20.0)
**Tag:** `[GAP-MIGRASI]` — perilaku ORM 20.0, dampak hanya ke test-harness (kode modul benar)
**Ref:** AC-02-01, AC-03-01, AC-04-01, `10_BUSINESS_FLOW_MIGRATION.md` §Loop-back
**Lokasi:** `product_history_report/tests/test_product_history_report.py` `_make_move()`
**Deskripsi:** helper memundurkan tanggal lewat `UPDATE stock_move_line SET date` lalu `invalidate_recordset(['date'])`. Di 20.0, setelah `button_validate()` masih ada write ORM tertunda ke `stock_move_line`; write itu ter-flush SETELAH UPDATE dan menimpa tanggal jadi "sekarang". Bukti probe (`odoo-bin shell`, pola persis helper): 19.0 → tanggal tersimpan `2025-07-01`; 20.0 → `2026-09-24`. Test tetap hijau karena AC-02-01 hanya cek qty kumulatif akhir dan AC-03-01 punya fallback "baris terakhir" — jadi saldo pembuka >13 bulan TIDAK benar-benar teruji di 20.0 sebelum fix.
**Tindakan:** `env.flush_all()` sebelum UPDATE + assert tanggal di DB = `move_date`. Re-run Run C & Run E `0 failed of 17` — test kini menguji tanggal sesungguhnya. Kode modul benar: Cross-Version Compare dengan seed yang di-flush menghasilkan 15/15 baris identik 19.0↔20.0.
**Keputusan pemilik modul:** tidak perlu (perbaikan test).

---

### MF-12 — `RecursionError` native OdooBot di bootstrap web client pertama (20.0 Enterprise)
**Ditemukan di:** Step 10 (2026-09-24), login pertama admin di server QA 20.0 (`odoo20` `b0329e93ae8` + `enterprise20` `bbccc6bce1`)
**Tag:** `[GAP-MIGRASI]` — bug native Odoo 20.0, BUKAN modul ini
**Lokasi:** `odoo20/addons/mail_bot/models/res_users.py:27-32` `_init_odoobot` → `mail/models/discuss/discuss_channel.py:1809` `_get_or_create_chat` → `_compute_member_indices` (:409) → rekursi; tidak ada frame `product_history_report`.
**Deskripsi:** request `/odoo/action-…` pertama setelah login → HTTP 500. Reload berikutnya normal (chat OdooBot sudah terinisialisasi). Tour test tidak terkena.
**Dampak:** tidak ada ke modul; catatan untuk instalasi 20.0 baru (build pre-release).
**Keputusan pemilik modul:** tidak perlu (native).

---

### Update MF-08 (2026-09-24, pasca penutupan)
**Keputusan pemilik modul:** ✅ Dev: "abaikan saja, itu di luar scope, itu scope task publish". Sinkronisasi perubahan `index.html` ke `tools/variant.py` (sumber generator halaman store, tidak ada di repo ini) **bukan bagian migrasi** — ditangani di task publish App Store. MF-08 ditutup untuk migrasi ini.
