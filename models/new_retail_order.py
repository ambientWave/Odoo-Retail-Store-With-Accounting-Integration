from odoo import api, fields, models, _
from datetime import datetime
import pytz
from odoo.exceptions import ValidationError, UserError

class RetailOrder(models.Model):
    _name = "new.retail.order"  # name of odoo business model that refers to restaurant menu. The dot delimiter is replaced by
    # underscore in some fields inside csv files
    # _inherit = ["mail.thread"]
    _description = "Retail Order"
    _rec_name = "order_timestamp"

    order_line_id = fields.One2many('new.order.line', 'order_id', "الاصناف المباعة")
    user_id = fields.Many2one('res.users', 'البائع المسئول', default=lambda self: self.env.user)
    order_total = fields.Float('إجمالي الفاتورة', compute='compute_sale_total_credit', store=True)
    order_timestamp = fields.Datetime(string='تاريخ الفاتورة', required=True, default=datetime.now())
    invoice_status = fields.Selection([
        ('draft', 'امر بيع غير مؤكد'),
        ('confirm', 'تم تسجيل فاتورة الحسابات'),
    ], required=False, string="حالة تسجيل الفاتورة في الحسابات", tracking=True, default='draft')

    #TODO once order created, product qty should be discounted

    account_move = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False, index=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True)
    name = fields.Char(string='Order Ref', required=True, readonly=True, copy=False, default='/')
    date_order = fields.Datetime(string='Date', readonly=True, index=True, default=fields.Datetime.now)
    amount_tax = fields.Float(string='Taxes', digits=0, readonly=True, required=True)
    amount_total = fields.Float(string='Total', digits=0, readonly=True, required=True)
    amount_paid = fields.Float(string='Paid', states={'draft': [('readonly', False)]},
        readonly=True, digits=0, required=True)
    amount_return = fields.Float(string='Returned', digits=0, required=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=True, states={
                                   'draft': [('readonly', False)]}, readonly=True)
    partner_id = fields.Many2one('res.partner', string='اسم العميل', change_default=True, index=True, states={'draft': [('readonly', False)], 'paid': [('readonly', False)]})
    sequence_number = fields.Integer(string='Sequence Number', help='A session-unique sequence number for the order', default=1)

    currency_id = fields.Many2one('res.currency', related='config_id.currency_id', string="Currency")
    currency_rate = fields.Float("Currency Rate", store=True, digits=0, readonly=True,
        help='The rate of the currency to the currency of rate applicable at the date of the order')
    session_id = fields.Many2one(
        'pos.session', string='Session', required=True, index=True,
        domain="[('state', '=', 'opened')]", states={'draft': [('readonly', False)]},
        readonly=True)
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position', string='Fiscal Position',
        readonly=False)
    state = fields.Selection(
        [('draft', 'New'), ('cancel', 'Cancelled'), ('paid', 'Paid'), ('done', 'Posted'), ('invoiced', 'Invoiced')],
        'Status', readonly=True, copy=False, default='draft')
    config_id = fields.Many2one('pos.config', related='session_id.config_id', string="Point of Sale", readonly=False)





    
    @api.depends('order_line_id')
    def compute_sale_total_credit(self):
        print(self)
        
        for rec in self:
            # todo don't forget to clarify that both two following variables are updated on
            # every change in sale order form
            sale_line_count = 0
            added_items_price_ordered_list = rec.order_line_id.mapped('price')
            added_items_quantity_ordered_list = rec.order_line_id.mapped('qty')

            item_price_multiplied_by_quantity = [price * qty for price, qty in
                                                 zip(added_items_price_ordered_list, added_items_quantity_ordered_list)]
            
            sale_total_value = sum(item_price_multiplied_by_quantity)

            
            print(item_price_multiplied_by_quantity) # a list that contains each line subtotal
            print(rec.order_line_id.ids)
            rec.order_total = sale_total_value


        # moves = self.env['account.move']

	

        # for order in self:
        #     # Force company for all SUPERUSER_ID action
        #     if order.account_move:
        #         moves += order.account_move
        #         continue

        #     new_move = self.env['account.move'].sudo().with_company(self.company_id).with_context(default_move_type='out_invoice').create({'payment_reference': self.name,
        #     'invoice_origin': self.name,
        #     'journal_id': 1,
        #     'move_type': 'out_invoice',
        #     'ref': self.name,
        #     'partner_id': 14,
        #     'narration': "",
        #     # considering partner's sale pricelist's currency
        #     'currency_id': 2,
        #     'invoice_user_id': self.user_id.id,
        #     'invoice_date': self.order_timestamp,
        #     'fiscal_position_id': self.fiscal_position_id.id,
        #     'invoice_line_ids': [(0, None, {'product_id': 23, 'quantity': 8.0, 'discount': 0.0, 'price_unit': 16.5, 'name': '[E-COM12] Conference Chair (CONFIG) (Steel)', 'tax_ids': [(6, 0, [1])], 'product_uom_id': 1})],
        #     'invoice_cash_rounding_id': False})

        #     self.env['account.move.line'].with_context(check_move_validity=False).create({
        #     'debit': sale_total_value or 0.0,
        #     'credit': sale_total_value or 0.0,
        #     'quantity': 1.0,
        #     'amount_currency': sale_total_value,
        #     'partner_id': new_move.partner_id.id,
        #     'move_id': 54,
        #     'currency_id': False,
        #     'company_id': False,
        #     'company_currency_id': False,
        #     'is_rounding_line': True,
        #     'sequence': 9999,
        #     'name': new_move.invoice_cash_rounding_id.name,
        #     'account_id': 35,
        # })
        #     order.write({'account_move': new_move.id, 'state': 'invoiced'})
        #     new_move.sudo().with_company(order.company_id)._post()
        #     moves += new_move

        #     if not moves:
        #         return {}



#####################################



        # def _create_invoice(self, move_vals):

        #     new_move = self.env['account.move'].sudo().with_company(self.company_id).with_context(default_move_type=move_vals['move_type']).create(move_vals)
            
        #     {
        #     'debit': order_total or 0.0,
        #     'credit': order_total or 0.0,
        #     'quantity': 1.0,
        #     'amount_currency': sale_total_value,
        #     'partner_id': new_move.partner_id.id,
        #     'move_id': 54,
        #     'currency_id': False,
        #     'company_id': False,
        #     'company_currency_id': False,
        #     'is_rounding_line': True,
        #     'sequence': 9999,
        #     'name': new_move.invoice_cash_rounding_id.name,
        #     'account_id': 35,
        # }
        #     self.env['account.move.line'].with_context(check_move_validity=False).create({
        #         'debit': rounding_applied < 0.0 and -rounding_applied or 0.0,
        #         'credit': rounding_applied > 0.0 and rounding_applied or 0.0,
        #         'quantity': 1.0,
        #         'amount_currency': rounding_applied,
        #         'partner_id': new_move.partner_id.id,
        #         'move_id': new_move.id,
        #         'currency_id': new_move.currency_id if new_move.currency_id != new_move.company_id.currency_id else False,
        #         'company_id': new_move.company_id.id,
        #         'company_currency_id': new_move.company_id.currency_id.id,
        #         'is_rounding_line': True,
        #         'sequence': 9999,
        #         'name': new_move.invoice_cash_rounding_id.name,
        #         'account_id': account_id,
        #     })

        #     return new_move



        # def _prepare_invoice_vals(self):        
        #     vals = {
        #         'payment_reference': self.name,
        #         'invoice_origin': self.name,
        #         'journal_id': self.session_id.config_id.invoice_journal_id.id,
        #         'move_type': 'out_invoice' if self.amount_total >= 0 else 'out_refund',
        #         'ref': self.name,
        #         'partner_id': self.partner_id.id,
        #         # considering partner's sale pricelist's currency
        #         'currency_id': self.pricelist_id.currency_id.id,
        #         'invoice_user_id': self.user_id.id,
        #         'invoice_date': self.date_order.astimezone(timezone).date(),
        #         'fiscal_position_id': self.fiscal_position_id.id,
        # {
        #         'product_id': line.product_id.id,
        #         'quantity': line.qty if self.amount_total >= 0 else -line.qty,
        #         'discount': line.discount,
        #         'price_unit': line.price_unit,
        #         'name': line.product_id.display_name,
        #         'tax_ids': [(6, 0, [1])],
        #         'product_uom_id': line.product_uom_id.id,
        #     }
        # [(0, None, {'product_id': 23, 'quantity': 8.0, 'discount': 0.0, 'price_unit': 16.5, 'name': '[E-COM12] Conference Chair (CONFIG) (Steel)', 'tax_ids': [(6, 0, [])], 'product_uom_id': 1})],
        #         'invoice_line_ids': [(0, None, self._prepare_invoice_line(line)) for line in self.lines],
        #         'invoice_line_ids': [(0, None, {
        #     'product_id': line.product_item_id.id,
        #     'quantity': line.qty if self.amount_total >= 0 else -line.qty,
        #     'discount': line.discount,
        #     'price_unit': line.price,
        #     'name': line.product_item_id.display_name,
        #     'tax_ids': [(6, 0, [1])],
        #     'product_uom_id': line.product_uom_id.id,
        # }) for line in self.order_line_id],
        #         'invoice_cash_rounding_id': self.config_id.rounding_method.id
        #         if self.config_id.cash_rounding and (not self.config_id.only_round_cash_method or any(p.payment_method_id.is_cash_count for p in self.payment_ids))
        #         else False
        #     }
        #     return vals
        
    def action_order_invoice(self):
        # res = self._generate_pos_order_invoice()
        # return res
        
        moves = self.env['account.move']



        for order in self:
            # Force company for all SUPERUSER_ID action
            if order.account_move:
                moves += order.account_move
                continue

            new_move = self.env['account.move'].sudo().with_company(self.company_id).with_context(default_move_type='out_invoice').create({'payment_reference': self.name,
            'invoice_origin': self.name,
            'journal_id': 1,
            'move_type': 'out_invoice',
            'ref': self.name,
            'partner_id': self.partner_id.id,
            'narration': "",
            # considering partner's sale pricelist's currency
            'currency_id': 2,
            'invoice_user_id': self.user_id.id,
            'invoice_date': self.order_timestamp,
            'fiscal_position_id': self.fiscal_position_id.id,
            'invoice_line_ids': [(0, None, {
            'product_id': line.product_item_id.id,
            'quantity': line.qty if self.amount_total >= 0 else -line.qty,
            'discount': line.discount,
            'price_unit': line.price,
            'name': line.product_item_id.display_name,
            'tax_ids': [(6, 0, [1])],
            'product_uom_id': line.product_uom_id.id,
        }) for line in self.order_line_id],
            'invoice_cash_rounding_id': False})

            self.env['account.move.line'].with_context(check_move_validity=False).create({
            'debit': 0.0 or 0.0,
            'credit': 0.0 or 0.0,
            'quantity': 1.0,
            'amount_currency': self.order_total,
            'partner_id': new_move.partner_id.id,
            'move_id': 54,
            'currency_id': False,
            'company_id': False,
            'company_currency_id': False,
            'is_rounding_line': True,
            'sequence': 9999,
            'name': new_move.invoice_cash_rounding_id.name,
            'account_id': 35,
        })
            order.write({'account_move': new_move.id, 'state': 'invoiced', 'invoice_status': 'confirm'})
            new_move.sudo().with_company(order.company_id)._post()
            moves += new_move

            if not moves:
                return {}

        
        # def _generate_pos_order_invoice(self):
        #     moves = self.env['account.move']

        #     for order in self:
        #         # Force company for all SUPERUSER_ID action
        #         if order.account_move:
        #             moves += order.account_move
        #             continue

        #         if not order.partner_id:
        #             raise UserError(_('Please provide a partner for the sale.'))

        #         move_vals = order._prepare_invoice_vals()
        #         new_move = order._create_invoice(move_vals)
        #         order.write({'account_move': new_move.id, 'state': 'invoiced'})
        #         new_move.sudo().with_company(order.company_id)._post()
        #         moves += new_move

        #     if not moves:
        #         return {}
            


    @api.onchange('order_line_id')
    def onchange_sale_item_subtotal(self):
        for i in self:
            print(i)
        print()
        for i in self.env: # this is an important list
            print(type(self.env))
            print(type(i))
            print(i)
        print()
        print(self.env['new.order.line'])
        print()
        print(self.env['new.order.line'].search([('price', '=', 320)]))
        print()
        print(self.env['new.order.line']['price'])
        print()
        print(self.env['new.order.line'].mapped('price'))
        print()
        # print(self.order.line.id.mapped('price'))
        # print(self.env['new.order.line'].search([('product_id', '=', self.product_pizza.id), ('user_id', '=', pizza.user_id.id)]))
        if self.order_line_id:
            for rec in self.order_line_id:
                print(rec)
                # rec.sale_item_subtotal = rec.quantity * rec.item_price
                print(rec.qty * rec.price)
                # sbttl = rec.quantity * rec.item_price
                # rec.write({'order_total': sbttl})

