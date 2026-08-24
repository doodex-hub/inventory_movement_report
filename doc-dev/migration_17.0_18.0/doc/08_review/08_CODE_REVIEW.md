# Code Review — product_history_report

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/06c_IMPLEMENTATION_LOG.md`, `01_intake/01b_BASELINE_SPEC.md`
**Odoo Version:** 18.0
**Files reviewed:** `__manifest__.py`, `models/product_template.py`, `models/stock_history_view.py`, `views/stock_history_view.xml`, `views/views.xml`, `security/ir.model.access.csv`, `tests/test_product_history_report.py`, `controllers/controllers.py` (diff terhadap `source-codebase` branch `migration/17.0_source`)
**Tanggal:** 2026-08-24

---

## A. Issues (Lint, Konvensi Odoo, Business Logic, Security, Performance, Code Quality)

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| REV-01 | 🔵 Info | Code Quality | `models/product_template.py`, `models/stock_history_view.py` | 3 | Import `from odoo.http import request` tidak dipakai (dead import, sudah ada sejak 17.0, bukan hasil migrasi) | Opsional dibersihkan — TIDAK wajib, di luar scope migrasi (`03_MIGRATION_SPEC.md` §4) |
| REV-02 | 🔵 Info | Code Quality | `models/product_template.py` | 28 | Key `'view_type': 'form'` sudah deprecated/tidak dipakai native manapun (DIFF-03), harmless | Opsional dibersihkan — TIDAK wajib |
| REV-03 | 🔵 Info | Code Quality | `views/stock_history_view.xml` | 63-74 | `action_stock_history_graph2`/`action_stock_history_tree2` tetap dead code (tidak terhubung `<menuitem>`) — sudah ada sejak 17.0, bukan hasil migrasi | Opsional dibersihkan — TIDAK wajib |
| REV-04 | 🟡 Warning | Konvensi Odoo | `models/stock_history_view.py` | 26-109 | SQL mentah via f-string ke `product_template_id`/`companies` — sudah ada sejak 17.0 (BR-02, `FINDINGS.md` MF-01), risiko SQL injection klasik RENDAH karena kedua nilai berasal dari `self.id`/`self.env.companies.ids` (integer ORM, bukan input user bebas), tapi pola f-string-ke-SQL tetap rapuh secara konvensi | Tidak diubah saat migrasi (bug/pola source dipertahankan, `03_MIGRATION_SPEC.md` §4) — dicatat ulang di sini murni untuk visibility reviewer, bukan actionable item migrasi |

**Tidak ada issue 🔴 Critical.** Semua temuan 🔵/🟡 di atas adalah warisan langsung dari source 17.0 (sudah tercatat `FINDINGS.md` MF-01..MF-04 atau `01b_BASELINE_SPEC.md` BSL-010/BSL-011), bukan regresi baru dari migrasi.

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item (`DIFF-NNN`/Fase) | Implementasi | Status | Catatan |
|---|---|---|---|
| DIFF-01 (`<tree>`→`<list>`) | `views/stock_history_view.xml` baris 51/59 | ✅ Match | Dikonfirmasi G1: install bersih, tidak ada `ParseError` |
| DIFF-02 (`view_mode` token) | `views/stock_history_view.xml` baris 66/73, `models/product_template.py` baris 29 | ✅ Match | Ketiga titik diupdate konsisten |
| DIFF-03 (`view_type` dead key) | Tidak diubah (opsional) | ✅ Match — sesuai spec (tidak wajib) | — |
| DIFF-04 s/d DIFF-11 | Tidak ada perubahan kode | ✅ Match | Sesuai spec (dikonfirmasi stabil, tidak perlu perubahan) |
| DIFF-12 (`product.template.type='product'`→`is_storable`) | `tests/test_product_history_report.py` baris 27 | ✅ Match | Ditemukan & difix di Fase G2 (lihat `06c_IMPLEMENTATION_LOG.md`), sudah diupdate ke `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md` sebelum fix diterapkan |
| Manifest version bump | `__manifest__.py` `'18.0.1.0.0'` | ✅ Match | — |

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC ID | Behavior | Status | Catatan |
|---|---|---|---|
| AC-01-01 | Tombol Stock History muncul di form | ✅ Match | Dikonfirmasi test `test_ac_01_01_button_present_in_form_arch` PASS (Step 9) |
| AC-01-02 | Window action `graph,pivot,list` terbuka | ✅ Match (token berubah sesuai DIFF-02, behavior sama) | Dikonfirmasi test `test_ac_01_02_...` PASS setelah assertion diupdate |
| AC-02-01 | qty running-sum mencakup saldo >13 bulan | ✅ Match | Dikonfirmasi test `test_ac_02_01_...` PASS |
| AC-02-02 | Race condition SQL view (dipertahankan, bukan ditest otomatis) | ✅ Match (by design, tidak ada test) | Konsisten `05b_TEST_PLAN_MIGRATION.md` — tidak ada regresi kode yang mengubah mekanisme ini |
| AC-03-01 | Move customer→internal = income saja | ✅ Match | Dikonfirmasi test PASS |
| AC-03-02 | Double-count internal→internal DIPERTAHANKAN | ✅ Match | Dikonfirmasi test PASS — bug MF-02 terbukti masih terjadi identik di 18.0 |
| AC-04-01 | Filter multi-company | ✅ Match | Dikonfirmasi test PASS |
| AC-05-01 | ACL terbuka tanpa grup (dipertahankan) | ✅ Match | Dikonfirmasi test PASS |
| AC-05-02 | create/write/unlink gagal di DB | ✅ Match | Dikonfirmasi test PASS |

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — semua deviasi dari source (`source-codebase`) sudah eksplisit tercatat & disetujui (hanya 3 titik `tree`→`list`, 1 titik `type`→`is_storable` di test, 1 bump version — semua mekanis, tidak menyentuh business logic).

**Cek tabrakan nama method dengan Odoo core (dua arah):**
1. **Arah 1:** Modul hanya mendefinisikan `action_open_stock_history` (nama unik, spesifik ke modul ini) pada `product.template` — grep `odoo18/addons/stock`, `odoo18/addons/product` untuk `def action_open_stock_history` → 0 match. Tidak ada override method core.
2. **Arah 2:** Field/method yang didefinisikan modul pada `product.template` (`action_open_stock_history` saja, tidak ada field baru) — dicek `native-target` (`odoo18`) tidak menambahkan definisi baru dengan nama sama. Model `stock.history.view` sendiri adalah model BARU milik modul ini (`_name = 'stock.history.view'`), tidak ada tabrakan dengan model core manapun.

- [x] Sudah dicek (kedua arah) — tidak ada tabrakan nama method/field dengan core/Enterprise.

## E. Perubahan Tak Tertelusuri (di luar spec)

- [x] Tidak ada perubahan yang tidak tertelusuri ke spec — satu temuan di luar spec awal (DIFF-12) sudah ditelusuri balik dan didokumentasikan di `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md` SEBELUM diimplementasikan, sesuai prosedur ("STOP, jangan improvisasi, balik ke step 3/4 dulu" — lihat `06c_IMPLEMENTATION_LOG.md` "Temuan di Luar Spec").

## F. Kontribusi ke Knowledge Base

- [x] Ada — sudah dicatat di `migration-tool/migration-records/product_history_report_17.0_18.0/SUMMARY.md`: **CAND-01** (`product.template.type='product'` dihapus 18.0, ganti `is_storable`). Lihat juga entry sebelumnya di file yang sama: catatan struktural `doc-dev-backfill`, `[REPO-NAMING]`, `[DEPENDENCY-COMPAT] stock`, dan konfirmasi ulang `<tree>`→`<list>` juga berlaku untuk token `view_mode`.

## G. Verdict

- Ringkasan Issues: 0 🔴 · 1 🟡 · 3 🔵
- [x] ✅ **Lulus** — tidak ada 🔴, lanjut ke step 9 (sudah dieksekusi bersamaan, lihat `09_devtest/09_DEV_TESTING.md` — hasil 8/8 test pass sudah tersedia dari Fase G2 step 6)
