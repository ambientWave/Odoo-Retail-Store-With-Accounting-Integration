from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class OrderLine(models.Model):
    _name = "new.order.line"  # name of odoo business model that refers to restaurant menu. The dot delimiter is replaced by
    # underscore in some fields inside csv files
    # _inherit = ["mail.thread"]
    _description = "Retail One Order Line Transaction"

    product_item_id = fields.Many2one('product.product', 'الاصناف', domain=[('sale_ok', '=', True)], required=True, change_default=True)
    product_id = fields.Many2one('new.product')
    order_id = fields.Many2one('new.retail.order', ondelete='cascade', required=False, index=True)
    qty = fields.Float(string='الكمية', digits='Product Unit of Measure', default=1)
    price = fields.Float(related="product_item_id.lst_price", string='سعر الوحده', digits=0)
    order_line_subtotal = fields.Float(string='الاجمالي الفرعي', compute='compute_subtotal')

    product_item_available_qty = fields.Float(string='الكمية المتاحة', related='product_item_id.qty_available')

    discount = fields.Float(string='Discount (%)', digits=0, default=0.0)
    # tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False})
    tax_ids = fields.Many2many('account.tax', string='Taxes', readonly=True)
    tax_ids_after_fiscal_position = fields.Many2many('account.tax', compute='_get_tax_ids_after_fiscal_position', string='Taxes to Apply')
    product_uom_id = fields.Many2one('uom.uom', string='Product UoM', related='product_item_id.uom_id')

    @api.depends('order_id', 'order_id.fiscal_position_id')
    def _get_tax_ids_after_fiscal_position(self):
        for line in self:
            line.tax_ids_after_fiscal_position = line.order_id.fiscal_position_id.map_tax(line.tax_ids, line.product_item_id, line.order_id.partner_id)
    
    @api.model
    def create(self, vals):  # if the create button is pressed, the function will execute for each record line 
        # print(self.env['product.product'].search([('qty_available', '=', vals.get('product_item_available_qty'))])) # float operators are >= or <=
        product_stock_quantity_that_need_to_be_subtracted = self.env['stock.quant'].sudo(True).search([('product_id', '=', vals.get('product_item_id')), ('location_id', '=', 8)])
        
        product_stock_quantity_that_need_to_be_subtracted.quantity = (product_stock_quantity_that_need_to_be_subtracted['quantity'] - vals.get('qty')) # either computed member access: product_stock_quantity_that_need_to_be_subtracted['quantity'] or write method: product_stock_quantity_that_need_to_be_subtracted.write({"quantity": (product_stock_quantity_that_need_to_be_subtracted['quantity'] - vals.get('qty'))}) could be used
        # product_stock_quantity_that_need_to_be_subtracted.write({"quantity": (product_stock_quantity_that_need_to_be_subtracted['quantity'] - vals.get('qty'))}) # .write({"qty_available": vals.get('qty_available') - vals.get('qty')})
        # print(product_stock_quantity_that_need_to_be_subtracted['quantity'], type(product_stock_quantity_that_need_to_be_subtracted['quantity'])) # product_that_need_to_be_subtracted['qty_available'] has the same output as product_that_need_to_be_subtracted.qty_available
        '''
            move3 = self.env['stock.move'].create({
            'name': '12 out (2 negative)',
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'product_id': self.product1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 8.0,
            'price_unit': 0,
            'move_line_ids': [(0, 0, {
                'product_id': self.product1.id,
                'location_id': self.stock_location.id,
                'location_dest_id': self.customer_location.id,
                'product_uom_id': self.uom_unit.id,
                'qty_done': 8.0,
            })]
        })
        move3._action_confirm()
        move3._action_done()
        '''
        
        
        result = super(OrderLine, self).create(vals)
        return result

        # if we subtract from local field product_item_available_qty, does that update the related field? or the related field must be accessed directly?
        # try:
        #     print(vals, type(vals))
        #     for val in vals: # vals is a dictionary: {'order_id': 15, 'tax_ids': [[6, False, []]], 'tax_ids_after_fiscal_position': [[6, False, []]], 'product_item_id': 17, 'qty': 1} <class 'dict'>
        #         print(vals['qty'], type(vals['qty'])) # vals['qty'] has the same output (integer) as vals.get('qty') but maybe the former can modify the record (vals) field (qty) if used like this: vals['qty'] = <new_value>
        #         print(val, type(val)) # val is the name (string) of each field in the record
        #     result = super(OrderLine, self).create(vals)
        #     return result
        # except:
        #     print('exception!!!!!!!!!!!!!')

    

    @api.depends('price', 'qty')
    def compute_subtotal(self):
        for rec in self:
            print(rec['price'])
            added_items_price_ordered_list = rec.mapped('price') # rec['price'] used for field access to modify it
            added_items_quantity_ordered_list = rec.mapped('qty')

            item_price_multiplied_by_quantity = [price * qty for price, qty in
                                                 zip(added_items_price_ordered_list, added_items_quantity_ordered_list)]
            
            line_subtotal_value = sum(item_price_multiplied_by_quantity)

            
            print(item_price_multiplied_by_quantity) # a list that contains each line subtotal
            print(rec.ids)
            rec.order_line_subtotal = line_subtotal_value



    