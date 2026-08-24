# Migration Spec (Teknis) — product_history_report

**Step:** 3 — Migration Spec
**Versi:** 17.0 → 18.0
**Ref:** `02_diff/02_DIFF_ANALYSIS.md`
**Tanggal:** 2026-08-24

---

## 1. Ringkasan Strategi

Modul kecil, murni backend (1 model extend + 1 SQL view + 2 file view XML + 1 baris ACL, tidak ada JS/Owl/controller aktif). **Hampir seluruhnya port langsung 1:1** — satu-satunya perubahan wajib adalah sintaks view `<tree>`→`<list>` (3 titik, lihat §2b "View List Checklist"). Tidak ada rewrite logic, tidak ada perubahan field/model, tidak ada dependency yang hilang. Bug/quirk source (`FINDINGS.md` MF-01..MF-04) dipertahankan identik, TIDAK diperbaiki.

## 2. Strategi per File/Simbol (ringkasan umum)

| File/simbol | Ref `DIFF-NNN` (02_DIFF_ANALYSIS §1) | Strategi migrasi | Risiko | Ref `BSL-NNN` |
|---|---|---|---|---|
| `views/stock_history_view.xml` — record `stock_history_tree_view2` | DIFF-01 | Ganti tag `<tree string="stock history">`→`<list string="stock history">` (dan penutup `</tree>`→`</list>`), field-field di dalamnya tidak berubah | Rendah — mekanis, sudah dikonfirmasi cukup rename tag | BSL-001 |
| `views/stock_history_view.xml` — `action_stock_history_graph2` (`view_mode="graph,tree,pivot"`), `action_stock_history_tree2` (`view_mode="tree,pivot,graph"`) | DIFF-02 | Ganti token `tree`→`list` di kedua `view_mode` | Rendah — mekanis | — (dead code, `BSL-010`) |
| `models/product_template.py` — `action_open_stock_history()` return dict `'view_mode': 'graph,pivot,tree'` | DIFF-02 | Ganti token `tree`→`list` | Rendah — mekanis | BSL-001, BSL-002 |
| `models/product_template.py` — `'view_type': 'form'` key | DIFF-03 | Opsional hapus (dead key, tidak dipakai native manapun) — TIDAK wajib untuk kompatibilitas | Sangat rendah | — |
| `models/stock_history_view.py` — SQL mentah (`stock_move`/`stock_move_line`/`product_product`/`product_template`) | DIFF-05, DIFF-06 | Tidak ada perubahan — semua field & `tools.drop_view_if_exists` dikonfirmasi identik | Tidak ada | BSL-004, BSL-005, BSL-006 |
| `views/views.xml` — inherit `stock.product_template_form_view_procurement_button` | DIFF-04 | Tidak ada perubahan | Tidak ada | BSL-001, BSL-003 |
| `security/ir.model.access.csv` | DIFF-08 | Tidak ada perubahan | Tidak ada | BSL-007, BSL-008 |
| `models/*.py` — `from odoo.http import request` (tidak dipakai) | DIFF-11 | Opsional hapus (dead import) — TIDAK wajib | Tidak ada | BSL-011 |
| `tests/test_product_history_report.py:103` — `self.assertEqual(action['view_mode'], 'graph,pivot,tree')` | DIFF-02 (turunan) | **Wajib update** string assertion jadi `'graph,pivot,list'`, konsisten dengan perubahan `product_template.py` — kalau tidak diupdate, test ini akan FAIL bukan karena bug migrasi tapi karena test-nya sendiri belum disinkronkan | Rendah — mekanis, satu baris | AC-01-02 (`doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md`) |
| `__manifest__.py` — `'version': '17.0.1.0.0'` | — (tidak ada baris `02_DIFF_ANALYSIS` khusus, tapi wajib untuk kompatibilitas platform) | Wajib ganti prefix versi jadi `'18.0.1.0.0'` | Tidak ada — konvensi baku Odoo | — |

## 2b. Risk Analysis Terstruktur (detail, per kategori)

### Critical Migration Blockers
*(Mencegah instalasi atau operasi inti di 18.0)*

| # | Isu | Lokasi | Rujukan knowledge base |
|---|---|---|---|
| 1 | Manifest version — harus `18.0.x` | `__manifest__.py:18` (`'version': '17.0.1.0.0'`) | `knowledge/version-diffs/17-to-18.md` (konvensi baku) |
| 2 | `<tree>` view type dihapus — `ParseError` saat install kalau tidak diganti `<list>` | `views/stock_history_view.xml:51` (`stock_history_tree_view2`) | `knowledge/version-diffs/17-to-18.md` §1 (`odoo/odoo#159909`), `02_DIFF_ANALYSIS.md` DIFF-01 |
| 3 | Token `view_mode="...,tree,..."` — window action gagal resolve view kalau tidak diganti `list` | `views/stock_history_view.xml:66,73`, `models/product_template.py:29` | `02_DIFF_ANALYSIS.md` DIFF-02 |

**Priority:** HIGH — perbaiki sebelum runtime testing apapun (ini SATU-SATUNYA kategori blocker untuk modul ini).

### OWL Widget yang Butuh Rewrite/Review

N/A — modul tidak punya komponen Owl/JavaScript custom (`01a_MIGRATION_INTAKE.md` §2b).

### Controller & Route

N/A — `controllers/controllers.py` murni boilerplate, tidak expose route (`01a_MIGRATION_INTAKE.md` §2b, DIFF-10).

### Assets & Dependency

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Tidak ada asset/JS/CSS custom, tidak ada dependency yang berubah/hilang | `__manifest__.py` (`depends: ['base', 'stock']`) | N/A |

### Kompatibilitas Data Model

| # | Isu | Lokasi | Priority | Ref `BSL-NNN` |
|---|---|---|---|---|
| 1 | Tidak ada field/model yang berubah struktur — semua field SQL mentah dikonfirmasi stabil (DIFF-05) | `models/stock_history_view.py` | N/A | BSL-004..BSL-006 |

### Risiko Integrasi

| # | Isu | Lokasi | Priority |
|---|---|---|---|
| 1 | Tidak ada — modul tidak diintegrasikan modul custom lain, cuma extend `product.template` bawaan `stock` | — | N/A |

### Urutan Prioritas Testing

1. Install & startup — manifest version, `<list>` view (blocker #1-3 di atas) HARUS lulus dulu sebelum lanjut
2. Core user flow — klik tombol "Stock History" di form produk, verifikasi window action graph/pivot/list terbuka dengan data benar (AC-01, AC-02 lama)
3. Persistensi data — N/A (modul tidak menulis data, `_auto=False` SQL view read-only secara praktis)
4. Widget backend (Owl) — N/A
5. Business rule spesifik: income/outcome (BR-03/BSL-004, termasuk verifikasi bug double-count tetap ada — MF-02), multi-company filter (BR-05/BSL-006), ACL terbuka (BR-06/BSL-007 — MF-03)

### View List (dulu Tree) Checklist

| # | Apa | Di mana | Perubahan |
|---|---|---|---|
| 1 | Standalone list view | `views/stock_history_view.xml:47-61` (`stock_history_tree_view2`) | `<tree string="stock history">` → `<list string="stock history">`, tutup `</tree>`→`</list>` |
| 2 | `view_mode` di action (XML) | `views/stock_history_view.xml:66` (`action_stock_history_graph2`), `:73` (`action_stock_history_tree2`) | `graph,tree,pivot` → `graph,list,pivot`; `tree,pivot,graph` → `list,pivot,graph` |
| 3 | `view_mode` di action (Python dict) | `models/product_template.py:29` | `'graph,pivot,tree'` → `'graph,pivot,list'` |
| 4 | Inline tree di form | Tidak ada — tidak ditemukan `<tree>` inline di dalam `<field>` manapun | N/A |
| 5 | Test assertion string `view_mode` | `tests/test_product_history_report.py:103` | `'graph,pivot,tree'` → `'graph,pivot,list'` |

### Estimasi Effort

| Area | Effort | Catatan |
|---|---|---|
| View migration (`<tree>`→`<list>`, 3 titik) | Sangat kecil (< 30 menit) | Mekanis, sudah terpetakan lengkap di atas |
| Manifest version bump | Sangat kecil | 1 baris |
| Sisanya (model/SQL/ACL/security) | Nol | Tidak ada perubahan kode diperlukan |

## 3. Data Migration (ringkas — detail di step 7)

N/A — port kode saja (`01a_MIGRATION_INTAKE.md` §3), tidak ada instance produksi dengan data lama. Step 7 di-skip.

## 4. Scope

### Termasuk
- Ganti `<tree>`→`<list>` (3 titik, lihat checklist di atas)
- Bump `__manifest__.py` version ke `18.0.1.0.0`
- Verifikasi instalasi bersih di Odoo 18.0

### Di Luar Scope (sengaja, disetujui di intake)
- 4 bug/quirk source (`MF-01`..`MF-04`) — TIDAK diperbaiki, dipertahankan identik
- Dead code (`action_stock_history_graph2`/`*_tree2` tidak terhubung menu, import `odoo.http.request` tidak terpakai, key `view_type` dead) — boleh dibersihkan sebagai cleanup opsional, TIDAK wajib untuk kompatibilitas, TIDAK mengubah scope migrasi kalau tidak dibersihkan
