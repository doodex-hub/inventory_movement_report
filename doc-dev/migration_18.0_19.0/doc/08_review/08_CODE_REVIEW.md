# Code Review — product_history_report

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/06c_IMPLEMENTATION_LOG.md`, `01_intake/01b_BASELINE_SPEC.md`
**Odoo Version:** 19.0
**Files reviewed:** `__manifest__.py`, `models/product_template.py`, `models/stock_history_view.py`, `views/stock_history_view.xml`, `views/views.xml`, `security/ir.model.access.csv`, `tests/test_product_history_report.py`, `tests/test_stock_history_tour.py`, `static/tests/tours/stock_history_tour.js`, `controllers/controllers.py` (diff terhadap `source-codebase` branch `migration/18.0`)
**Tanggal:** 2026-08-26

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| REV-01 | 🔵 Info | Code Quality | `models/product_template.py`, `models/stock_history_view.py` | 3 | Import `from odoo.http import request` tidak dipakai (dead import, sudah ada sejak 17.0, bukan hasil migrasi) | Opsional dibersihkan — TIDAK wajib, di luar scope migrasi (`03_MIGRATION_SPEC.md` §4) |
| REV-02 | 🔵 Info | Code Quality | `views/stock_history_view.xml` | 63-74 | `action_stock_history_graph2`/`action_stock_history_tree2` tetap dead code (tidak terhubung `<menuitem>`) — sudah ada sejak 17.0, bukan hasil migrasi | Opsional dibersihkan — TIDAK wajib |
| REV-03 | 🟡 Warning | Konvensi Odoo | `models/stock_history_view.py` | 26-109 | SQL mentah via f-string ke `product_template_id`/`companies` — sudah ada sejak 17.0 (BR-02, `FINDINGS.md` MF-01), risiko SQL injection klasik RENDAH karena kedua nilai berasal dari `self.id`/`self.env.companies.ids` (integer ORM, bukan input user bebas), tapi pola f-string-ke-SQL tetap rapuh secara konvensi | Tidak diubah saat migrasi (bug/pola source dipertahankan, `03_MIGRATION_SPEC.md` §4) — dicatat ulang di sini murni untuk visibility reviewer, bukan actionable item migrasi |
| REV-04 | 🔵 Info | Code Quality | `models/stock_history_view.py` | 24, 26 | `self._cr` dipakai (2 titik) — deprecated sejak 19.0 (`@api.deprecated`, DIFF-03), masih berfungsi sebagai alias `self.env.cr` | Opsional diganti `self.env.cr` — TIDAK wajib, tidak install/runtime-blocking |

**Tidak ada issue 🔴 Critical.** REV-01/REV-02 warisan langsung dari 17.0 (sudah tercatat `01b_BASELINE_SPEC.md` BSL-010/BSL-011), REV-03 warisan `FINDINGS.md` MF-01 — bukan regresi baru dari migrasi. REV-04 murni baru muncul di 19.0 (deprecation warning), tapi tidak actionable-wajib.

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| DIFF-01 (`<group expand=/string=>` dihapus) | `views/stock_history_view.xml` baris 10 | ✅ Match | Dikonfirmasi G1: install bersih, tidak ada `ValidationError` |
| DIFF-02 (`res.users.groups_id`→`group_ids`) | `tests/test_product_history_report.py` baris 189 | ✅ Match | Dikonfirmasi G1: `test_ac_05_01_...` PASS |
| DIFF-03 (`self._cr` deprecated, opsional) | Tidak diubah (opsional, sesuai spec) | ✅ Match — sesuai spec (tidak wajib) | Lihat REV-04 |
| DIFF-04 s/d DIFF-09, DIFF-11, DIFF-12, DIFF-13 | Tidak ada perubahan kode | ✅ Match | Sesuai spec (dikonfirmasi stabil, tidak perlu perubahan) |
| DIFF-10 (xmlid picking type/location) | Tidak diubah | ✅ Match — dikonfirmasi aman via G1, sesuai keputusan spec (jangan fix preventif tanpa bukti gagal) | — |
| DIFF-14 (manifest version) | `__manifest__.py` `'19.0.1.0.0'` | ✅ Match | — |
| DIFF-15 (`stock.move.name` dihapus, BARU ditemukan G1) | `tests/test_product_history_report.py` baris 64-65 (key `name` dihapus) | ✅ Match | Ditemukan & difix di G1 run #1→#2 (lihat `06c_IMPLEMENTATION_LOG.md`), didokumentasikan ke `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md` SEBELUM fix diterapkan |
| DIFF-16 (tour `.o_button_more` tidak render, BARU ditemukan G1) | `static/tests/tours/stock_history_tour.js` (step diubah) | ✅ Match | Ditemukan & difix di G1 run #1→#2, didokumentasikan dulu sebelum fix |

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC ID | Behavior | Status | Catatan |
|---|---|---|---|
| AC-01-01 | Tombol Stock History muncul di form | ✅ Match | Dikonfirmasi test `test_ac_01_01_button_present_in_form_arch` PASS |
| AC-01-02 | Window action `graph,pivot,list` terbuka | ✅ Match | Dikonfirmasi test `test_ac_01_02_...` PASS (tidak butuh update, token sudah final sejak 18.0) |
| AC-01-03 | Search panel groupby tetap berfungsi pasca hapus atribut `<group>` | ⏳ Belum diverifikasi | Tidak ada test otomatis (by design) — didorong ke Step 10 QA (Manual), sesuai `05b_TEST_PLAN_MIGRATION.md` |
| AC-02-01 | qty running-sum mencakup saldo >13 bulan | ✅ Match | Dikonfirmasi test `test_ac_02_01_...` PASS (setelah fix DIFF-15) |
| AC-02-02 | Race condition SQL view (dipertahankan, bukan ditest otomatis) | ✅ Match (by design, tidak ada test) | Konsisten `05b_TEST_PLAN_MIGRATION.md` — tidak ada regresi kode yang mengubah mekanisme ini |
| AC-03-01 | Move customer→internal = income saja | ✅ Match | Dikonfirmasi test PASS (setelah fix DIFF-15) |
| AC-03-02 | Double-count internal→internal DIPERTAHANKAN | ✅ Match | Dikonfirmasi test PASS — bug MF-02 terbukti masih terjadi identik di 19.0 |
| AC-04-01 | Filter multi-company | ✅ Match | Dikonfirmasi test PASS (setelah fix DIFF-15) |
| AC-05-01 | ACL terbuka tanpa grup (dipertahankan) | ✅ Match | Dikonfirmasi test PASS (setelah fix DIFF-02) |
| AC-05-02 | create/write/unlink gagal di DB | ✅ Match | Dikonfirmasi test PASS |

**Catatan AC-01-03:** satu-satunya AC yang belum diverifikasi eksekusi (butuh klik manual, bukan gap implementasi) — ditandai eksplisit di sini supaya tidak lupa sebelum Step 10 ditutup.

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — semua deviasi dari source (`source-codebase`) sudah eksplisit tercatat & disetujui (2 titik view/test mekanis DIFF-01/02, 2 titik test-only ditemukan G1 DIFF-15/16, 1 bump version — semua mekanis/test-only, tidak menyentuh business logic produksi).

**Cek tabrakan nama method dengan Odoo core (dua arah):**
1. **Arah 1:** Modul hanya mendefinisikan `action_open_stock_history` (nama unik, spesifik ke modul ini) pada `product.template` — grep `enterprise19.0/odoo/addons/stock`, `enterprise19.0/odoo/addons/product` untuk `def action_open_stock_history` → 0 match. Tidak ada override method core.
2. **Arah 2:** Field/method yang didefinisikan modul pada `product.template` (`action_open_stock_history` saja, tidak ada field baru) — dicek `native-target` (`enterprise19.0`) tidak menambahkan definisi baru dengan nama sama. Model `stock.history.view` sendiri adalah model milik modul ini (`_name = 'stock.history.view'`), tidak ada tabrakan dengan model core manapun.

- [x] Sudah dicek (kedua arah) — tidak ada tabrakan nama method/field dengan core/Enterprise.

## E. Perubahan Tak Tertelusuri (di luar spec)

- [x] Tidak ada perubahan yang tidak tertelusuri ke spec — dua temuan di luar spec awal (DIFF-15, DIFF-16) sudah ditelusuri balik dan didokumentasikan di `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md` SEBELUM diimplementasikan, sesuai prosedur ("STOP, jangan improvisasi, balik ke step 2/3 dulu" — lihat `06c_IMPLEMENTATION_LOG.md` "Temuan di Luar Spec").

## F. Kontribusi ke Knowledge Base

- [x] Ada — sudah dicatat di `migration-tool/migration-records/product_history_report_18.0_19.0/SUMMARY.md`: `<group expand=/string=>` dihapus (DIFF-01), `res.users.groups_id`→`group_ids` konfirmasi kedua (DIFF-02), `stock.move.name` dihapus total diganti `reference` compute (DIFF-15), threshold overflow `ButtonBox`/`.o_button_more` berubah (DIFF-16), dan resolusi open question xmlid `stock.picking_type_*` (DIFF-10 — terkonfirmasi aman).

## G. Verdict

- Ringkasan Issues: 0 🔴 · 1 🟡 · 3 🔵
- [x] ✅ **Lulus** — tidak ada 🔴, lanjut ke step 9 (sudah dieksekusi bersamaan dengan Step 6 G1 — hasil 9/9 test PASS sudah tersedia, lihat `09_devtest/09_DEV_TESTING.md`)
