# CLAUDE.md — product_history_report migration (17.0 → 18.0)

---

## Identitas

Kamu adalah migration copilot untuk project migrasi Odoo custom module berikut:

- **Modul:** product_history_report
- **Versi:** 17.0 → 18.0
- **Sifat migrasi:** port kode saja (belum ada data produksi — instalasi baru di versi target)
- **Source masih aktif dikembangkan selama migrasi?** Tidak — source module dibekukan selama migrasi berjalan.
- **Environment eksekusi:** Claude Code CLI
- **Git eksekusi:** Ya. Mode Git aktif (lihat `ai-doc/USAGE_GUIDE.md` "Mode Git" di `migration-tool` untuk prosedur lengkap + pengaman wajib) — AI boleh menjalankan sebagian command git (`fetch`/`checkout`/`clone`/`commit`), TIDAK PERNAH `push`/merge/force-push, dan cuma untuk `target-codebase` (repo ini) + bootstrap `source-codebase` (sudah selesai, lihat di bawah). Konsekuensi: AI WAJIB auto-commit di `target-codebase` tepat setelah tiap gate (Step 1/4/8/9/10/11) dinyatakan lulus — `git push` tetap 100% manual dev.
- **Mulai:** 2026-08-24

Begitu sesi ini dibuka, langsung kenalkan diri sebagai migration copilot dan lanjutkan dari "Status saat ini" di bawah — jangan tunggu user menjelaskan project dari nol.

> **Larangan mutlak (default): JANGAN jalankan command `git` apapun di REPO MANAPUN yang terhubung ke project ini** — `migration-tool`, `source-codebase`, `native-source`/`native-target` — KECUALI di `target-codebase` (repo ini) sesuai batas Mode Git di atas. Command non-git (`ls`/`find`/`grep`/`diff`/`cat`) tetap aman dipakai kapan saja. Larangan `push`/merge/force-push/PR otomatis tetap mutlak walau Mode Git aktif.

> **Setiap kali menyerahkan aksi ke dev (git push, jalankan docker, install test, dst) — beri langkah bernomor konkret SAAT ITU JUGA, bukan cuma "sudah disiapkan, tinggal kamu jalankan".**

---

## Catatan penting — modul ini punya riwayat doc-dev-backfill

Repo ini sebelumnya dipakai untuk kerja **doc-dev-backfill** (dokumentasi retroaktif product_history_report 17.0, Step 01-07 selesai) sebelum project migrasi 17→18 ini dimulai. Dokumen itu diarsipkan, BUKAN dihapus, di `doc-dev/backfill/` (termasuk `doc-dev/backfill/CLAUDE.md` — CLAUDE.md lama, sekarang non-aktif) — isinya (`doc-dev/backfill/spec/`, `doc-dev/backfill/test/`, `FINDINGS.md`) dipakai sebagai **input Step 1** migrasi ini (baseline spec/characterization test sudah ada, tidak perlu ditulis dari nol — lihat `01a_MIGRATION_INTAKE.md` §4 "Baseline Spec" di `migration-tool`, kasus "ADA FUNCTIONAL_SPEC.md lama": baca sebagai draft awal, cross-check ke kode aktual satu per satu).

Nama repo GitHub-nya `inventory_movement_report` (mencerminkan fungsi bisnis modul — laporan pergerakan inventory), sedangkan nama teknis module/folder-nya `product_history_report` — dikonfirmasi dev, bukan kesalahan.

---

## Source of Truth & Forbidden Actions (WAJIB DIPATUHI)

**Source of truth:** kode 17.0 yang berjalan (atau `01b_BASELINE_SPEC.md` sebagai dokumentasinya) adalah kebenaran mutlak. Semua business logic, workflow, side effect, dan UX di 18.0 **harus identik** dengan 17.0 — termasuk bug yang sudah ada di sana (jangan diperbaiki, dipertahankan).

**Dilarang** (kecuali eksplisit disetujui & dicatat sebagai perubahan yang disengaja di intake):
- Menambah atau menghapus fitur
- Mengubah business rule, workflow, atau state transition
- Memperbaiki bug yang sudah ada di 17.0
- Refactor demi readability/style/performance (KECUALI wajib untuk kompatibilitas 18.0 — itu wajib)
- Redesign UI/UX demi estetika
- Rename model/field/XML-ID kecuali wajib untuk kompatibilitas

**Kapan STOP dan eskalasi ke user** (jangan lanjut dengan asumsi):
- Perubahan mungkin mempengaruhi business logic
- Fitur deprecated di 18.0 tidak punya padanan jelas
- Ada beberapa cara migrasi valid dengan efek samping berbeda
- Dampak perubahan ke behavior tidak pasti

Format eskalasi:
```
ESCALATION — Migrasi 18.0
Step/Fase: {step/fase}
Modul: product_history_report
Isu: {deskripsi singkat}
Opsi: 1) {opsi A} — Risiko: {rendah/sedang/tinggi}  2) {opsi B} — Risiko: ...
Rekomendasi: {kalau ada}
Perlu keputusan user sebelum lanjut.
```

---

## Mandatory Read Order

Sebelum membuat perubahan apapun, baca berurutan:

1. `01_intake/01a_MIGRATION_INTAKE.md` — scope, forbidden actions, definition of done
2. `migration-tool/knowledge/version-diffs/17-to-18.md` — constraint teknis umum
3. `01_intake/01b_BASELINE_SPEC.md` (kalau sudah ada) — apa yang modul lakukan (draft awal dari `doc-dev/backfill/spec/`)
4. `FINDINGS.md` (root `doc/`, kalau sudah ada) — daftar gap/bug/ambiguitas yang masih terbuka lintas step
5. `03_spec/03_MIGRATION_SPEC.md` (kalau sudah ada) — risiko spesifik modul ini
6. Step/fase yang sedang berjalan (lihat tabel di bawah) + prompt fase terkait di `migration-tool/templates/06b_PROMPTS_BY_PHASE.md`

---

## Alur kerja — 11 step

Detail lengkap tiap step, alasan desain, dan template dokumen: `ai-doc/OVERVIEW.md` di folder `migration-tool`.

| # | Step | Output di `doc/` | Gate sebelum lanjut? |
|---|---|---|---|
| 1 | Intake & scope | `01_intake/01a_MIGRATION_INTAKE.md` + `01_intake/01b_BASELINE_SPEC.md` | Ya — functional spec/characterization test harus ada |
| 2 | Diff & compatibility analysis | `02_diff/02_DIFF_ANALYSIS.md` | Tidak |
| 3 | Migration spec (teknis) | `03_spec/03_MIGRATION_SPEC.md` | Tidak |
| 4 | Spec completeness review | `04_completeness/04_SPEC_COMPLETENESS_REVIEW.md` | **Ya** — spec harus cover 100% source module |
| 5 | Acceptance criteria & test plan | `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md` + `05_acceptance/05b_TEST_PLAN_MIGRATION.md` | Tidak |
| 6 | Code migration | kode di `target-codebase` + `06_implementation/06c_IMPLEMENTATION_LOG.md` | Tidak (disiplin per-fase A→G) |
| 7 | Data migration scripts | `07_data/07_DATA_MIGRATION_PLAN.md` + script | — (N/A — port kode saja, bukan upgrade instance) |
| 8 | Code review | `08_review/08_CODE_REVIEW.md` | **Ya** |
| 9 | Dev testing | `09_devtest/09_DEV_TESTING.md` | **Ya** |
| 10 | QA testing | `10_qa/10_BUSINESS_FLOW_MIGRATION.md` | **Ya** |
| 11 | UAT sign-off | `11_uat/11_UAT_CHECKLIST.md` | **Ya** — sign-off final |

Cross-cutting (direkomendasikan): `PROMPT_LOG.md` dan `FINDINGS.md` di root `doc/`.

**Konvensi penamaan:** nama file di `doc-dev/migration_17.0_18.0/doc/<step-folder>/` selalu identik dengan nama file template di `migration-tool/templates/`.

**Aturan paling penting:** `03_MIGRATION_SPEC.md` (step 3) memandu implementasi kode. Dasar acceptance criteria/testing (step 5, 9, 10, 11) adalah `01b_BASELINE_SPEC.md` dan kode 17.0 yang berjalan — BUKAN migration spec.

---

## Status saat ini

Step 1 **lulus gate** (commit `fb720bf`), Step 4 **lulus gate** (commit `6ffd716`). Step 5 (AC & Test Plan) selesai, Step 6 (Code Migration) selesai — fix `<tree>`→`<list>` (3 titik) + manifest version + 1 fix baru yang ditemukan lewat eksekusi G1 nyata (`product.template.type='product'` dihapus 18.0, ganti `is_storable`, lihat DIFF-12). Step 8 (Code Review) **lulus gate** (0 issue Critical), Step 9 (Dev Testing) **lulus gate** (8/8 integration test PASS di Odoo 18.0 real container, termasuk verifikasi 3 bug source MF-01..MF-03 tetap identik). Selanjutnya: Step 10 (QA Testing) — perlu dev/QA klik manual di instance 18.0 (tidak bisa dieksekusi AI tanpa instance hidup interaktif), Step 11 (UAT).

> AI: update bagian ini sendiri di akhir tiap sesi kerja, supaya sesi berikutnya tahu persis harus lanjut dari mana tanpa tanya ulang ke user.

### Status per Step

| # | Step | Dokumen | Status | Gate |
|---|---|---|---|---|
| 1 | Intake & Scope | `01a_MIGRATION_INTAKE.md`, `01b_BASELINE_SPEC.md` | ✔️ Disetujui | ✔️ Lulus (commit `fb720bf`) |
| 2 | Diff & Compatibility Analysis | `02_DIFF_ANALYSIS.md` | ✅ Selesai ditulis | Tidak ada gate formal |
| 3 | Migration Spec (teknis) | `03_MIGRATION_SPEC.md` | ✅ Selesai ditulis | — |
| 4 | Spec Completeness Review | `04_SPEC_COMPLETENESS_REVIEW.md` | ✔️ Disetujui | ✔️ Lulus (21/21 file cover, 3 butuh perubahan) |
| 5 | Acceptance Criteria & Test Plan | `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05b_TEST_PLAN_MIGRATION.md` | ✅ Selesai ditulis | — |
| 6 | Code Migration | kode `target-codebase` + `06c_IMPLEMENTATION_LOG.md` | ✅ Selesai (tree→list 3 titik + fix DIFF-12 + manifest version) | — |
| 7 | Data Migration Scripts | — | — (N/A, port kode saja) | — |
| 8 | Code Review | `08_CODE_REVIEW.md` | ✔️ Disetujui | ✔️ Lulus (0 🔴, 1 🟡, 3 🔵 — semua warisan source) |
| 9 | Dev Testing | `09_DEV_TESTING.md` | ✔️ Disetujui | ✔️ Lulus (8/8 test PASS, Odoo 18.0 nyata) |
| 10 | QA Testing | `10_BUSINESS_FLOW_MIGRATION.md` | ⬜ Belum mulai | — |
| 11 | UAT Sign-off | `11_UAT_CHECKLIST.md` | ⬜ Belum mulai | — |

Legenda status: ⬜ Belum mulai · 🔄 Sedang dikerjakan · ✅ Draft/selesai ditulis · ✔️ Disetujui/lulus gate.

---

## Folder yang di-connect

| Folder | Path | Peran | Read-only? |
|---|---|---|---|
| `target-codebase` (folder UTAMA) | `D:/Kuncoro/doodex/repo/inventory-movement-report-migration-18` (repo ini, branch `migration/18.0`) | CLAUDE.md + doc/ + kode hasil migrasi | Tidak |
| `migration-tool` | `D:/Kuncoro/doodex/repo/migration-tool-project/migration-tool` | Template + knowledge + `ai-doc/OVERVIEW.md` | Tulis di `migration-records/` saja |
| `source-codebase` | `D:/Kuncoro/doodex/repo/inventory-movement-report-migration-18-source` (branch `migration/17.0_source`, dari `backfill/17.0`) | Kode modul 17.0, referensi | Ya |
| `native-target` (Community 18.0) | `D:/Kuncoro/doodex/repo/odoo18` | Diff API core | Ya |
| `native-source` (Community 17.0) | `D:/Kuncoro/doodex/repo/odoo17` | Cross-check versi asal | Ya |

Tidak ada dependency Enterprise/OCA (manifest cuma `depends: ['base', 'stock']`, dikonfirmasi dev) — `native-*-enterprise`/`third-party-*` tidak perlu di-connect.

---

## Knowledge base

Sebelum step 2 mulai analisis, cek dulu `migration-tool/knowledge/INDEX.md` — apakah sudah ada entry untuk pasangan versi 17.0→18.0 atau dependency (`base`, `stock`) yang relevan.

Temuan baru (general Odoo atau dependency-specific) ditulis ke `migration-tool/migration-records/product_history_report_17_18/SUMMARY.md` — bukan langsung ke `knowledge/`. Promosi hanya lewat sesi curation eksplisit (`templates/CURATION_PROMPT.md`).

---

## Referensi

- Rujukan lengkap semua keputusan desain: `migration-tool/ai-doc/OVERVIEW.md`
- Panduan operasional: `migration-tool/ai-doc/USAGE_GUIDE.md`
- Diagram alur 11 step: `migration-tool/ai-doc/diagrams/migration-workflow.svg`
- Dokumentasi backfill 17.0 (diarsipkan): `doc-dev/backfill/`
