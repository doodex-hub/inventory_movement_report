# -*- coding: utf-8 -*-
# BACKFILL — test baru ditambahkan retroaktif (modul tidak punya tests/ sama sekali sebelumnya).
# Ref: doc-dev/backfill/spec/01B_ACCEPTANCE_CRITERIA.md, doc-dev/backfill/test/03B_TEST_PLAN.md
from datetime import date, timedelta

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestProductHistoryReport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.internal_loc = cls.env.ref('stock.stock_location_stock')
        cls.customer_loc = cls.env.ref('stock.stock_location_customers')
        cls.supplier_loc = cls.env.ref('stock.stock_location_suppliers')
        cls.internal_loc_b = cls.env['stock.location'].create({
            'name': 'BACKFILL Shelf B',
            'usage': 'internal',
            'location_id': cls.internal_loc.location_id.id,
        })
        cls.product = cls.env['product.template'].create({
            'name': 'BACKFILL Test Product',
            'is_storable': True,
        })

    def _picking_type_for(self, src, dest, company):
        # Menentukan picking type dari arah lokasi supaya button_validate() tidak menolak
        # kombinasi (lihat lesson di bawah soal kenapa _action_done() langsung tidak dipakai).
        if src.usage == 'internal' and dest.usage == 'internal':
            xmlid = 'stock.picking_type_internal'
        elif dest.usage == 'internal':
            xmlid = 'stock.picking_type_in'
        else:
            xmlid = 'stock.picking_type_out'
        picking_type = self.env.ref(xmlid)
        if company and picking_type.company_id and picking_type.company_id != company:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', picking_type.code), ('company_id', '=', company.id)], limit=1
            ) or picking_type
        return picking_type

    def _make_move(self, src, dest, qty, move_date, company=None):
        company = company or self.env.company
        # LESSON (ditemukan lewat eksekusi nyata Step 04 BACKFILL, bukan dugaan — lihat
        # doc-dev-backfill/records/product_history_report/SUMMARY.md): memanggil
        # `stock.move._action_confirm()/_action_assign()/_action_done()` LANGSUNG (tanpa lewat
        # `stock.picking.button_validate()`) TIDAK benar-benar menyelesaikan move di Odoo 17 —
        # `move.state` sempat terbaca "done" dari cache ORM tepat setelah `_action_done()`
        # dipanggil, TAPI baris `stock_move` di database tetap `state='draft'` dan
        # `stock_move_line.picked` balik ke `False` (dibuktikan lewat query SQL mentah, bukan
        # baca field ORM). `button_validate()` adalah jalur resmi (sama seperti tombol
        # "Validate" di UI) yang menandai `picked=True` dan benar-benar menuntaskan `_action_done()`.
        picking_type = self._picking_type_for(src, dest, company)
        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': src.id,
            'location_dest_id': dest.id,
            'company_id': company.id,
        })
        move = self.env['stock.move'].create({
            'name': 'BACKFILL test move',
            'picking_id': picking.id,
            'product_id': self.product.product_variant_id.id,
            'product_uom_qty': qty,
            'product_uom': self.product.uom_id.id,
            'location_id': src.id,
            'location_dest_id': dest.id,
            'company_id': company.id,
        })
        picking.action_confirm()
        picking.action_assign()
        for line in move.move_line_ids:
            line.quantity = qty
        picking.button_validate()

        # `write({'date': ...})` lewat ORM setelah validate TIDAK berefek ke kolom DB (root cause
        # belum ditelusuri lebih jauh — di luar scope BACKFILL untuk memperbaiki behavior Odoo
        # core). Test-only workaround: UPDATE langsung ke tabel via cursor, lalu invalidate cache.
        self.env.cr.execute(
            "UPDATE stock_move_line SET date = %s WHERE id IN %s",
            (move_date, tuple(move.move_line_ids.ids)),
        )
        move.move_line_ids.invalidate_recordset(['date'])
        return move

    def _companies_str(self, companies):
        return ','.join(map(str, companies.ids))

    # --- AC-01-01 : tombol "Stock History" ada di arch form product.template ---
    def test_ac_01_01_button_present_in_form_arch(self):
        view = self.env['product.template'].get_view(view_type='form')
        self.assertIn('action_open_stock_history', view['arch'],
                       "Tombol Stock History (name=action_open_stock_history) harus ada di arch form product.template")

    # --- AC-01-02 : klik tombol mengembalikan action window yang benar ---
    def test_ac_01_02_action_open_stock_history_returns_expected_action(self):
        action = self.product.action_open_stock_history()
        self.assertEqual(action['res_model'], 'stock.history.view')
        self.assertEqual(action['view_mode'], 'graph,pivot,list')
        self.assertIn('domain', action)

    # --- AC-02-01 : qty running-sum memasukkan saldo dari histori > 13 bulan ---
    def test_ac_02_01_qty_includes_pre_window_balance(self):
        far_past = date.today() - timedelta(days=450)  # > 13.2 bulan lalu
        self._make_move(self.supplier_loc, self.internal_loc, 100.0, far_past)

        recent = date.today() - timedelta(days=10)
        self._make_move(self.supplier_loc, self.internal_loc, 5.0, recent)

        companies = self._companies_str(self.env.companies)
        self.env['stock.history.view'].recreate_view(self.product.id, companies)
        rows = self.env['stock.history.view'].search(
            [('product_template_id', '=', self.product.id)], order='date')
        self.assertTrue(rows, "Harus ada baris stock.history.view setelah recreate_view")
        last_qty = rows[-1].qty
        self.assertAlmostEqual(last_qty, 105.0, places=2,
                                msg="qty kumulatif baris terakhir harus mencakup 100 (>13 bulan lalu) + 5 (baru)")

    # --- AC-03-01 : move customer->internal (return) masuk income saja ---
    def test_ac_03_01_customer_return_is_income_only(self):
        move_date = date.today() - timedelta(days=5)
        self._make_move(self.customer_loc, self.internal_loc, 7.0, move_date)

        companies = self._companies_str(self.env.companies)
        self.env['stock.history.view'].recreate_view(self.product.id, companies)
        row = self.env['stock.history.view'].search([
            ('product_template_id', '=', self.product.id),
            ('date', '=', move_date.replace(day=1) + timedelta(days=31)),
        ], limit=1) or self.env['stock.history.view'].search(
            [('product_template_id', '=', self.product.id)], order='date desc', limit=1)
        self.assertGreaterEqual(row.income, 7.0)
        self.assertEqual(row.outcome, 0.0)

    # --- AC-03-02 : move internal->internal dihitung DI KEDUA income dan outcome ---
    def test_ac_03_02_internal_transfer_counted_as_both_income_and_outcome(self):
        # isi stok dulu di internal_loc lewat supplier->internal
        self._make_move(self.supplier_loc, self.internal_loc, 20.0, date.today() - timedelta(days=3))
        # transfer internal -> internal (dua-duanya usage='internal')
        self._make_move(self.internal_loc, self.internal_loc_b, 4.0, date.today() - timedelta(days=1))

        companies = self._companies_str(self.env.companies)
        self.env['stock.history.view'].recreate_view(self.product.id, companies)
        rows = self.env['stock.history.view'].search(
            [('product_template_id', '=', self.product.id)], order='date desc', limit=1)
        # baris bulan berjalan: income = 20 (in) + 4 (internal->internal) = 24, outcome = 4
        self.assertGreaterEqual(rows.income, 24.0)
        self.assertGreaterEqual(rows.outcome, 4.0)

    # --- AC-04-01 : filter multi-company — company lain tidak ikut terhitung ---
    def test_ac_04_01_company_filter_excludes_other_company(self):
        self._make_move(self.supplier_loc, self.internal_loc, 9.0, date.today() - timedelta(days=2))

        # kontrol: dengan company yang BENAR, income harus > 0
        companies = self._companies_str(self.env.companies)
        self.env['stock.history.view'].recreate_view(self.product.id, companies)
        rows_correct = self.env['stock.history.view'].search(
            [('product_template_id', '=', self.product.id)])
        self.assertGreater(sum(rows_correct.mapped('income')), 0.0,
                            "Sanity check: dengan company yang benar, income harus > 0")

        # kandidat: dengan company id yang TIDAK cocok, income harus 0
        fake_other_company_id = self.env.company.id + 999999
        self.env['stock.history.view'].recreate_view(self.product.id, str(fake_other_company_id))
        # `recreate_view()` DROP+CREATE lewat SQL mentah (bypass ORM) — ORM TIDAK tahu isi view
        # berubah dan bisa menyajikan field value dari cache `search()` sebelumnya (id row sama
        # persis karena PK view = product_template_id+YYYYMMDD, deterministik per produk). Invalidate
        # eksplisit di sini murni supaya TEST INI (dua kali recreate_view dalam satu environment yang
        # sama) valid — bukan mensimulasikan bug produksi (di produksi tiap klik tombol = request/env
        # baru). Lihat FINDINGS.md F-01 untuk catatan terkait risiko cache-staleness ini.
        self.env['stock.history.view'].invalidate_model()
        rows = self.env['stock.history.view'].search(
            [('product_template_id', '=', self.product.id)])
        total_income = sum(rows.mapped('income'))
        self.assertEqual(total_income, 0.0,
                          "Move milik company asli tidak boleh ikut terhitung kalau filter companies di-set ke company lain")

    # --- AC-05-01 : read stock.history.view terbuka untuk user tanpa grup Inventory khusus ---
    def test_ac_05_01_read_open_for_user_without_inventory_group(self):
        companies = self._companies_str(self.env.companies)
        self.env['stock.history.view'].recreate_view(self.product.id, companies)

        plain_user = self.env['res.users'].create({
            'name': 'BACKFILL Plain User',
            'login': 'backfill_plain_user',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        # sanity: user ini TIDAK punya grup stock manapun
        self.assertFalse(plain_user.has_group('stock.group_stock_user'))
        rows = self.env['stock.history.view'].with_user(plain_user).search(
            [('product_template_id', '=', self.product.id)])
        self.assertTrue(rows, "User tanpa grup Inventory tetap bisa search/read stock.history.view (ACL longgar, lihat FINDINGS.md F-04)")

    # --- AC-05-02 : create/write/unlink langsung ke SQL view gagal di level DB ---
    def test_ac_05_02_create_on_view_fails(self):
        with self.assertRaises(Exception), mute_logger('odoo.sql_db'):
            self.env['stock.history.view'].create({
                'date': date.today(),
                'income': 1.0,
            })
