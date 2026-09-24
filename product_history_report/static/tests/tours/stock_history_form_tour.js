/** @odoo-module **/
// stock_history_form_tour.js — Tour test AC-01-04/AC-01-05, migrasi 19.0->20.0.
// Companion Python: tests/test_stock_history_tour.py::test_stock_history_form_tour.
// Dimulai langsung dari form produk fixture (URL diberikan start_tour), jadi tidak bergantung pada
// menu apps Community — jalan di Community DAN Enterprise (Home Menu web_enterprise, DIFF-12).
// Memverifikasi ikon tombol benar-benar dirender sebagai Material Symbols di DOM (DIFF-02), lalu
// klik tombol membuka action "Stocks Histories" dengan graph sebagai view pertama.

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("stock_history_form_tour", {
    test: true,
    url: "/odoo",
    steps: () => [
        {
            trigger: 'button[name="action_open_stock_history"] i.o_button_icon[data-icon="android_cell_5_bar"]',
            content: "The Stock History stat button renders the Material Symbols signal icon (not fa-signal)",
        },
        {
            trigger: 'button[name="action_open_stock_history"]',
            content: "Click the Stock History stat button",
            run: "click",
        },
        {
            trigger: '.o_breadcrumb .active:contains("Stocks Histories")',
            content: "The action window replaced the product form (target: current)",
        },
        {
            trigger: ".o_graph_renderer",
            content: "Graph is the first view of the action (view_mode graph,pivot,list)",
        },
    ],
});
