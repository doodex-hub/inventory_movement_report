# Migration Spec (Teknis) — product_history_report

**Step:** 3 — Migration Spec
**Versi:** 18.0 → 19.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-26

> Dokumen ini memandu IMPLEMENTASI (step 6). Ini **bukan** dasar testing/acceptance criteria —
> itu datang dari `01b_BASELINE_SPEC.md` (step 1). Lihat step 5.

---

## 1. Ringkasan Strategi

Modul kecil, murni backend (1 model extend + 1 SQL view + 2 file view XML + 1 baris ACL, tidak ada JS/Owl/controller aktif, kecuali 1 test tour). **Hampir seluruhnya port langsung 1:1** — dua perubahan wajib: (1) hapus atribut `expand`/`string` dari tag `<group>` di search view (DIFF-01, install-blocking, BARU untuk 18→19), (2) rename `groups_id`→`group_ids` di test fixture `res.users.create()` (DIFF-02, test-blocking). Satu open question (DIFF-10, xmlid `stock.picking_type_*`/`stock.stock_location_stock` di test) ditunda ke Step 9 G1 — TIDAK diubah sekarang kecuali eksekusi nyata membuktikan gagal. Bug/quirk source (`FINDINGS.md` MF-01..MF-04) dipertahankan identik, TIDAK diperbaiki.

## 2. Strategi per File/Simbol (ringkasan umum)

| File/simbol | Ref `DIFF-NNN` (02_DIFF_ANALYSIS §1) | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `views/stock_history_view.xml:10` — `<group expand="0" string="Group By">` (record `view_stock_history_search2`) | DIFF-01 | Hapus dua atribut `expand="0"` dan `string="Group By"`, biarkan `<group>` polos (isi `<filter>` di dalamnya tidak berubah) | Rendah — mekanis, sudah dikonfirmasi cukup hapus dua atribut | BSL-010 (view ini bagian dari search view, tidak ada BSL spesifik untuk group tag) |
| `tests/test_product_history_report.py:189` — `'groups_id': [(6, 0, [...])]` (create `res.users`, test `test_ac_05_01_...`) | DIFF-02 | Rename key `groups_id`→`group_ids`, value/tuple `(6, 0, [...])` tidak berubah | Rendah — mekanis, satu baris | BSL-007 (test ini memverifikasi ACL longgar yang harus dipertahankan) |
| `models/stock_history_view.py:24,26` — `self._cr` (2 titik: `tools.drop_view_if_exists(self._cr, ...)`, `self._cr.execute(query)`) | DIFF-03 | **Opsional** — boleh diganti `self.env.cr`, TIDAK wajib (masih berfungsi sebagai alias deprecated) | Sangat rendah | BSL-002 |
| `tests/test_product_history_report.py` — `_picking_type_for()` (`env.ref('stock.picking_type_internal'/'_in'/'_out')`), `setUpClass` (`env.ref('stock.stock_location_stock'/'_customers'/'_suppliers')`) | DIFF-10 | **Tidak diubah — dikonfirmasi aman via G1 run nyata**, semua `env.ref()` resolve normal | Tidak ada (resolved) | — (test-only, tidak ada BSL terkait) |
| `tests/test_product_history_report.py:65` — `_make_move()`, `self.env['stock.move'].create({'name': 'BACKFILL test move', ...})` | DIFF-15 (BARU, ditemukan G1) | **Wajib** — hapus key `'name': ...`, tidak perlu pengganti (field dihapus total, diganti compute `reference` yang tidak settable langsung) | Rendah — mekanis, satu baris, TAPI wajib (test-blocking untuk 4 test) | — (test-only, modul produksi tidak pernah pakai `stock_move.name`) |
| `static/tests/tours/stock_history_tour.js` — step trigger `.o_button_more` + `.o_dropdown_more button:contains("Stock History")` | DIFF-16 (BARU, ditemukan G1) | **Wajib** — hapus step klik `.o_button_more`, ubah trigger step berikutnya jadi `button:contains("Stock History")` langsung (tombol sudah tidak collapse ke overflow menu di 19.0) | Rendah — mekanis, TAPI wajib (Tour test gagal tanpa ini) | — (tour test-only, bukan perubahan UI produksi — tombol tetap sama, cuma tidak overflow) |
| `models/stock_history_view.py` — SQL mentah (`stock_move`/`stock_move_line`/`product_product`/`product_template`) | DIFF-04, DIFF-05 | Tidak ada perubahan — semua field & `tools.drop_view_if_exists` dikonfirmasi identik | Tidak ada | BSL-004, BSL-005, BSL-006 |
| `views/views.xml` — inherit `stock.product_template_form_view_procurement_button` | DIFF-08 | Tidak ada perubahan | Tidak ada | BSL-001, BSL-003 |
| `security/ir.model.access.csv` | DIFF-11 | Tidak ada perubahan | Tidak ada | BSL-007, BSL-008 |
| `models/*.py` — `from odoo.http import request` (tidak dipakai) | DIFF-13 | Opsional hapus (dead import) — TIDAK wajib | Tidak ada | BSL-011 |
| `__manifest__.py:17` — `'version': '18.0.1.0.0'` | DIFF-14 | Wajib ganti prefix versi jadi `'19.0.1.0.0'` | Tidak ada — konvensi baku Odoo | — |

## 2b. Risk Analysis Terstruktur (detail, per kategori)

### Critical Migration Blockers
*(Mencegah instalasi atau operasi inti di 19.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version — harus `19.0.x` | `__manifest__.py:17` (`'version': '18.0.1.0.0'`) | Konvensi baku Odoo |
| 2 | Atribut `expand`/`string` dihapus dari skema `<group>` — `ValidationError` saat install kalau tidak dihapus | `views/stock_history_view.xml:10` (record `view_stock_history_search2`) | `02_DIFF_ANALYSIS.md` DIFF-01 (BARU, belum ada di `knowledge/version-diffs/18-to-19.md` sebelum sesi ini) |

**Priority:** HIGH — perbaiki sebelum runtime testing apapun.

### Test-Blocking (kategori baru, terpisah dari install-blocking — pola dari project 17→18 `DIFF-12`)

| # | Isu | Lokasi | Rujukan |
|---|---|---|---|
| 1 | `res.users.groups_id`→`group_ids` — `create()` gagal di test | `tests/test_product_history_report.py:189` | `02_DIFF_ANALYSIS.md` DIFF-02 — **dikonfirmasi fix via G1 run #2** |
| 2 | `stock.move.name` dihapus — `create()` gagal di 4 test lewat `_make_move()` | `tests/test_product_history_report.py:65` | `02_DIFF_ANALYSIS.md` DIFF-15 (BARU, ditemukan G1 run #1) — **dikonfirmasi fix via G1 run #2** |
| 3 | Tour `.o_button_more` tidak render lagi — Tour test timeout | `static/tests/tours/stock_history_tour.js` | `02_DIFF_ANALYSIS.md` DIFF-16 (BARU, ditemukan G1 run #1) — **dikonfirmasi fix via G1 run #2** |

(Item "xmlid `stock.picking_type_*`" yang sebelumnya di sini sebagai open question DIFF-10 — **sudah RESOLVED via G1**, dikonfirmasi aman, dipindah ke bagian "Tidak berubah" §2.)

**Priority:** Semua HIGH — ketiganya genuinely membuat test gagal kalau tidak difix, sudah dikonfirmasi lewat eksekusi nyata (bukan diasumsikan).

### OWL Widget yang Butuh Rewrite/Review

N/A — modul tidak punya komponen Owl/JavaScript custom aplikatif (`01a_MIGRATION_INTAKE.md` §2b). Satu file test tour (`static/tests/tours/stock_history_tour.js`) — tidak berisi business logic produksi, TAPI trigger-nya perlu fix (DIFF-16 di atas) karena behavior overflow button box berubah di 19.0.

### Controller & Route

N/A — `controllers/controllers.py` murni boilerplate, tidak expose route.

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Tidak ada asset/JS/CSS aplikatif custom, tidak ada dependency yang berubah/hilang | `__manifest__.py` (`depends: ['base', 'stock']`) | N/A |

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref `BSL-NNN` |
|---|---|---|---|---|
| 1 | Tidak ada field/model yang berubah struktur — semua field SQL mentah dikonfirmasi stabil (DIFF-04) | `models/stock_history_view.py` | N/A | BSL-004..BSL-006 |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Tidak ada — modul tidak diintegrasikan modul custom lain, cuma extend `product.template` bawaan `stock` | — | N/A |

### Urutan Prioritas Testing

1. Install & startup — manifest version, fix `<group>` (blocker #1-2 di atas) HARUS lulus dulu sebelum lanjut
2. Core user flow — klik tombol "Stock History" di form produk, verifikasi window action graph/pivot/list terbuka dengan data benar
3. Test suite integration (`test_product_history_report.py`) — fix `group_ids` dulu, JALANKAN, baru putuskan soal DIFF-10 berdasarkan hasil nyata
4. Tour test (`test_stock_history_tour.py`) — verifikasi API `HttpCase.start_tour` tidak berubah di 19.0
5. Business rule spesifik: income/outcome (BSL-004, termasuk verifikasi bug double-count tetap ada — MF-02), multi-company filter (BSL-006), ACL terbuka (BSL-007 — MF-03)

### Estimasi Effort

| Area | Effort | Catatan |
|---|---|---|
| Fix `<group>` search view (DIFF-01) | Sangat kecil (< 15 menit) | Hapus 2 atribut, 1 titik — **selesai** |
| Fix `groups_id`→`group_ids` (DIFF-02) | Sangat kecil (< 15 menit) | 1 baris — **selesai** |
| Manifest version bump | Sangat kecil | 1 baris — **selesai** |
| Fix `stock.move.name` di test fixture (DIFF-15) | Sangat kecil (< 15 menit) | Hapus 1 key, tidak perlu pengganti — **selesai, ditemukan+fix di sesi G1 yang sama** |
| Fix Tour trigger `.o_button_more` (DIFF-16) | Sangat kecil (< 15 menit) | Hapus 1 step, ubah 1 trigger — **selesai, ditemukan+fix di sesi G1 yang sama** |
| DIFF-10 | Nol — dikonfirmasi aman via G1, tidak perlu fix | — |
| Sisanya (model/SQL/ACL/security) | Nol | Tidak ada perubahan kode diperlukan |

## 3. Data Migration (ringkas — detail di step 7)

N/A — port kode saja (`01a_MIGRATION_INTAKE.md` §3), tidak ada instance produksi dengan data lama. Step 7 di-skip.

## 4. Scope

### Termasuk
- Hapus atribut `expand`/`string` dari `<group>` di `views/stock_history_view.xml:10` (DIFF-01)
- Rename `groups_id`→`group_ids` di `tests/test_product_history_report.py:189` (DIFF-02)
- Bump `__manifest__.py` version ke `19.0.1.0.0` (DIFF-14)
- Hapus key `name` dari `stock.move.create()` di `_make_move()` (DIFF-15, ditemukan G1)
- Ubah trigger Tour `.o_button_more` → klik langsung `button:contains("Stock History")` (DIFF-16, ditemukan G1)
- Verifikasi instalasi bersih + test suite penuh (9/9) di Odoo 19.0 — **selesai, G1 run #2: 0 failed, 0 error(s) of 9 tests** (lihat `06c_IMPLEMENTATION_LOG.md`)

### Di Luar Scope (sengaja, disetujui di intake)
- 4 bug/quirk source (`MF-01`..`MF-04`) — TIDAK diperbaiki, dipertahankan identik
- `self._cr`→`self.env.cr` (DIFF-03) — opsional, TIDAK wajib untuk kompatibilitas
- Dead code (`action_stock_history_graph2`/`*_tree2` tidak terhubung menu, import `odoo.http.request` tidak terpakai) — boleh dibersihkan sebagai cleanup opsional, TIDAK wajib, TIDAK mengubah scope migrasi kalau tidak dibersihkan
