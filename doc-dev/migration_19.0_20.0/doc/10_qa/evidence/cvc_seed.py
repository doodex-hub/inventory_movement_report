from datetime import date, timedelta
P = env['product.template'].create({'name': 'QA20 CVC Product', 'is_storable': True})
stock = env.ref('stock.stock_location_stock')
cust = env.ref('stock.stock_location_customers')
supp = env.ref('stock.stock_location_suppliers')
shelf = env['stock.location'].create({'name': 'QA Shelf B', 'usage': 'internal', 'location_id': stock.location_id.id})
uomkey = 'product_uom' if 'product_uom' in env['stock.move']._fields else 'uom_id'

def mv(src, dst, qty, d):
    xmlid = 'stock.picking_type_internal' if src.usage == dst.usage == 'internal' else ('stock.picking_type_in' if dst.usage == 'internal' else 'stock.picking_type_out')
    pt = env.ref(xmlid)
    pk = env['stock.picking'].create({'picking_type_id': pt.id, 'location_id': src.id, 'location_dest_id': dst.id})
    m = env['stock.move'].create({'picking_id': pk.id, 'product_id': P.product_variant_id.id, 'product_uom_qty': qty,
                                  uomkey: P.uom_id.id, 'location_id': src.id, 'location_dest_id': dst.id})
    pk.action_confirm()
    pk.action_assign()
    for line in m.move_line_ids:
        line.quantity = qty
    pk.button_validate()
    env.flush_all()
    env.cr.execute("UPDATE stock_move_line SET date = %s WHERE id IN %s", (d, tuple(m.move_line_ids.ids)))
    env.invalidate_all()

t = date.today()
mv(supp, stock, 100, t - timedelta(days=450))   # saldo pembuka (> 13.2 bulan)
mv(supp, stock, 40, t - timedelta(days=200))
mv(stock, cust, 15, t - timedelta(days=100))
mv(cust, stock, 7, t - timedelta(days=40))       # retur customer -> income
mv(stock, shelf, 4, t - timedelta(days=5))       # internal->internal (double count, MF-02)
mv(supp, stock, 5, t - timedelta(days=3))
env.cr.commit()
env['stock.history.view'].recreate_view(P.id, ','.join(map(str, env.companies.ids)))
rows = env['stock.history.view'].search([('product_template_id', '=', P.id)], order='date')
print('SEEDED product_template_id=%s moves_done=%s' % (P.id, env['stock.move'].search_count([('product_id', '=', P.product_variant_id.id), ('state', '=', 'done')])))
for r in rows:
    print('ROW %s | in=%.3f | out=%.3f | qty=%.3f' % (r.date, r.income, r.outcome, r.qty))
env.cr.commit()
