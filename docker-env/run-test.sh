#!/usr/bin/env bash
# ==========================================================================
# run-test.sh — wrapper WAJIB untuk SEMUA eksekusi G1/Step 9 lewat Docker
# (diinstansiasi dari migration-tool/templates/run-test.sh.template via
#  optional_field_save 19->20, diadaptasi 2026-09-24 untuk product_history_report)
# ==========================================================================
# Mencegah 2 false-pass yang terdokumentasi:
#  1. `--test-tags /modul` di-mangle MSYS/Git Bash -> tag kosong -> "0 tests". Dicegah dengan
#     MSYS_NO_PATHCONV=1.
#  2. DB yang sudah pernah `-i` membuat install+test di-skip diam-diam. Dicegah dengan
#     `docker compose down -v` sebelum DAN sesudah tiap run (DB selalu baru).
# Sanity-check: jumlah baris log "Starting <Class>.<method>" harus > 0.
#
# USAGE (dari folder docker-env/):
#   ./run-test.sh                      # Run C — Community, install + semua test modul
#   EDITION=enterprise ./run-test.sh   # Run E — + enterprise20 di addons-path, install
#                                      #   stock_enterprise,quality_control,stock_barcode juga
#   NO_TESTS=1 ./run-test.sh           # G1 install-only (tanpa --test-enable)
# ==========================================================================
set -uo pipefail

MODULE_NAME="product_history_report"
EDITION="${EDITION:-community}"
NO_TESTS="${NO_TESTS:-}"
DB_NAME="phr20_${EDITION}"
ADDONS_PATH="/opt/odoo/addons,/opt/odoo/odoo/addons,/mnt/extra-addons"
INSTALL="${MODULE_NAME}"
if [ "${EDITION}" = "enterprise" ]; then
  ADDONS_PATH="/opt/enterprise,${ADDONS_PATH}"
  INSTALL="${MODULE_NAME},stock_enterprise,quality_control,stock_barcode"
fi

mkdir -p logs
STAMP="$(date +%Y%m%d-%H%M%S)"
LOGFILE="logs/run-${EDITION}-${STAMP}.log"

TEST_ARGS=(--test-enable --test-tags "/${MODULE_NAME}")
[ -n "${NO_TESTS}" ] && TEST_ARGS=()

echo "=== run-test.sh: edition=${EDITION} db=${DB_NAME} install=${INSTALL} tests=$([ -n "${NO_TESTS}" ] && echo OFF || echo ON) ==="
echo "=== log: docker-env/${LOGFILE} ==="

docker compose down -v 2>&1 | tail -3

MSYS_NO_PATHCONV=1 docker compose run --rm odoo \
  -d "${DB_NAME}" -i "${INSTALL}" --without-demo=true \
  --addons-path="${ADDONS_PATH}" \
  "${TEST_ARGS[@]}" --stop-after-init 2>&1 | tee "${LOGFILE}"
RC=${PIPESTATUS[0]}

echo ""
echo "=== Sanity check ==="
echo "Exit code odoo-bin: ${RC}"
ERRORS=$(grep -cE " (ERROR|CRITICAL) " "${LOGFILE}" || true)
echo "Baris log ERROR/CRITICAL: ${ERRORS}"
if [ -z "${NO_TESTS}" ]; then
  STARTED=$(grep -c "Starting " "${LOGFILE}" || true)
  SUMMARY=$(grep -E "[0-9]+ failed, [0-9]+ error\(s\) of [0-9]+ tests" "${LOGFILE}" | tail -1 || true)
  echo "Baris 'Starting <Class>.<method>': ${STARTED}"
  echo "Ringkasan Odoo: ${SUMMARY:-'(tidak ada)'}"
  if [ "${STARTED}" -eq 0 ]; then
    echo "GAGAL — 0 test ter-start (pola false-pass). Periksa ${LOGFILE}."
    RC=2
  fi
fi

docker compose down -v 2>&1 | tail -3
exit "${RC}"
