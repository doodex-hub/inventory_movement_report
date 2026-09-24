# Dev Testing — product_history_report

**Step:** 9 — Dev Testing (gate)
**Ref:** `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `05_acceptance/05b_TEST_PLAN_MIGRATION.md`, `01_intake/01b_BASELINE_SPEC.md`
**Tanggal:** 2026-09-24
**Status:** ✔️ Lulus gate

Eksekusi Mode C/D lewat `docker-env/run-test.sh` (Odoo 20.0 build-from-source `odoo20` HEAD `b0329e93ae8`, `enterprise20` HEAD `bbccc6bce1`, Chrome 153 headless di container, DB baru tiap run, tanpa demo).

---

## 9a. Audit Kesiapan Test

- Registrasi: `tests/__init__.py` meng-import `test_product_history_report` dan `test_stock_history_tour` — kedua file ter-load.
- Isi method (parse `ast` di container, bukan grep nama): 13/13 method **Lengkap** (0 stub) — tiap method berisi ≥1 `assert*` atau `start_tour`.

| AC | Deskripsi | File test | Status | Catatan |
|---|---|---|---|---|
| AC-01-01 | Tombol di arch | `test_product_history_report.py::test_ac_01_01_…` | ✅ Lengkap | |
| AC-01-02 | Action dict | `…::test_ac_01_02_…` | ✅ Lengkap | 3 assert |
| AC-01-03 | Navigasi Community + group-by | `test_stock_history_tour.py::test_stock_history_tour` | ✅ Lengkap | skip eksplisit di Enterprise |
| AC-01-04 ⚠️ | Ikon Material | `…::test_ac_01_04_…` + tour form step 2 | ✅ Lengkap | arch + DOM |
| AC-01-05 | Form → graph, 2 edisi | `test_stock_history_tour.py::test_stock_history_form_tour` | ✅ Lengkap | |
| AC-02-01 | Saldo pembuka | `…::test_ac_02_01_…` | ✅ Lengkap | |
| AC-02-02 | Race condition tetap | — | ✅ via code identity | `models/` 0 diff vs 19.0 (Step 8 §E) |
| AC-03-01/02 | income/outcome, double-count | `…::test_ac_03_01/02_…` | ✅ Lengkap | |
| AC-04-01 | Filter company | `…::test_ac_04_01_…` | ✅ Lengkap | |
| AC-05-01 ⚠️ | Read internal tanpa grup stock | `…::test_ac_05_01_…` | ✅ Lengkap | |
| AC-05-02 | Create gagal di DB | `…::test_ac_05_02_…` | ✅ Lengkap | |
| AC-05-03 ⚠️ | Record `ir.access` | `…::test_ac_05_03_…` | ✅ Lengkap | 6 assert |
| AC-05-04 ⚠️ | Read portal | `…::test_ac_05_04_…` | ✅ Lengkap | dijalankan juga di 19.0 (baseline) |
| AC-06-01 | Enterprise | seluruh suite di Run E | ✅ Lengkap | |

**Verdict audit:** semua AC risiko tinggi berstatus Lengkap → lanjut eksekusi.

## Baseline

- Test lama ada di lokasi yang sama dengan source (`01a` §4): `migration/19.0:product_history_report/tests/` (8 Integration + 1 Tour).
- **Run baseline 19.0 (2026-09-24):** salinan `git archive migration/19.0 product_history_report` di scratchpad + test portal AC-05-04 ditempel (hanya di salinan, tidak di-commit), dijalankan di image `product_history_report_migration_19-odoo_target` (Odoo 19.0, dari project 18→19) dengan Postgres 15 sementara → **`0 failed, 0 error(s) of 10 tests`**, tour 12/12 "tour succeeded". Membuktikan: (1) 9 test warisan tetap hijau di 19.0; (2) **user portal BISA membaca `stock.history.view` di 19.0** → BSL-007 "semua user" terkonfirmasi empiris, jadi `base.group_everyone` di 20.0 adalah padanan yang benar (bukan pelonggaran); (3) `ERROR Model stock.history.view has no table.` ×2 juga muncul di 19.0 → MF-09 terkonfirmasi `[DIWARISI-SOURCE]`.
- Applicability Check Fase E: N/A untuk kode aplikatif; tour test tetap wajib (ada 2, keduanya jalan).

## Hasil Unit, Integration & Tour Test (target-codebase `migration/20.0`)

| Run | Log | Hasil |
|---|---|---|
| **Run C** — Community (`./run-test.sh`) | `docker-env/logs/run-community-20260924-144814.log` | exit 0 — **`0 failed, 0 error(s) of 15 tests`**; 13 method modul ter-start (+2 `WebSuite`/`MobileWebSuite` milik `web`, kosong untuk modul ini); `stock_history_form_tour` tour succeeded; `stock_history_tour` 12/12 tour succeeded |
| **Run E** — Enterprise (`EDITION=enterprise ./run-test.sh`: `enterprise20` di addons-path, install `stock_enterprise,quality_control,stock_barcode`) | `docker-env/logs/run-enterprise-20260924-144123.log` | exit 0 — **`0 failed, 0 error(s) of 15 tests`**; 13 method ter-start, 12 pass + 1 skip (`test_stock_history_tour`, alasan: `web_enterprise` Home Menu, DIFF-12); `stock_history_form_tour` 5/5 tour succeeded |

| AC | Integration | Tour | Run C | Run E |
|---|---|---|---|---|
| AC-01-01 | ✅ | — | Pass | Pass |
| AC-01-02 | ✅ | — | Pass | Pass |
| AC-01-03 | — | `stock_history_tour` | Pass | Skip (by design) |
| AC-01-04 | ✅ | form tour (DOM `data-icon`) | Pass | Pass |
| AC-01-05 | — | form tour | Pass | Pass |
| AC-02-01, 03-01, 03-02, 04-01 | ✅ | — | Pass | Pass |
| AC-05-01..04 | ✅ | — | Pass | Pass |
| AC-06-01 | seluruh suite | form tour | — | Pass |

### Loop test→fix→test di step ini

| # | Run | Hasil | Akar masalah | Fix |
|---|---|---|---|---|
| 1 | Run E (`run-enterprise-20260924-143417.log`) | ❌ 1 failed of 15 — `stock_history_form_tour` step 1: elemen `button[name="action_open_stock_history"] i.o_button_icon[...]` tidak ditemukan (timeout 10 s) | Dengan modul Enterprise, form produk punya lebih banyak stat button; `ButtonBox` membatasi tombol yang tampil (`[0,0,7,4,5,8][ui.size]`) dan memindah sisanya ke dropdown **More** — logika **identik** di 19.0 (`odoo19/.../button_box.js:20`) dan 20.0 (`odoo20/.../button_box.js:19`). Bukan regresi modul; tour-nya yang tidak menangani overflow. 11 test Integration tetap PASS (install Enterprise sukses). | Tambah step pertama di `stock_history_form_tour.js`: klik `.o_button_more` HANYA bila tombol tidak ada di bagian terlihat button box (test code saja) |
| 2 | Run E (`run-enterprise-20260924-144123.log`) | ✅ 0 failed of 15, tour 5/5 | — | — |
| 3 | Run C ulang (`run-community-20260924-144814.log`) | ✅ 0 failed of 15 | regresi-check setelah ubah tour | — |

### Tidak dijalankan
- Probe eksploitasi untuk MF-10 (SQL injection via RPC) sengaja **tidak** dijalankan. Finding tetap berbasis analisis kode statis (`08_CODE_REVIEW.md` CR-01) dan dieskalasi ke dev. Setelah dev menyetujui, MF-10 diperbaiki di 20.0 (SCOPE-02) — lihat §Re-run di bawah.

## Kontribusi ke Knowledge Base

- [x] Ada — `migration-records/product_history_report_19.0_20.0/SUMMARY.md`: (1) tour stat button harus menangani dropdown **More** kalau dijalankan di instance dengan lebih banyak stat button (Enterprise); (2) baseline 19.0 bisa dijalankan murah dari image project sebelumnya + `git archive` (tanpa worktree).

## Verdict

- [x] ✅ Semua AC pass — Run C 13/13, Run E 12/12 + 1 skip by design, baseline 19.0 10/10. **Siap Step 10 — menunggu slot dari dev (STOP WAJIB sesuai instruksi).**
- [ ] ❌ Ada yang gagal

---

## Re-run pasca SCOPE-02/SCOPE-03 (2026-09-24)

| Run | Log | Hasil |
|---|---|---|
| Run C — Community | `docker-env/logs/run-community-20260924-150118.log` | exit 0 — **`0 failed, 0 error(s) of 17 tests`**; 15 method modul (13 Integration termasuk `test_ac_07_01`, `test_ac_07_02` + 2 Tour, keduanya "tour succeeded") |
| Run E — Enterprise | `docker-env/logs/run-enterprise-20260924-150648.log` | exit 0 — **`0 failed, 0 error(s) of 17 tests`**; 14 pass + 1 skip by design (tour Community) |

| AC | Integration | Run C | Run E |
|---|---|---|---|
| AC-07-01 (RPC ditolak, tombol tetap jalan) | `test_ac_07_01_recreate_view_not_callable_over_rpc` | Pass | Pass |
| AC-07-02 (argumen non-integer ditolak) | `test_ac_07_02_recreate_view_rejects_non_integer_arguments` | Pass | Pass |

Semua AC-01..AC-06 tetap Pass → fix tidak mengubah hasil laporan. **Verdict tetap ✅ Lulus — siap Step 10, menunggu slot dev.**
