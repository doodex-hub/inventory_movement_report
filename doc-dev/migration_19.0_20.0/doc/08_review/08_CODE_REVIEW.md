# Code Review — product_history_report

**Step:** 8 — Code Review (gate)
**Ref:** `03_spec/03_MIGRATION_SPEC.md`, `05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md`, `06_implementation/06c_IMPLEMENTATION_LOG.md`, `01_intake/01b_BASELINE_SPEC.md`
**Odoo Version:** 20.0
**Diff direview:** `migration/19.0` (`f57dee4`) → `migration/20.0` (`64152a6`), `product_history_report/` — 9 file kode/test/doc (+59 file aset `static/description/`, identik branch `19.0`, tidak direview sebagai kode). Framework dibaca di `odoo20` HEAD `b0329e93ae8`, `enterprise20` HEAD `bbccc6bce1`.
**Files reviewed:** `__manifest__.py`, `security/ir.access.csv` (+ hapus `ir.model.access.csv`), `views/views.xml`, `tests/test_product_history_report.py`, `tests/test_stock_history_tour.py`, `static/tests/tours/stock_history_form_tour.js`, `README.md`, `LISEZMOI.md`; konteks tak berubah: `models/*.py`, `views/stock_history_view.xml`.
**Tanggal:** 2026-09-24
**Status:** ✔️ Lulus gate (0 🔴 akibat migrasi; 1 🔴 WARISAN dieskalasi — lihat §G)

---

## A. Issues

**Status skill `odoo-review`:**
- [x] Terinstall (`.claude/skills/odoo-review`, `odoo-guidelines`, `odoo-security`, `odoo-web-guidelines`) & sudah dijalankan — pemetaan file → section, dua pass (rules + merits), sweep pola `odoo-security`.

| ID | Severity | Kategori | File | Baris | Issue | Rekomendasi |
|---|---|---|---|---|---|---|
| CR-01 | 🔴 **WARISAN** (bukan akibat migrasi) | Security | `models/stock_history_view.py` | 24-110 | `recreate_view(product_template_id, companies)` adalah method **publik** (tanpa `_`, tanpa `@api.private`) → callable lewat `/web/dataset/call_kw` (`auth="user"`, `odoo20/addons/web/controllers/dataset.py:28`; `get_public_method` hanya memblokir `_`/`@api.private`, `odoo20/odoo/orm/models.py:199-223`). Kedua argumen diinterpolasi f-string langsung ke SQL `CREATE VIEW` yang dieksekusi `self._cr.execute(query)` tanpa parameter. **Risiko:** user login mana pun (internal, bahkan portal) dapat memanggil method ini lewat RPC dengan argumen non-integer yang ikut menjadi bagian teks SQL → SQL di luar maksud modul dapat dieksekusi dengan hak DB Odoo. Identik di 17.0/18.0/19.0 (kode byte-identik). Section: `odoo-security` "Use the ORM; parameterize SQL" + "Default to private methods". | **TIDAK difix di migrasi** (CLAUDE.md: dilarang memperbaiki bug 19.0 tanpa persetujuan). Dieskalasi → `FINDINGS.md` MF-10. Fix minimal yang disarankan (menunggu keputusan dev): rename ke `_recreate_view` atau `@api.private` + `int()`/`','.join(str(int(c)) ...)` sebelum interpolasi (atau `SQL(...)` berparameter). Berbasis analisis kode statis; probe eksploitasi sengaja tidak dijalankan. |
| CR-02 | 🟡 | Security / Access rights | `security/ir.access.csv` | 2 | `crud` ke `base.group_everyone` (termasuk portal/public) — guideline eksplisit "flag any c/u/d granted to base.group_everyone". | **Dipertahankan by design** — padanan persis ACL 19.0 tanpa grup (MF-03, BSL-007), identik output skrip resmi `19.4-00-ir-access`. c/u/d praktis gagal di level DB (VIEW Postgres, BSL-008/AC-05-02). Pengetatan = keputusan pemilik modul (MF-03). |
| CR-03 | 🔵 | Manifest | `__manifest__.py` | 20 | `depends` mencantumkan `base` (guideline: jangan). | Warisan, tidak diubah (diff minimal). |
| CR-04 | 🔵 | Naming / ORM | `models/product_template.py` | 17 | Object action `action_open_stock_history` tanpa `self.ensure_one()` (guideline Naming). | Warisan BSL-003, dipertahankan. |
| CR-05 | 🔵 | Code quality | `__manifest__.py` | 28-31 | Indentasi item `images` 7 spasi (disalin persis dari branch rilis `19.0`, commit `9b88ff8`). | Kosmetik, dibiarkan identik dengan branch rilis. |
| CR-06 | 🔵 | Tests | `tests/*.py` | — | Test tidak memakai `BaseCommon` (guideline Tests untuk business test baru). | Test baru mengikuti gaya file yang ada (`TransactionCase`) — konsisten dengan test warisan; tidak bergantung demo data. |

Business Logic (manual): tidak ada perubahan logika — `models/` 0 baris diff terhadap 19.0. Edge case recordset kosong/multi-record tetap seperti 19.0 (BSL-003).

## B. Gap Analysis — Implementasi vs Migration Spec

| Spec item | Implementasi | Status | Catatan |
|---|---|---|---|
| DIFF-01 ACL | `security/ir.access.csv` 1 baris `base.group_everyone`, `crud`; manifest `data[0]` | ✅ | Identik output skrip resmi (`06c` A3) |
| DIFF-02 ikon | `views/views.xml:13` `icon="android_cell_5_bar"` | ✅ | |
| DIFF-03 test uom | `'uom_id'` di `_make_move` | ✅ | |
| DIFF-04 versi | `20.0.1.0.0` | ✅ | |
| DIFF-05..10 tidak berubah | `models/`, `controllers/`, `stock_history_view.xml` 0 diff | ✅ | |
| DIFF-11/12 tour | tour lama tak diubah; skip hanya bila `web_enterprise`; tour form baru | ✅ | |
| SCOPE-01 aset | `static/description` = branch `19.0` (0 diff), `images` | ✅ | |
| A6 README | README/LISEZMOI modul "20.0" | ✅ | Tercatat di spec (koreksi Step 6) |
| Test baru (spec §2) | 3 Integration + 1 Tour | ✅ | |

## C. Gap Analysis — Implementasi vs Acceptance Criteria

| AC ID | Behavior | Status | Jejak Nalar (Desk Review) | Catatan |
|---|---|---|---|---|
| AC-01-01 | Tombol di form setelah In/Out | ✅ Match | Form produk → view `stock.product_template_form_view_procurement_button` (`odoo20/addons/stock/views/product_views.xml:423`) → `<button name="action_view_stock_move_lines">` (masih ada, di `<t groups="stock.group_stock_user">`) → `views.xml` `position="after"` sisip tombol → tampil setelahnya untuk user Inventory | G2: `test_ac_01_01` PASS |
| AC-01-02 | Action dict | ✅ Match | klik → `action_open_stock_history()` (tak berubah) → dict `graph,pivot,list`, domain ids | G2 PASS |
| AC-01-03 | Navigasi Community + group-by | ✅ Match | tour 12 step, selector 19.0 semua valid di 20.0 | G2 tour 12/12 |
| AC-01-04 | Ikon Material | ✅ Match | arch `icon` → `ViewButton.iconFromString` → `<i class="o_button_icon oi" data-icon="android_cell_5_bar">` → ligature font subset (`icons_wishlist.txt:17`) → ikon bar sinyal | G2 arch test + tour step 1 |
| AC-01-05 | Form → graph, kedua edisi | ✅ Match (Community); Enterprise di Step 9 | `/odoo/action-.../<id>` → form → klik → action → view pertama graph | G2 tour 4/4 |
| AC-02-01, 03-01, 03-02, 04-01 | Nilai laporan | ✅ Match | SQL `recreate_view` byte-identik; kolom yang dibaca stabil (DIFF-05) | G2 PASS |
| AC-02-02 | Race condition tetap | ✅ Match | code identity (0 diff) | — |
| AC-05-01 | Read internal tanpa grup stock | ✅ Match | user `base.group_user` → `base.group_everyone` di-imply `group_user` (`base_groups.xml:94`) → permission `r` | G2 PASS |
| AC-05-02 | Create gagal di DB | ✅ Match | ACL izinkan `c` → INSERT ke VIEW → Postgres menolak | G2 PASS |
| AC-05-03 | Record `ir.access` | ✅ Match | CSV → `ir.access` xmlid sama, `kind=permission` | G2 PASS |
| AC-05-04 | Read portal | ✅ Match | portal → implied `group_everyone` → `r` | G2 PASS; baseline 19.0 dicek Step 9 |
| AC-06-01 | Enterprise | ⏳ Step 9 | analisis statis Step 2: tidak ada tabrakan | Run E |

## D. Cek Khusus Migrasi — P1 Fidelity

- [x] Tidak ada perubahan behavior yang tidak disengaja — semua deviasi dari `migration/19.0` tercatat & disetujui: DIFF-01..04 (wajib kompatibilitas), SCOPE-01 (disetujui dev), A6 README (housekeeping wajib `06a`), test tambahan.

**Empat arah tabrakan:**
- Arah 1 (method core ditimpa): modul hanya mendefinisikan `action_open_stock_history` di `product.template` — tidak ada method core bernama sama di `odoo20`/`enterprise20` (0 match, Step 2 §0e).
- Arah 2 (definisi baru core di target bernama sama): `action_open_stock_history`, model `stock.history.view`, tabel `stock_history_view` — 0 match di `odoo20` + `enterprise20`.
- Arah 3 (replace-total registry UI): N/A — tidak ada JS aplikatif.
- Arah 4 (action baru tumpang-tindih kapabilitas baru native): tombol "Stock History" di form produk — `odoo20`/`enterprise20` tidak menambah laporan riwayat stok bulanan per produk di form yang sama (stat button native tetap On Hand/Forecasted/In-Out/Rules/Lot/Putaway; `quality_control` menambah Quality Points/Checks). Tidak ada tumpang-tindih.
- [x] Sudah dicek (keempat arah) — tidak ada tabrakan/penyimpangan/tumpang-tindih.

## E. Perubahan Tak Tertelusuri

- [x] Tidak ada — `git diff --stat migration/19.0 migration/20.0 -- product_history_report ':!static/description'` = 9 file, semuanya ada di §B.

## F. Kontribusi ke Knowledge Base

- [x] Ada — `migration-records/product_history_report_19.0_20.0/SUMMARY.md`: pola "method publik model + SQL f-string = RPC SQL injection" sebagai item checklist review migrasi (Step 8 wajib sweep `odoo-security`, jangan terima klaim "nilai bukan input user" untuk method publik).

## G. Verdict

- Ringkasan Issues: 1 🔴 (WARISAN, bukan akibat migrasi — CR-01) · 1 🟡 (by design, CR-02) · 4 🔵
- [x] ✅ Lulus — tidak ada 🔴 yang DIPERKENALKAN migrasi; lanjut ke step 9.
- [ ] ❌ Ditolak

**Catatan gate:** CR-01 adalah kerentanan yang sudah ada sejak 17.0 dan byte-identik di 19.0. Memperbaikinya = perubahan kode di luar kompatibilitas 20.0, yang menurut CLAUDE.md butuh persetujuan eksplisit pemilik modul. Karena itu CR-01 tidak memblokir gate migrasi, tapi **WAJIB dieskalasi** ke dev (MF-10, prioritas Kritis) dan dilaporkan di ringkasan akhir sesi. Kalau dev menyetujui fix, itu dikerjakan sebagai perubahan disengaja tercatat (intake §5) + test regresi.

---

## H. Addendum re-review pasca Step 9 — SCOPE-02 (fix MF-10) & SCOPE-03 (2026-09-24)

Diff yang direview (satu-satunya perubahan `models/` di migrasi ini):
```
+    @api.private
     def recreate_view(self, product_template_id, companies):
+        # Security fix 20.0 (FINDINGS.md MF-10): ...
+        product_template_id = int(product_template_id)
+        companies = ','.join(str(int(company_id)) for company_id in str(companies).split(','))
```

| Cek | Hasil |
|---|---|
| RPC ditutup | `@api.private` → `get_public_method` raise `AccessError` (`odoo20/odoo/orm/models.py:219-223`); dibuktikan `test_ac_07_01`. Pemanggil satu-satunya (`product_template.action_open_stock_history`, server-side) tidak terpengaruh. Tidak ada override `recreate_view` di `odoo20`/`enterprise20` (Step 2 §0e). |
| Input ke teks SQL | Hanya digit + koma yang bisa lolos casting → teks SQL tidak bisa berisi apapun selain id. Dibuktikan `test_ac_07_02`. |
| Behavior input sah | Nilai hasil casting untuk `self.id` / `','.join(map(str, env.companies.ids))` identik dengan input asli → teks SQL byte-identik → AC-02..AC-05 tetap PASS (Run C 15/15, Run E 14+1 skip). |
| Edge case | `companies` berspasi (`"1, 2"`) tetap diterima (`int(" 2")`); string kosong → `ValueError` (di 19.0 juga gagal, di SQL). Multi-record `self` tidak dipakai method ini. |
| Guideline | `odoo-security` "Default to private methods" (sanctioned fix `@api.private` bila rename memecah pemanggil) terpenuhi. "Parameterize SQL": interpolasi masih f-string, tapi hanya untuk integer tervalidasi — rewrite ke `SQL()` berparameter sengaja tidak dilakukan (diff minimal, P3). 🔵 info. |
| SCOPE-03 | `index.html`: 18 baris, hanya penanda versi modul ini + jumlah test; link `/apps/modules/19.0/...` modul lain utuh. README/LISEZMOI root 1 baris masing-masing. |

**Status CR-01:** ✅ RESOLVED di 20.0 (perubahan disengaja disetujui dev). 17.0/18.0/19.0 tetap rentan (keputusan dev). **Verdict tetap ✅ Lulus** — 0 🔴 terbuka.
