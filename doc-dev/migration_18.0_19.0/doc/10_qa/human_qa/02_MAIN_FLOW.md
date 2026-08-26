# Main Flow Test — product_history_report

**Level:** Main Flow — flow bisnis inti sehari-hari.
**Estimasi waktu:** ~5 menit.
**Sumber:** S-02, S-03 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. Buka Stock History untuk produk dengan minimal satu stock move dari lokasi
   Customer/Supplier ke lokasi Internal (state Done).
2. Switch ke view pivot atau list, cari bulan terjadinya move itu.
3. Cek kolom "Input" bertambah sesuai qty move, kolom "Output" TIDAK bertambah untuk
   move ini (kecuali produk itu juga punya transfer internal terpisah, itu kasus lain).
4. Bandingkan kolom "Stock Quantity uom" (qty) baris PERTAMA jendela dengan quantity
   on-hand aktual produk (menu Inventory Reporting atau field on-hand di form produk).
5. Pastikan qty baris pertama TIDAK mulai dari 0 kalau produk punya histori lebih dari
   12 bulan — harus sudah mencakup saldo pembuka.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Odoo 19.0, docker (odoo:19.0 resmi) | AI (automated test, bukan klik manual) | Pass | `test_ac_02_01_...`, `test_ac_03_01_...` |
