# Prompt Log — product_history_report (19.0 → 20.0)

**Tujuan:** data empiris untuk `ai-doc/ROADMAP.md` Fase 5 — prompt flow normal vs tool-fix per step. Klasifikasi mengikuti `migration-tool/templates/PROMPT_LOG.md`.

## Log per Step

| Step | # Prompt Normal | # Prompt Tool-fix | Catatan |
|---|---|---|---|
| 0 — Bootstrap (conditioning) | — | — | Dikerjakan sesi terpisah sebelum sesi ini (tidak tercatat di sini) |
| 1 — Intake & Baseline Spec | 2 | 0 | 1 prompt kickoff (Step 1→9 non-stop, STOP sebelum Step 10) + 1 jawaban AskUserQuestion intake (4 pertanyaan) |
| 2 — Diff & Compatibility Analysis | 0 | 0 | Dijalankan otomatis dari prompt kickoff |
| 3 — Migration Spec | 0 | 0 | idem |
| 4 — Spec Completeness Review | 0 | 0 | idem |
| 5 — Acceptance Criteria & Test Plan | 0 | 0 | idem |
| 6 — Code Migration (semua fase A-G2) | 0 | 0 | idem |
| 7 — Data Migration Scripts | — | — | N/A (port kode saja) |
| 8 — Code Review | 0 | 0 | idem |
| 9 — Dev Testing (+ fix pasca-gate) | 1 | 0 | Prompt dev: setujui fix MF-10 di 20.0 (catat sebagai fix baru, versi sebelumnya belum) + "sesuaikan" MF-08 → SCOPE-02/03, re-run Run C/E |
| 10 — QA Testing | 1 | 0 | Prompt dev "lanjut step 10" (slot diberikan) |
| 11 — UAT Sign-off | 1 | 0 | Prompt dev "lanjut step 11, sign-off percaya test AI" |
| **Total** | 5 | 0 | |

## Catatan Definisi

*(belum ada revisi)*

## Ringkasan Akhir Project

- Step dengan rasio Tool-fix tertinggi: tidak ada (0 prompt tool-fix sepanjang project).
- Step paling "bersih": Step 2–8 berjalan otomatis dari satu prompt kickoff tanpa intervensi (0 prompt). Prompt manusia hanya di titik yang memang didesain untuk keputusan/izin: intake (1 jawaban), persetujuan fix MF-10/MF-08 (1), slot Step 10 (1), sign-off Step 11 (1), plus kickoff (1) — total 5.
- Catatan: satu output berhenti karena safety classifier di awal Step 9 (rencana probe eksploitasi MF-10) — bukan prompt user; probe dibatalkan, finding tetap berbasis analisis statis.
