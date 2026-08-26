/** @odoo-module **/
// stock_history_tour.js — Tour test AC-01-01/AC-01-02, migrasi 17.0->18.0.
// Companion Python: tests/test_stock_history_tour.py.
// Menguji alur nyata: buka produk fixture -> klik tombol "Stock History" -> window action
// (target: 'current', BUKAN dialog) berganti breadcrumb jadi "Stocks Histories".

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("stock_history_tour", {
    test: true,
    url: "/web",
    steps: () => [
        {
            trigger: ".o_navbar_apps_menu button",
            content: "Open the apps menu",
            run: "click",
        },
        {
            trigger: '.o_app[data-menu-xmlid="stock.menu_stock_root"]',
            content: "Open the Inventory app",
            run: "click",
        },
        {
            trigger: 'button:contains("Products")',
            content: "Open the Products menu dropdown",
            run: "click",
        },
        {
            trigger: '.dropdown-item:contains("Products")',
            content: "Open the Products list",
            run: "click",
        },
        {
            trigger: ".o_searchview_input",
            content: "Click the search bar",
            run: "click",
        },
        {
            trigger: ".o_searchview_input",
            content: "Type the fixture product name",
            run: "edit TOUR QA Stock History Product",
        },
        {
            trigger: ".o_searchview_input",
            content: "Confirm the search",
            run: "press Enter",
        },
        {
            trigger: '.o_kanban_record:contains("TOUR QA Stock History Product")',
            content: "Open the fixture product (default Products view is Kanban, not list)",
            run: "click",
        },
        {
            trigger: 'button:contains("Stock History")',
            content: "Click the Stock History stat button (visible directly in the button box in 19.0, no longer collapsed into '.o_button_more' overflow menu like 18.0)",
            run: "click",
        },
        {
            trigger: '.o_breadcrumb .active:contains("Stocks Histories")',
            content: "The action window replaced the current view (target: current), breadcrumb confirms it opened",
        },
    ],
});
