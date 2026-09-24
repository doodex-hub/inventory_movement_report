# Detail Test — product_history_report (Odoo 20.0)

**Level:** Detail — varian/edge-case.
**Estimasi waktu:** ~10 menit.
**Sumber:** S-05, S-06, S-07, S-08, S-12 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Ikon tombol

```
1. Buka form produk, temukan tombol "Stock History" (langsung atau di dalam "More").
2. Pastikan ikonnya berupa bar sinyal bertingkat — BUKAN kotak kosong atau teks seperti "fa-signal"/"android_cell_5_bar".
```

## Filter Group By

```
1. Buka laporan Stock History, klik panah dropdown di kotak pencarian.
2. Di bagian Group By pastikan ada: By products, Date, Category, UOM.
3. Klik "By products": data terkelompok per produk, jumlah baris tetap sama.
```

## Transfer internal dihitung dua kali (perilaku lama, sengaja dipertahankan)

```
1. Buat & validasi transfer internal (dari satu lokasi internal ke lokasi internal lain) untuk produk, misal 4 unit.
2. Buka laporan Stock History produk itu.
3. Di baris bulan berjalan, 4 unit itu muncul di Input DAN di Output (saldo tidak berubah).
   Ini perilaku yang sama dengan versi 19.0 — BUKAN bug baru.
```

## Multi-company

```
1. Di instance multi-company, pilih hanya Company A di pemilih company.
2. Buka laporan produk yang punya pergerakan di Company A dan Company B.
3. Pastikan hanya pergerakan Company A yang dihitung.
```

## Posisi tombol di Enterprise

```
1. Di instance Enterprise (mis. dengan Quality terpasang), buka form produk.
2. Tombol "Stock History" boleh berada di dropdown "More" — itu sama seperti versi 19.0 Enterprise.
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker QA 19.0 vs 20.0 Enterprise + test otomatis | AI (Playwright MCP + Integration/Tour) | Pass | Ikon setara 19.0; Group By 4 filter; double-count identik; More identik |
