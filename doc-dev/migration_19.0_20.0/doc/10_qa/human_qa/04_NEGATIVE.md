# Negative Test — product_history_report (Odoo 20.0)

**Level:** Negative — guard/keamanan. Jalankan minimal sekali sebelum rilis besar.
**Estimasi waktu:** ~10 menit (sebagian butuh developer mode / akses teknis).
**Sumber:** S-09, S-10, S-11 di `../10_BUSINESS_FLOW_MIGRATION.md`.

## Akses baca terbuka untuk semua user (perilaku lama, sengaja dipertahankan)

```
1. Login sebagai user internal TANPA hak Inventory.
2. Buka laporan (via URL action stock.history.view atau developer mode).
3. Data laporan tetap bisa dibaca — sama seperti 19.0. (Pengetatan akses = keputusan terpisah, lihat FINDINGS.md MF-03.)
```

## Data laporan tidak bisa diubah langsung

```
1. Di developer mode, coba buat/ubah baris "stock.history.view" secara langsung.
2. Harus gagal (error database) — laporan hanya hasil hitung, bukan data yang bisa diedit.
```

## Fungsi rebuild laporan tidak bisa dipanggil dari luar (fix keamanan 20.0)

```
1. Minta developer menjalankan test otomatis modul:
   test_ac_07_01_recreate_view_not_callable_over_rpc dan
   test_ac_07_02_recreate_view_rejects_non_integer_arguments
   (bagian dari ./run-test.sh di docker-env/).
2. Keduanya harus PASS.
3. Tombol "Stock History" di form produk tetap berfungsi normal (01_SMOKE.md).
   Catatan: fix ini HANYA ada di 20.0 — versi 17.0/18.0/19.0 belum diperbaiki (FINDINGS.md MF-10).
```

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-09-24 | Docker Run C (Community) + Run E (Enterprise) | AI (Integration test) | Pass | test_ac_05_01/02/03/04, test_ac_07_01/02 PASS |
