# Negative Test — product_history_report

**Level:** Negative — guard/keamanan, hal yang HARUS ditolak. Direkomendasikan dijalankan minimal sekali sebelum rilis besar.
**Estimasi waktu:** ~3 menit (butuh developer mode/technical access).
**Sumber:** S-06 di `../10_BUSINESS_FLOW_MIGRATION.md`.

```
1. Aktifkan Developer Mode (Settings -> Activate the developer mode).
2. Buka Odoo shell atau technical menu, coba create() record baru langsung ke model
   'stock.history.view' (mis. lewat odoo shell: env['stock.history.view'].create({...})).
3. Pastikan operasi GAGAL dengan error database (bukan pesan ACL Odoo yang ramah) --
   model ini SQL view tanpa INSTEAD OF trigger, create/write/unlink langsung HARUS
   selalu gagal di level database.
```

**Catatan:** Skenario ini sudah dikonfirmasi PASS lewat automated test Step 9
(`test_ac_05_02_create_on_view_fails`) -- checklist ini untuk re-verifikasi manual
opsional, tidak wajib diulang kalau sudah percaya hasil test otomatis.

## Hasil eksekusi

| Tanggal | Environment | Dijalankan oleh | Hasil | Catatan |
|---|---|---|---|---|
| 2026-08-24 | Odoo 18.0, docker (odoo:18.0 resmi) | AI (automated test, bukan klik manual) | Pass | Dikonfirmasi `test_ac_05_02_create_on_view_fails`, 0 failed 0 error dari 8 test |
