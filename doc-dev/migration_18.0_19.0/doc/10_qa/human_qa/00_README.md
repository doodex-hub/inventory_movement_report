# Human QA Checklists — product_history_report

**Sumber:** diturunkan dari skenario S-01..S-07 di `../10_BUSINESS_FLOW_MIGRATION.md`, dikelompokkan per `Level`.

| File | Isi | Kapan dipakai |
|---|---|---|
| `01_SMOKE.md` | S-01 — buka Stock History | Re-cek super cepat sebelum deploy/hotfix |
| `02_MAIN_FLOW.md` | S-02, S-03 — income-only & qty kumulatif | QA rutin |
| `03_DETAIL.md` | S-04, S-05, S-07 — multi-company, bug dipertahankan, & search panel groupby | QA menyeluruh sebelum rilis |
| `04_NEGATIVE.md` | S-06 — create/write/unlink ditolak | Sekali sebelum rilis besar |

**Kombinasi yang disarankan:**
- Deploy/hotfix kecil → `01_SMOKE.md` saja
- Deploy rutin → `01_SMOKE.md` + `02_MAIN_FLOW.md`
- Rilis besar / sebelum UAT → keempat file
