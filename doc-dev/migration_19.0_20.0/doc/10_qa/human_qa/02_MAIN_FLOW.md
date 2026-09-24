# Main Flow Test — product_history_report (Odoo 20.0)

**Level:** Main Flow — flow bisnis inti.
**Estimasi waktu:** ~10 menit.
**Sumber:** S-03, S-04 di `../10_BUSINESS_FLOW_MIGRATION.md`.
**Persiapan:** satu produk dengan pergerakan stok di beberapa bulan berbeda, termasuk minimal satu pergerakan lebih dari 13 bulan lalu (saldo awal).

## Angka laporan per bulan

```
1. Buka laporan Stock History produk tersebut (lihat 01_SMOKE.md).
2. Klik ikon List (paling kanan di pojok kanan atas).
3. Pastikan ada satu baris per akhir bulan untuk 12 bulan terakhir + bulan berjalan (13 baris).
4. Untuk tiap baris, cek:
   - Input  = jumlah barang masuk ke lokasi internal di bulan itu
   - Output = jumlah barang keluar dari lokasi internal di bulan itu
   - Stock Quantity uom = saldo kumulatif (termasuk saldo dari sebelum 12 bulan terakhir)
5. Baris terakhir (bulan berjalan) harus sama dengan stok On Hand produk.
```

## Tiga tampilan laporan

```
1. Klik ikon Graph: grafik batang per bulan, tinggi batang = saldo kumulatif.
2. Klik ikon Pivot: kolom per bulan, masing-masing berisi Input, Output, Stock Quantity UOM.
3. Angka di Pivot dan List harus sama untuk bulan yang sama.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker QA 19.0 (8094) vs 20.0 (8093), data identik | AI (Playwright MCP + skrip seed) | Pass | 13 baris List identik 19.0↔20.0; saldo akhir 137 = On Hand |
