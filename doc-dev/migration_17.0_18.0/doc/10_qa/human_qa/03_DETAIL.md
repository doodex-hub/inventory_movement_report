# Detail Test — product_history_report

**Level:** Detail — varian/edge-case, boleh ditunda ke rilis berikutnya kalau disepakati eksplisit.
**Estimasi waktu:** ~5 menit.
**Sumber:** S-04, S-05 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. (Kalau instance multi-company) Login sebagai user dengan company aktif = Company A.
   Buka Stock History produk yang punya move di Company B juga — pastikan hanya move
   Company A yang terhitung. Kalau instance single-company, lewati langkah ini (sudah
   dikonfirmasi test otomatis Step 9).
2. Lakukan transfer stok internal->internal untuk suatu produk (dua lokasi sama-sama
   usage 'internal', mis. antar rak dalam warehouse yang sama).
3. Buka Stock History produk itu, cek bulan terjadinya transfer.
4. PENTING: pastikan kolom "Input" DAN "Output" SAMA-SAMA bertambah sejumlah qty
   transfer itu. Ini bug yang SENGAJA DIPERTAHANKAN dari versi 17.0 (FINDINGS.md MF-02)
   — BUKAN kegagalan migrasi. Kalau ternyata cuma satu kolom yang bertambah (tidak
   double-count lagi), itu justru tanda regresi/perubahan behavior tak sengaja yang
   WAJIB dilaporkan ke dev.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| | | | | |
