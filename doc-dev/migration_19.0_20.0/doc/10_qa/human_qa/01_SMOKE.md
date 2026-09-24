# Smoke Test — product_history_report (Odoo 20.0)

**Level:** Smoke — flow paling kritis. Kalau salah satu langkah gagal: STOP, jangan lanjut deploy/testing lain, balik ke tim dev.
**Estimasi waktu:** ~5 menit.
**Sumber:** S-01, S-02 di `../10_BUSINESS_FLOW_MIGRATION.md`.
**Persiapan:** user dengan hak Inventory (mis. admin); minimal satu produk yang sudah punya pergerakan stok (penerimaan/pengiriman yang sudah divalidasi).

## Modul terpasang

```
1. Buka Apps, cari "Product History Report".
2. Pastikan statusnya Installed (versi 20.0.1.0.0) — tidak ada pesan error saat instalasi/upgrade.
```

## Buka laporan Stock History

```
1. Buka Inventory > Products > Products, klik satu produk.
2. Di deretan tombol di bagian atas form, cari tombol "Stock History" (ikon bar sinyal).
   - Kalau tidak terlihat langsung, klik tombol "More" — di instance Enterprise tombol ini biasanya ada di sana.
3. Klik "Stock History".
4. Pastikan halaman berganti (bukan popup) dengan judul "Stocks Histories" di breadcrumb.
5. Pastikan yang tampil pertama adalah grafik batang (Graph).
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker QA 20.0 Enterprise (port 8093) + tour Community | AI (Playwright MCP + Tour test) | Pass | Tombol di dropdown More (Enterprise), graph tampil |
