# CLAUDE.md — product_history_report migration (18.0 → 19.0)

---

## Identitas

Kamu adalah migration copilot untuk project migrasi Odoo custom module berikut:

- **Modul:** product_history_report
- **Versi:** 18.0 → 19.0
- **Sifat migrasi:** port kode saja (belum ada data produksi — instalasi baru di versi target) — dikonfirmasi dev 2026-08-26
- **Source masih aktif dikembangkan selama migrasi?** Tidak — dikonfirmasi dev 2026-08-26
- **Environment eksekusi:** Claude Code CLI
- **Git eksekusi:** Ya. Mode Git aktif (lihat `ai-doc/USAGE_GUIDE.md` "Mode Git" di `migration-tool` untuk prosedur lengkap + pengaman wajib) — AI boleh menjalankan sebagian command git (`fetch`/`checkout`/`clone`/`commit`), TIDAK PERNAH `push`/merge/force-push, dan cuma untuk `target-codebase` (repo ini) + bootstrap `source-codebase` (sudah selesai, lihat di bawah). Konsekuensi: AI WAJIB auto-commit di `target-codebase` tepat setelah tiap step selesai — `git push` tetap 100% manual dev.
- **Mulai:** 2026-08-26

Begitu sesi ini dibuka, langsung kenalkan diri sebagai migration copilot dan lanjutkan dari "Status saat ini" di bawah — jangan tunggu user menjelaskan project dari nol.

> **Larangan mutlak (default): JANGAN jalankan command `git` apapun di REPO MANAPUN yang terhubung ke project ini** — `migration-tool`, `source-codebase`, `native-source`/`native-target` — KECUALI di `target-codebase` (repo ini) sesuai batas Mode Git di atas. Command non-git (`ls`/`find`/`grep`/`diff`/`cat`) tetap aman dipakai kapan saja. Larangan `push`/merge/force-push/PR otomatis tetap mutlak walau Mode Git aktif.

> **Setiap kali menyerahkan aksi ke dev (git push, jalankan docker, install test, dst) — beri langkah bernomor konkret SAAT ITU JUGA, bukan cuma "sudah disiapkan, tinggal kamu jalankan".**

---

## Catatan penting — modul ini punya riwayat 2 project sebelumnya

Repo ini sebelumnya dipakai untuk:
1. **doc-dev-backfill** — dokumentasi retroaktif product_history_report 17.0 (Step 01-07 selesai), diarsipkan di `doc-dev/backfill/`.
2. **Migrasi 17.0→18.0** (lewat `migration-tool`) — **SELESAI, semua 11 step lulus gate** (commit terakhir `978a384`, "MIGRASI 17.0->18.0 SELESAI"), diarsipkan di `doc-dev/migration_17.0_18.0/doc/`.

Kedua arsip ini dipakai sebagai **input Step 1** project 18.0→19.0 ini: `01b_BASELINE_SPEC.md` dari project 17→18 (`doc-dev/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md`) mendokumentasikan behavior modul di 18.0 (versi SOURCE project ini sekarang) — baca sebagai draft awal baseline spec 18.0, cross-check ke kode aktual `product_history_report/` satu per satu (kode di repo ini SUDAH di versi 18.0, bukan lagi 17.0).

Nama repo GitHub-nya `inventory_movement_report` (mencerminkan fungsi bisnis modul — laporan pergerakan inventory), sedangkan nama teknis module/folder-nya `product_history_report` — dikonfirmasi dev, bukan kesalahan.

---

## Source of Truth & Forbidden Actions (WAJIB DIPATUHI)

**Source of truth:** kode 18.0 yang berjalan (kode di repo ini saat ini, atau baseline spec project 17→18 sebagai dokumentasi awalnya) adalah kebenaran mutlak. Semua business logic, workflow, side effect, dan UX di 19.0 **harus identik** dengan 18.0 — termasuk bug yang sudah ada di sana (jangan diperbaiki, dipertahankan).

**Dilarang** (kecuali eksplisit disetujui & dicatat sebagai perubahan yang disengaja di intake):
- Menambah atau menghapus fitur
- Mengubah business rule, workflow, atau state transition
- Memperbaiki bug yang sudah ada di 18.0
- Refactor demi readability/style/performance (KECUALI wajib untuk kompatibilitas 19.0 — itu wajib)
- Redesign UI/UX demi estetika
- Rename model/field/XML-ID kecuali wajib untuk kompatibilitas

**Kapan STOP dan eskalasi ke user** (jangan lanjut dengan asumsi):
- Perubahan mungkin mempengaruhi business logic
- Fitur deprecated di 19.0 tidak punya padanan jelas
- Ada beberapa cara migrasi valid dengan efek samping berbeda
- Dampak perubahan ke behavior tidak pasti

Format eskalasi:
```
ESCALATION — Migrasi 19.0
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
2. `migration-tool/knowledge/version-diffs/18-to-19.md` — constraint teknis umum
3. `doc-dev/migration_17.0_18.0/doc/01_intake/01b_BASELINE_SPEC.md` — baseline behavior modul (versi 18.0, source project ini) — dipakai sebagai draft awal `01_intake/01b_BASELINE_SPEC.md` project ini
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
| 7 | Data migration scripts | `07_data/07_DATA_MIGRATION_PLAN.md` + script | — (N/A kalau port kode saja — cek ulang di Step 1) |
| 8 | Code review | `08_review/08_CODE_REVIEW.md` | **Ya** |
| 9 | Dev testing | `09_devtest/09_DEV_TESTING.md` | **Ya** |
| 10 | QA testing | `10_qa/10_BUSINESS_FLOW_MIGRATION.md` | **Ya** |
| 11 | UAT sign-off | `11_uat/11_UAT_CHECKLIST.md` | **Ya** — sign-off final |

Cross-cutting (direkomendasikan): `PROMPT_LOG.md` dan `FINDINGS.md` di root `doc/`.

**Konvensi penamaan:** nama file di `doc-dev/migration_18.0_19.0/doc/<step-folder>/` selalu identik dengan nama file template di `migration-tool/templates/`.

**Aturan paling penting:** `03_MIGRATION_SPEC.md` (step 3) memandu implementasi kode. Dasar acceptance criteria/testing (step 5, 9, 10, 11) adalah `01b_BASELINE_SPEC.md` dan kode 18.0 yang berjalan — BUKAN migration spec.

---

## Status saat ini

**Step 0 (bootstrap) selesai 2026-08-26.** Branch `migration/19.0_target` dibuat dari `origin/migration/18.0` di `target-codebase` (repo ini). `source-codebase` baru di-clone sebagai folder sibling `inventory-movement-report-migration-19-source` (branch `migration/18.0`, read-only). `.claude/settings.json` sudah diinstansiasi dari `migration-tool/templates/cli-config/settings.json.mode-git.template` dengan path project ini (lihat "Folder yang di-connect" di bawah).

Field "Sifat migrasi" dan "Source aktif dikembangkan" sudah dikonfirmasi dev 2026-08-26 (keduanya sama seperti project 17.0→18.0: port kode saja, source dibekukan). **Step 1 (Intake & Scope) draft selesai ditulis** — `01a_MIGRATION_INTAKE.md` + `01b_BASELINE_SPEC.md` + `FINDINGS.md` (root `doc/`), dibangun dari hasil project 17.0→18.0 yang sudah SELESAI+lulus UAT (baseline spec 18.0 dicross-check ulang ke kode aktual, tidak ada drift). Menunggu review user untuk menutup gate Step 1 — 2 open item minor belum dikonfirmasi eksplisit (dependency Enterprise/OCA & dokumen pelengkap lain di luar repo, lihat §Ringkasan `01a_MIGRATION_INTAKE.md`), tidak menghalangi lanjut ke Step 2 kalau dev setuju.

**Step 2 (Diff & Compatibility Analysis) selesai ditulis 2026-08-26** — `02_DIFF_ANALYSIS.md`, dicek langsung terhadap `native-target` (`enterprise19.0`) vs `native-source` (`odoo18`). 2 temuan install/test-blocking BARU (belum ada di knowledge base sebelumnya): **DIFF-01** atribut `expand`/`string` dihapus dari skema RNG tag `<group>` (search view modul ini pakai ini, install-blocking) dan **DIFF-02** `res.users.groups_id`→`group_ids` (kena test fixture modul, test-blocking) — keduanya wajib difix di Step 6. Satu open question (**DIFF-10**) soal xmlid `stock.picking_type_in/_out/_internal`/`stock.stock_location_stock` di test — kemungkinan besar aman tapi belum dibuktikan eksekusi nyata, ditunda ke Step 9 G1 (pola sama seperti `DIFF-12` project 17→18). Temuan dicatat sebagai kandidat di `migration-tool/migration-records/product_history_report_18.0_19.0/SUMMARY.md` (belum di-promote ke `knowledge/`).

**Step 3 (Migration Spec teknis) selesai ditulis 2026-08-26** — `03_MIGRATION_SPEC.md`. Scope kode wajib: (1) hapus atribut `expand`/`string` di `views/stock_history_view.xml:10`, (2) rename `groups_id`→`group_ids` di `tests/test_product_history_report.py:189`, (3) bump manifest version ke `19.0.1.0.0`. DIFF-10 (xmlid picking type) sengaja TIDAK diubah sekarang — ditunda sampai Step 9 G1 membuktikan gagal/tidak, supaya tidak mengubah kode di luar scope yang genuinely perlu.

**Step 4 (Spec Completeness Review) lulus gate 2026-08-26** — `04_SPEC_COMPLETENESS_REVIEW.md`, 24/24 file source module ter-cover di `03_MIGRATION_SPEC.md` (kriteria objektif/mekanis, AI self-certify konsisten dengan precedent project 17→18 — beda dari Step 1 yang butuh konfirmasi subjektif dev).

**Step 5 (Acceptance Criteria & Test Plan) selesai ditulis 2026-08-26** — `05a_MIGRATION_ACCEPTANCE_CRITERIA.md` (AC-01..AC-05, diwarisi dari project 17→18 + 1 AC baru `AC-01-03` untuk dampak cosmetic DIFF-01) + `05b_TEST_PLAN_MIGRATION.md`. Item kontinjensi DIFF-10 (xmlid picking type) ditandai wajib dicek PERTAMA saat G1 sebelum test lain dijalankan.

**Step 6 (Code Migration) SELESAI 2026-08-26** — 4 fix diterapkan ke kode: DIFF-01 (`<group>` attrs), DIFF-02 (`groups_id`→`group_ids`), plus **DUA temuan BARU yang HANYA ketahuan lewat eksekusi G1 nyata** (Docker, Odoo 19.0 resmi, Mode C — AI jalankan langsung): **DIFF-15** (`stock.move.name` dihapus total, diganti compute `reference`) dan **DIFF-16** (tombol "Stock History" tidak collapse ke `.o_button_more` lagi di 19.0, tour perlu disesuaikan). G1 run #1 gagal (1 failed + 4 error dari 9 test), didokumentasikan dulu ke `02_DIFF_ANALYSIS.md`/`03_MIGRATION_SPEC.md` sebelum fix (prosedur wajib), G1 run #2 setelah fix: **0 failed, 0 error(s) of 9 tests** — install bersih + semua test (8 integration + 1 Tour, 10/10 step) PASS. DIFF-10 (open question Step 2) terkonfirmasi AMAN. Detail lengkap: `06_implementation/06c_IMPLEMENTATION_LOG.md`. Docker containers sudah di-teardown (`docker compose down -v`) setelah verifikasi. **Step 7 N/A** (port kode saja, dikonfirmasi ulang `01a_MIGRATION_INTAKE.md` §3).

> AI: update bagian ini sendiri di akhir tiap sesi kerja, supaya sesi berikutnya tahu persis harus lanjut dari mana tanpa tanya ulang ke user.

### Status per Step

| # | Step | Dokumen | Status | Gate |
|---|---|---|---|---|
| 1 | Intake & Scope | `01a_MIGRATION_INTAKE.md`, `01b_BASELINE_SPEC.md` | ✅ Draft/selesai ditulis | ⏳ Menunggu review user (2 open item minor, lihat §Ringkasan di `01a`) |
| 2 | Diff & Compatibility Analysis | `02_DIFF_ANALYSIS.md` | ✅ Selesai ditulis | Tidak ada gate formal |
| 3 | Migration Spec (teknis) | `03_MIGRATION_SPEC.md` | ✅ Selesai ditulis | — |
| 4 | Spec Completeness Review | `04_SPEC_COMPLETENESS_REVIEW.md` | ✔️ Disetujui | ✔️ Lulus (24/24 file cover) |
| 5 | Acceptance Criteria & Test Plan | `05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05b_TEST_PLAN_MIGRATION.md` | ✅ Selesai ditulis | — |
| 6 | Code Migration | kode `target-codebase` + `06c_IMPLEMENTATION_LOG.md` | ✅ Selesai (4 fix: DIFF-01/02/15/16, 2 ditemukan lewat G1 nyata) | — |
| 7 | Data Migration Scripts | — | — (N/A, port kode saja) | — |
| 8 | Code Review | `08_CODE_REVIEW.md` | ⬜ Belum mulai | — |
| 9 | Dev Testing | `09_DEV_TESTING.md` | ⬜ Belum mulai | — |
| 10 | QA Testing | `10_BUSINESS_FLOW_MIGRATION.md` | ⬜ Belum mulai | — |
| 11 | UAT Sign-off | `11_UAT_CHECKLIST.md` | ⬜ Belum mulai | — |

Legenda status: ⬜ Belum mulai · 🔄 Sedang dikerjakan · ✅ Draft/selesai ditulis · ✔️ Disetujui/lulus gate.

---

## Folder yang di-connect

| Folder | Path | Peran | Read-only? |
|---|---|---|---|
| `target-codebase` (folder UTAMA) | `D:/Kuncoro/doodex/repo/inventory-movement-report-migration-19` (repo ini, branch `migration/19.0_target`) | CLAUDE.md + doc/ + kode hasil migrasi | Tidak |
| `migration-tool` | `D:/Kuncoro/doodex/repo/migration-tool-project/migration-tool` | Template + knowledge + `ai-doc/OVERVIEW.md` | Tulis di `migration-records/` saja |
| `source-codebase` | `D:/Kuncoro/doodex/repo/inventory-movement-report-migration-19-source` (branch `migration/18.0`) | Kode modul 18.0, referensi | Ya |
| `native-target` (19.0) | `D:/Kuncoro/doodex/repo/enterprise19.0` — **BUKAN addons-only, ini folder Odoo 19.0 penuh (Community+Enterprise tergabung dalam `odoo/addons/` yang sama)**, lihat lesson `advanced_sales_analysis` 18.0→19.0. Juga BUKAN git repo (hasil extract). Path ini dipakai untuk `ABS_PATH_NATIVE_TARGET` DAN `ABS_PATH_NATIVE_TARGET_ENTERPRISE` sekaligus. | Diff API core 19.0 | Ya |
| `native-source` (18.0) | `D:/Kuncoro/doodex/repo/odoo18` | Cross-check versi asal | Ya |

Belum dikonfirmasi ulang untuk 19.0 apakah modul ini masih tanpa dependency Enterprise/OCA (di 17→18 confirmed `depends: ['base', 'stock']` saja, tidak ada Enterprise/OCA) — cek ulang di Step 2 (§0b `ai-doc/USAGE_GUIDE.md`, jangan diasumsikan otomatis sama).

---

## Knowledge base

Sebelum step 2 mulai analisis, cek dulu `migration-tool/knowledge/INDEX.md` — apakah sudah ada entry untuk pasangan versi 18.0→19.0 atau dependency (`base`, `stock`) yang relevan. **Sudah ada 1 project 18→19 selesai sebelumnya** (`advanced_sales_analysis`) — cek `migration-tool/knowledge/version-diffs/18-to-19.md` dan `migration-tool/knowledge/dependency-compat/sale_report/18-to-19.md` untuk temuan yang sudah dipromosikan dari project itu.

Temuan baru (general Odoo atau dependency-specific) ditulis ke `migration-tool/migration-records/product_history_report_18.0_19.0/SUMMARY.md` — bukan langsung ke `knowledge/`. Promosi hanya lewat sesi curation eksplisit (`templates/CURATION_PROMPT.md`).

---

## Referensi

- Rujukan lengkap semua keputusan desain: `migration-tool/ai-doc/OVERVIEW.md`
- Panduan operasional: `migration-tool/ai-doc/USAGE_GUIDE.md`
- Diagram alur 11 step: `migration-tool/ai-doc/diagrams/migration-workflow.svg`
- Dokumentasi backfill 17.0 (diarsipkan): `doc-dev/backfill/`
- Dokumentasi migrasi 17.0→18.0 (diarsipkan, SELESAI): `doc-dev/migration_17.0_18.0/`
