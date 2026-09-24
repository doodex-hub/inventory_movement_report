# Test Plan (Migrasi) — product_history_report

**Step:** 5 — Acceptance Criteria & Test Plan
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`
**Tanggal:** 2026-09-24
**Status:** ✅ Selesai (step non-gate)

---

## Step 9 — Dev Testing

Eksekusi Mode C/D (AI jalankan Docker, Odoo 20 build-from-source `odoo20`, Chrome headless di container), selalu `down -v` + `--without-demo=all` lewat `docker-env/run-test.sh`. Dua run:
- **Run C (Community):** addons-path `odoo20` saja.
- **Run E (Enterprise):** addons-path `odoo20` + `enterprise20`, install tambahan `stock_enterprise,quality_control,stock_barcode`.

| AC | Deskripsi | Unit | Integration | Tour |
|---|---|---|---|---|
| AC-01-01 | Tombol di arch form | — | `test_ac_01_01_button_present_in_form_arch` | — |
| AC-01-02 | Action dict | — | `test_ac_01_02_action_open_stock_history_returns_expected_action` | — |
| AC-01-03 | Navigasi Community + filter group-by | — | — | `test_stock_history_tour` (Run C; skip di Run E) |
| AC-01-04 | Ikon Material (arch + DOM) | — | `test_ac_01_04_button_icon_is_material_signal` (arch) | `test_stock_history_form_tour` (DOM `data-icon`) |
| AC-01-05 | Klik dari form → graph, kedua edisi | — | — | `test_stock_history_form_tour` (Run C & E) |
| AC-02-01 | Saldo pembuka | — | `test_ac_02_01_qty_includes_pre_window_balance` | — |
| AC-02-02 | Race condition tetap | — | Code identity (Step 8 diff kosong `models/`) | — |
| AC-03-01 | Return → income | — | `test_ac_03_01_customer_return_is_income_only` | — |
| AC-03-02 | Double-count internal | — | `test_ac_03_02_internal_transfer_counted_as_both_income_and_outcome` | — |
| AC-04-01 | Filter company | — | `test_ac_04_01_company_filter_excludes_other_company` | — |
| AC-05-01 | Read user internal tanpa grup stock | — | `test_ac_05_01_read_open_for_user_without_inventory_group` | — |
| AC-05-02 | Create gagal di DB | — | `test_ac_05_02_create_on_view_fails` | — |
| AC-05-03 | Isi record `ir.access` | — | `test_ac_05_03_acl_record_is_group_everyone_crud` | — |
| AC-05-04 | Read user portal | — | `test_ac_05_04_read_open_for_portal_user` | — |
| AC-06-01 | Enterprise | — | Seluruh suite di Run E | `test_stock_history_form_tour` di Run E |

Total rencana: 11 Integration + 2 Tour = 13 test method (Run C: 13 jalan; Run E: 12 jalan + 1 skip).

**Baseline cross-check (opsional tapi direncanakan):** AC-05-04 adalah test baru — untuk membuktikan klaim "19.0 juga mengizinkan portal" (bukan cuma asumsi dari semantik `ir.model.access`), jalankan test portal yang sama terhadap kode `migration/19.0` di image `product_history_report_migration_19-odoo_target` yang sudah ada di host (salinan kode via `git archive`, tanpa worktree).

## Step 10 — QA Testing

> **Tidak dijalankan di sesi ini** — instruksi dev: STOP sebelum Step 10 sampai diberi slot (kontensi browser/Docker lintas repo). Rencana mode saat giliran tiba (lesson 17→18 & 18→19: AI-interaktif browser gagal di environment ini, pakai Tour + Integration):

| AC | Deskripsi | Manual | AI-interaktif | AI+tool eksternal |
|---|---|---|---|---|
| AC-01-01..05 | Tombol, ikon, navigasi, graph | — | Playwright MCP (verifikasi visual ikon + screenshot) kalau slot tersedia | — |
| AC-02..AC-05 | Isi laporan & akses | — | — (tercakup Step 9) | — |

## Step 11 — UAT

| Kelompok fitur | AC tercakup | UAT |
|---|---|---|
| Tombol & laporan | AC-01, AC-02, AC-03, AC-04 | Manual business user |
| Akses | AC-05 | Manual |

## Ringkasan

| Step | Role | Tipe | Eksekusi | Jumlah AC |
|---|---|---|---|---|
| 9 | Developer (AI) | Integration + Tour | Otomatis Docker (Run C + Run E) | 16 |
| 10 | QA | Tour/Playwright | Menunggu slot dev | 5 (visual) |
| 11 | PM/FA/User | UAT | Manual | 16 |
