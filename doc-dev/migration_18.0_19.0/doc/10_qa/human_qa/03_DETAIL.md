# Detail Test — product_history_report

**Level:** Detail — varian/edge-case, boleh ditunda ke rilis berikutnya kalau disepakati eksplisit.
**Estimasi waktu:** ~6 menit.
**Sumber:** S-04, S-05, S-07 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. (Kalau instance multi-company) Login sebagai user dengan company aktif = Company A.
   Buka Stock History produk yang punya move di Company B juga — pastikan hanya move
   Company A yang terhitung. Kalau instance single-company, lewati langkah ini (sudah
   dikonfirmasi test otomatis Step 9).
2. Lakukan transfer stok internal->internal untuk suatu produk (dua lokasi sama-sama
   usage 'internal', mis. antar rak dalam warehouse yang sama).
3. Buka Stock History produk itu, cek bulan terjadinya transfer.
4. PENTING: pastikan kolom "Input" DAN "Output" SAMA-SAMA bertambah sejumlah qty
   transfer itu. Ini bug yang SENGAJA DIPERTAHANKAN sejak versi 17.0/18.0
   (FINDINGS.md MF-02) -- BUKAN kegagalan migrasi. Kalau ternyata cuma satu kolom
   yang bertambah (tidak double-count lagi), itu justru tanda regresi/perubahan
   behavior tak sengaja yang WAJIB dilaporkan ke dev.
5. Buka window "Stocks Histories" (S-01), klik ikon dropdown search options (panah
   kecil di sisi kanan search bar).
6. Cek filter "Group By" masih muncul: "By products", "Date", "Category", "UOM" --
   klik salah satu, pastikan hasil ter-group sesuai pilihan. Ini verifikasi bahwa
   penghapusan atribut dekoratif di search view (wajib untuk kompatibilitas 19.0)
   TIDAK menghilangkan fungsinya.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-26 | Odoo 19.0, docker (odoo:19.0 resmi) | AI (automated test: Integration Step 9 untuk langkah 1-4, Tour test extended untuk langkah 5-6) | Pass | `test_ac_04_01_...`/`test_ac_03_02_...` (langkah 1-4), `stock_history_tour` step 11-12 (langkah 5-6) |
