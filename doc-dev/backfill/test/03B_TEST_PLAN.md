# Test Plan — product_history_report

**Module:** `product_history_report`
**Ref:** `doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md`
**Taxonomy:** vocab Odoo intrinsik (`TransactionCase`/`HttpCase`/Tour) — `cicd/test_design/odoo-testing-taxonomy.md`
tidak di-connect ke sesi ini, tidak dijadikan blocker (lihat `doc-dev-backfill/ai-doc/PLAYBOOK.md` §0).
**Dibuat oleh:** BACKFILL (Step 03B, backfill)
**Last Updated:** 2026-08-07

---

## Step 04 — Developer Testing (backfill)

**Output:** `04A_DEV_TESTING.md`. Tidak ada API eksternal (modul tidak expose/consume API), jadi
`04B_API_TEST.md` **tidak dibuat**.

| AC | Deskripsi singkat | Unit | Integration | API |
|---|---|---|---|---|
| AC-01-01 | Tombol "Stock History" muncul di arch view produk | | ✓ (baca arch via `TransactionCase`) | |
| AC-01-02 | Klik tombol → action window graph/pivot/tree dgn domain benar | | ✓ (panggil `action_open_stock_history()` langsung) | |
| AC-02-01 | `qty` running-sum benar, termasuk saldo-awal dari histori >13 bulan | | ✓ (`TransactionCase`, buat stock.move sintetis lintas waktu) | |
| AC-02-02 | Race condition dua klik ber-dekatan, produk berbeda | | ⚠️ Tidak dites otomatis — lihat catatan di bawah | |
| AC-03-01 | Move customer→internal masuk `income` saja | | ✓ | |
| AC-03-02 | Move internal→internal masuk `income` DAN `outcome` | | ✓ | |
| AC-04-01 | Filter multi-company — move company lain tidak ikut terhitung | | ✓ | |
| AC-05-01 | `read` `stock.history.view` terbuka utk user internal tanpa grup khusus | | ✓ (`with_user()` user tanpa grup Inventory) | |
| AC-05-02 | `create`/`write`/`unlink` langsung ke `stock.history.view` gagal di level DB | | ✓ (assert raises) | |

**Ringkasan:** 0 AC → Unit murni (semua method di modul ini menyentuh `self.env`/ORM/SQL cursor,
jadi tidak ada kandidat Mode D stub pure-logic — lihat `PLAYBOOK.md` §Mode D), 8 AC → Integration,
1 AC (AC-02-02) tidak dites otomatis (concurrency, lihat catatan), API = N/A.

**Catatan AC-02-02 (race condition):** `TransactionCase` Odoo berjalan dalam SATU transaksi/cursor
per test, tidak cocok untuk mensimulasikan dua request HTTP konkuren yang benar-benar berebut
DROP/CREATE VIEW yang sama di connection terpisah. Tidak dipaksa dibuatkan test otomatis — dicatat
sebagai keterbatasan test coverage di `04A_DEV_TESTING.md` §3 dan tetap sebagai
`[PERLU-KEPUTUSAN]` terbuka di `FINDINGS.md` F-01 (butuh keputusan desain dari pemilik modul,
bukan cuma butuh test tambahan).

**Email:** N/A — modul tidak menyentuh outgoing/incoming email sama sekali (tidak ada composer,
`account.move.send`, `message_process()`, atau `fetchmail.server`).

---

## Step 07 — QA Testing (level AI-interaktif + Smoke human-confirmed, TANPA UAT)

| AC | Deskripsi singkat | AI-interaktif (07 §3) | AI-Browser/Tour (07B) |
|---|---|---|---|
| AC-01-01 | Tombol tampil di form produk | ✓ | ✓ (Tour: buka form produk, assert tombol ada) |
| AC-01-02 | Klik tombol membuka window action yang benar | ✓ | ✓ (Tour: klik tombol, assert breadcrumb/judul "Stocks Histories") |
| AC-02-01 | Angka qty/income/outcome masuk akal di pivot/graph | ✓ | |
| AC-04-01 | Ganti company aktif, angka berubah sesuai | ✓ | |
| AC-05-01 | Login user non-Inventory bisa lihat data (ACL longgar) | ✓ | |

**Ringkasan:** BACKFILL pakai AI-interaktif (`07_QA_TESTING.md` §3) sebagai default untuk semua 8
AC. Tour headless (Mode E, `07B_QA_AI_BROWSER.md`) ditambahkan KHUSUS untuk AC-01-01/AC-01-02 —
satu-satunya interaksi UI nyata di modul ini (klik tombol statistik) — bukan kebutuhan wajib untuk
AC lain yang sifatnya lebih ke "angka di laporan benar", yang lebih efektif diverifikasi lewat
Integration test (Step 04) dan pembacaan pivot/graph langsung. **Skenario "hanya satu
dialog/wizard disentuh" (checklist wajib Step 07) TIDAK RELEVAN** — modul ini tidak pernah memicu
lebih dari satu dialog/wizard dari satu aksi (tombol langsung membuka satu action window, bukan
dialog bertumpuk).

---

## Ringkasan Keseluruhan

| Step | Tipe | Jumlah AC |
|---|---|---|
| 04 | Unit | 0 |
| 04 | Integration | 8 |
| 04 | Tidak dites otomatis (concurrency) | 1 (AC-02-02) |
| 04 | API (kondisional) | N/A |
| 07 | AI-interaktif (`07` §3) | 5 |
| 07 | AI-Browser/Tour (`07B`) | 2 (subset, AC-01-01/01-02) |
