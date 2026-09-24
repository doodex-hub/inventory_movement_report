# Human QA Checklists — product_history_report (Odoo 20.0)

**Sumber:** diturunkan dari skenario S-XX di `../10_BUSINESS_FLOW_MIGRATION.md`, dikelompokkan per `Level`. Kalau skenario/level di file itu berubah, regenerate 4 file di folder ini juga — jangan diedit terpisah sampai tidak sinkron.

**WAJIB digenerate di step 10, TERLEPAS dari mode eksekusi QA yang dipilih** (Manual / AI-interaktif / AI+tool — lihat `ai-doc/OVERVIEW.md` §5b). Kalau AI yang menjalankan skenario S-XX lewat browser automation, folder ini TETAP digenerate — supaya manusia (dev/QA/PM) tetap punya cara re-verifikasi sendiri kapan saja tanpa perlu AI atau tooling apapun, cukup baca dan ikuti langkah bernomor.

Tiap file berisi HANYA skenario dari satu `Level`, format bahasa manusia (bukan jargon AC/BSL), langkah bernomor siap-jalan, tanpa duplikasi ke file lain.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | Flow paling kritis saja | Re-cek super cepat sebelum deploy/hotfix — kalau ini gagal, STOP, jangan lanjut apapun |
| `02_MAIN_FLOW.md` | Flow bisnis inti sehari-hari | QA rutin dengan waktu terbatas, atau setelah deploy fitur baru yang menyentuh flow utama |
| `03_DETAIL.md` | Varian/edge-case, fitur sekunder | QA menyeluruh sebelum rilis besar, atau setelah bug report terkait edge-case |
| `04_NEGATIVE.md` | Guard/keamanan, hal yang HARUS ditolak | Direkomendasikan dijalankan minimal sekali sebelum rilis besar APAPUN, terlepas dari waktu — ini soal keamanan, bukan cuma fungsi |

Angka prefix (01-04) = urutan prioritas kalau waktu terbatas (Smoke dulu, baru Main Flow, dst) — bukan urutan wajib dijalankan berurutan.

**Kombinasi yang disarankan (bukan aturan kaku — sesuaikan konteks):**
- Deploy/hotfix kecil, waktu sangat terbatas → `01_SMOKE.md` saja
- Deploy rutin, waktu cukup → `01_SMOKE.md` + `02_MAIN_FLOW.md`
- Rilis besar / sebelum UAT (step 11) → keempat file
- Kapan pun ada perubahan yang berpotensi menyentuh keamanan/guard (misal ubah logic disable, policy, lockout) → jalankan `04_NEGATIVE.md` terlepas dari kombinasi lain yang dipilih

**Kalau modul ini tidak punya skenario di salah satu Level** (misal tidak ada skenario Negative sama sekali) — tulis file itu tetap ada, isinya "N/A — modul ini tidak punya skenario ber-Level ini di `10_BUSINESS_FLOW_MIGRATION.md`", jangan dihapus filenya (supaya strukturnya konsisten antar-project).
