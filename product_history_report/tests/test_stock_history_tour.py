# -*- coding: utf-8 -*-
# Tour test AC-01-01/AC-01-02 (migrasi 17.0->18.0, Step 9 Mode D) - klik nyata tombol "Stock
# History" lewat headless Chrome yang dikelola Odoo sendiri (HttpCase.start_tour), bukan
# automation eksternal. Companion JS: static/tests/tours/stock_history_tour.js.
# Migrasi 19.0->20.0: + test_stock_history_form_tour (static/tests/tours/stock_history_form_tour.js),
# edition-agnostic (Community & Enterprise), memverifikasi ikon Material di DOM (DIFF-02/DIFF-12).

from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged('post_install', '-at_install')
class TestStockHistoryTour(HttpCase):

    def setUp(self):
        super().setUp()
        self.product = self.env['product.template'].create({
            'name': 'TOUR QA Stock History Product',
            'is_storable': True,
        })

    def test_stock_history_tour(self):
        # web_enterprise (auto_install bersama web) mengganti menu apps Community (.o_navbar_apps_menu)
        # dengan Home Menu, jadi navigasi tour ini hanya valid di Community (02_DIFF_ANALYSIS.md DIFF-12).
        # Di Enterprise, alur klik tombol dicakup test_stock_history_form_tour.
        if self.env['ir.module.module'].search_count([('name', '=', 'web_enterprise'), ('state', '=', 'installed')]):
            self.skipTest("web_enterprise terinstal: Home Menu menggantikan .o_navbar_apps_menu (DIFF-12)")
        self.start_tour("/web", "stock_history_tour", login="admin")

    def test_stock_history_form_tour(self):
        self.start_tour(
            f"/odoo/action-stock.product_template_action_product/{self.product.id}",
            "stock_history_form_tour",
            login="admin",
        )
