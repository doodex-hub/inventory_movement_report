# Smoke Test — product_history_report

**Level:** Smoke — kalau ini gagal: STOP, jangan lanjut deploy/testing lain, balik ke Step 9 atau eskalasi ke dev.
**Estimasi waktu:** ~2 menit.
**Sumber:** S-01 di `../10_BUSINESS_FLOW_MIGRATION.md` — sudah PASS lewat Tour test otomatis (`static/tests/tours/stock_history_tour.js`). Checklist ini tetap disediakan untuk re-verifikasi manual kapan saja (deploy/hotfix), bukan berarti wajib diulang.

```
1. Login ke Odoo 19.0 (admin/admin di instance QA, atau kredensial dev di instance lain).
2. Buka app Inventory → Products → pilih produk apapun.
3. Di form produk, cari tombol statistik "Stock History" (icon sinyal) — tampil LANGSUNG
   di button box (tidak perlu klik "More" lagi seperti di 18.0).
4. Klik tombol tersebut.
5. Pastikan window baru terbuka dengan judul "Stocks Histories", TIDAK ada error
   "Invalid view type" atau layar putih/error lainnya.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Odoo 19.0, docker (odoo:19.0 resmi) | AI (Tour test otomatis, bukan klik manual) | Pass | `stock_history_tour`, 12/12 step, log `tour succeeded` |
