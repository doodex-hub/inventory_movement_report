# -*- coding: utf-8 -*-
# Tour test AC-01-01/AC-01-02 (migrasi 17.0->18.0, Step 9 Mode D) - klik nyata tombol "Stock
# History" lewat headless Chrome yang dikelola Odoo sendiri (HttpCase.start_tour), bukan
# automation eksternal. Companion JS: static/tests/tours/stock_history_tour.js.

from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged('post_install', '-at_install')
class TestStockHistoryTour(HttpCase):

    def setUp(self):
        super().setUp()
        self.env['product.template'].create({
            'name': 'TOUR QA Stock History Product',
            'is_storable': True,
        })

    def test_stock_history_tour(self):
        self.start_tour("/web", "stock_history_tour", login="admin")
