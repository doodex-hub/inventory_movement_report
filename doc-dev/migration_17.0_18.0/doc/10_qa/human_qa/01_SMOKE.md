# Smoke Test — product_history_report

**Level:** Smoke — kalau ini gagal: STOP, jangan lanjut deploy/testing lain, balik ke Step 9 atau eskalasi ke dev.
**Estimasi waktu:** ~2 menit.
**Sumber:** S-01 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. Login ke Odoo 18.0 (admin/admin di instance QA, atau kredensial dev di instance lain).
2. Buka app Inventory → Products → pilih produk apapun.
3. Di form produk, cari tombol statistik "Stock History" (icon sinyal), tepat setelah tombol
   "Stock Moves" bawaan.
4. Klik tombol tersebut.
5. Pastikan window baru terbuka dengan judul "Stocks Histories", TIDAK ada error
   "Invalid view type" atau layar putih/error lainnya.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| | | | | |
