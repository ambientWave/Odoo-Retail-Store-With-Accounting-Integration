# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class POSCombinedMenuItem(models.Model):
    _name = "combined.menu.item"  # name of odoo business model that refers to restaurant menu. The dot delimiter is replaced by
    # underscore in some fields inside csv files
    # _inherit = ["mail.thread"]
    _description = "Menu Item"
    _rec_name = "item_name"

    item_serial = fields.Char(string="مسلسل الصنف", required=True, copy=False, readonly=True, index=True,
                              default=lambda self: _("صنف جديد"))
    item_img = fields.Image("صورة الصنف")
    item_image = fields.Binary(string='صورة الصنف')
    item_name = fields.Char(string='اسم الصنف', required=False, tracking=True)  # name of food item inside the menu
    item_price = fields.Float(string='سعر الوحده', required=True)  # price of food item inside the menu
    quantity = fields.Float(string="الكمية", default=lambda self: _(0), store=True)
    sale_item_subtotal = fields.Float(string="اجمالي حساب الصنف", default=lambda self: _(0), store=True)#, compute='_compute_sale_subtotal_total_credit')
    sale_order_test = fields.Many2one('combined.sale.order', string='test')
    sale_order_test2 = fields.One2many('combined.sale.order', 'sale_item_test2', string='test')
    item_category = fields.Selection([
        ('salted pie', 'فطير حادق'),
        ('sweetened pie', 'فطير حلو'),
        ('sandwich', 'ساندويتش'),
        ('appetizer', 'اضافات'),
    ], required=False, string="نوع الصنف")
    no_of_orders_per_month = fields.Float(string='عدد الطلبات في الشهر', required=False)
    note = fields.Text(string='وصف الصنف')

    @api.onchange('quantity', 'sale_item_subtotal', 'combined.sale.order.sale_item_id')
    def onchange_sale_item_subtotal(self):
        if self.quantity:
            for rec in self:
                # rec.sale_item_subtotal = rec.quantity * rec.item_price
                sbttl = rec.quantity * rec.item_price
                rec.write({'sale_item_subtotal': sbttl})

    # @api.depends('sale_item_subtotal') #todo use the onchange method
    # def _compute_sale_subtotal_total_credit(self):
    #     i = self.item_price * self.quantity
    #     self.sale_item_subtotal.update({}) = i

    # @api.model
    # def create(self, vals):  # save button in the form view
    #     for rec in self:
    #         items_same_name = self.env['combined.item.menu'].search([('item_name', '=', rec.item_name)])
    #         if items_same_name:
    #             raise ValidationError("لا يمكنك ان تنشئ صنف مكرر")
    #     res = super(POSCombinedMenuItem, self).create(vals)
    #     return res

    @api.constrains('item_name')
    def check_name(self):
        for rec in self:
            items_same_name = self.env['combined.menu.item'].search([('item_name', '=', rec.item_name), ('id', '!=', rec.id)])
            if items_same_name:
                raise ValidationError("لا يمكنك ان تنشئ صنف مكرر")


class POSCombinedSaleItems(models.Model):
    _name = "combined.sale.items"
    # _inherit = ['mail.thread']
    _description = "Item Record Line of Sale Order Line"
    sale_id = fields.One2many('combined.sale.order', 'sale_item_test', string='مسلسل الفاتورة')
    item_id = fields.One2many('combined.menu.item', 'sale_order_test', string='مسلسل الصنف')
    item_id_price = fields.Float(related="item_id.item_price", string='سعر الوحدة')
    item_id_quantity = fields.Float(string='الكمية')
    item_subtotal = fields.Float(string="اجمالي حساب الصنف", default=lambda self: _(0), store=True)


class POSCombinedSaleOrder(models.Model):
    _name = "combined.sale.order"  # name of odoo business model that refers to restaurant menu. The dot delimiter is replaced by
    # underscore in some fields inside csv files
    _inherit = ['mail.thread']
    _rec_name = "sale_serial"
    _description = "Sale Order"
    _order = "sale_timestamp desc"  # field name followed by a space then type asc or desc

    sale_serial = fields.Char(string="مسلسل امر البيع", required=False, copy=False, readonly=True, index=True, default=lambda self: _("امر بيع جديد"))  #

    sale_timestamp = fields.Datetime(string='تاريخ الفاتورة', required=True, default=datetime.now())
    sale_item_id = fields.Many2many('combined.menu.item', string='الاصناف المباعة')
    sale_item_test = fields.One2many('combined.sale.items', 'sale_id', string="سجل الاصناف")
    sale_item_test2 = fields.Many2one('combined.sale.items', string="test2")
    sale_item_subtotal = fields.Float(string="اجمالي حساب الصنف", default=lambda self: _(0))

    # sale_item = fields.Char(string='اسم الصنف', required=False, tracking=True, related='sale_item_id.item_name')
    sale_total_credit = fields.Float(string='اجمالي الفاتورة', required=False, store=True, compute='_compute_sale_total_credit') # , related='sale_item_id.item_price') # )
    sale_status = fields.Selection([
        ('wait', 'انتظار'),
        ('in-operation', 'جاري العمل'),
        ('delivering', 'توصيل'),
        ('completed', 'تم الانتهاء'),
        ('cancelled', 'امر بيع ملغي'),
    ], required=False, string="حالة الطلب", tracking=True)
    sale_note = fields.Text(string='ملاحظات')
    assigned_deliveryman = fields.Char(string='مندوب التوصيل')

    customer_name = fields.Many2one('res.partner', string="اسم العميل")

    # def _get_rainbowman_message(self):
    #     message = False
    #     if self.user_id and self.team_id and self.expected_revenue:
    #         self.flush()  # flush fields to make sure DB is up to date
    #         query = """
    #             SELECT
    #                 SUM(CASE WHEN user_id = %(user_id)s THEN 1 ELSE 0 END) as total_won,
    #                 MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '30 days' AND user_id = %(user_id)s THEN expected_revenue ELSE 0 END) as max_user_30,
    #                 MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '7 days' AND user_id = %(user_id)s THEN expected_revenue ELSE 0 END) as max_user_7,
    #                 MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '30 days' AND team_id = %(team_id)s THEN expected_revenue ELSE 0 END) as max_team_30,
    #                 MAX(CASE WHEN date_closed >= CURRENT_DATE - INTERVAL '7 days' AND team_id = %(team_id)s THEN expected_revenue ELSE 0 END) as max_team_7
    #             FROM crm_lead
    #             WHERE
    #                 type = 'opportunity'
    #             AND
    #                 active = True
    #             AND
    #                 probability = 100
    #             AND
    #                 DATE_TRUNC('year', date_closed) = DATE_TRUNC('year', CURRENT_DATE)
    #             AND
    #                 (user_id = %(user_id)s OR team_id = %(team_id)s)
    #         """
    #         self.env.cr.execute(query, {'user_id': self.user_id.id,
    #                                     'team_id': self.team_id.id})
    #         query_result = self.env.cr.dictfetchone()
    #
    #         if query_result['total_won'] == 1:
    #             message = _('Go, go, go! Congrats for your first deal.')
    #         elif query_result['max_team_30'] == self.expected_revenue:
    #             message = _('Boom! Team record for the past 30 days.')
    #         elif query_result['max_team_7'] == self.expected_revenue:
    #             message = _('Yeah! Deal of the last 7 days for the team.')
    #         elif query_result['max_user_30'] == self.expected_revenue:
    #             message = _('You just beat your personal record for the past 30 days.')
    #         elif query_result['max_user_7'] == self.expected_revenue:
    #             message = _('You just beat your personal record for the past 7 days.')
    #     return message

    def _compute_employee_count(self):
        for item in self.with_context(active_test=False):
            item.employee_count = len(item.sale_item_id)

    def _get_price(self, parents):
        prices = parents.mapped('sale_item_id.item_price')
        for price in prices:
            price_sum = sum(prices)
        return price_sum

    # @api.onchange('sale_item_id')
    # def onchange_sale_item_subtotal(self):
    #     if self.sale_item_id:
    #         for rec in self:
    #             rec.sale_item_subtotal = rec.quantity * rec.item_price

    @api.depends('sale_item_id')
    def _compute_sale_total_credit(self):
        print(self)
        for rec in self:
            # todo don't forget to clarify that both two following variables are updated on
            # every change in sale order form
            sale_line_count = 0
            added_items_price_ordered_list = rec.sale_item_id.mapped('item_price')
            added_items_quantity_ordered_list = rec.sale_item_id.mapped('quantity')

            item_price_multiplied_by_quantity = [price * qty for price, qty in
                                                 zip(added_items_price_ordered_list, added_items_quantity_ordered_list)]
            print(rec.sale_item_id.ids)
            # if item_price_multiplied_by_quantity:
            #     rec.sale_item_id.sale_item_subtotal = rec.sale_item_id.item_price * rec.sale_item_id.quantity
            # if len(item_price_multiplied_by_quantity) >= 1:
            #     for id_recrd in rec.sale_item_id.ids:
            #         rec.sale_item_id.write({'sale_item_subtotal': item_price_multiplied_by_quantity[len(item_price_multiplied_by_quantity)-1]})
            added_items_subtotal_ordered_list = rec.sale_item_id.mapped('sale_item_subtotal')
            print(added_items_subtotal_ordered_list)
            # for rec2 in rec.sale_item_id.sale_item_subtotal:
            #     print(rec2.rec.sale_item_id.sale_item_subtotal)
            # for count in range(len(item_price_multiplied_by_quantity)):
            #     repr(self.sale_item_id.sale_item_subtotal)

            # rec.sale_item_id.sale_item_subtotal.clear()
            # rec.sale_item_id.sale_item_subtotal = item_price_multiplied_by_quantity[]

            # for count in range(len(item_price_multiplied_by_quantity)):
            #     rec.sale_item_id.sale_item_subtotal.append(
            #         item_price_multiplied_by_quantity[count])

            # print(rec.sale_item_id.convert_to_write(item_price_multiplied_by_quantity, 'sale_item_subtotal'))
            # for identity in rec.sale_item_id.ids:
            #     record_to_update = rec.env['combined.menu.item'].browse(identity)
            #     if record_to_update.exists():
            #         for subttl in item_price_multiplied_by_quantity:
            #             record_to_update.write({'sale_item_subtotal': subttl})
            #             rec.sale_item_id.write({'sale_item_subtotal': subttl})
                        # self.env.cr.execute("UPDATE combined_menu_item SET sale_item_subtotal = %s WHERE id = %s", (subttl, identity))
                        # rec.sale_item_id.update({'sale_item_subtotal': subttl})
                        # res.write({'partner_id': [(4, self.partner_id.id)]})
            print(rec)
            # for
            # range_id = self.env['combined.menu.item'].write({
            #     'name': str(item)
            # })
            #
            # (1, ID, {values})
            # ["x_company_ids"] = self.env['res.users'].search([('partner_id', '=', record.id)]).company_ids
            # rec.sale_item_id.mapped('sale_item_subtotal') = item_price_multiplied_by_quantity

            print(item_price_multiplied_by_quantity)
            # print(rec.sale_item_subtotal)
            # for number in range(len(item_price_multiplied_by_quantity)):
            #     # rec.update({'sale_item_subtotal': item_price_multiplied_by_quantity[number],})
            #     rec.sale_item_subtotal[number] = item_price_multiplied_by_quantity[number]
            print(len(rec))
            print(len(item_price_multiplied_by_quantity))
            rec.sale_total_credit = sum(item_price_multiplied_by_quantity)


            # item_price_multiplied_by_quantity = sum(
            # rec.sale_item_id.mapped('item_price')*rec.sale_item_id.mapped('quantity')) if rec.sale_item_id else 0
            # total = sum(rec.sale_item_id.mapped('item_price')) if rec.sale_item_id else 0
            # rec.sale_total_credit = total


        # for line in self.sale_total_credit:
        #     self.sale_total_credit2 += line.item_price
        #
        # sale_total_credit = self.env['menu.item'].search_count([('item_price', '=', self.id)])
        # self.sale_total_credit = sale_total_credit
        # print(api.Cache.get_values(self, self.sale_item_id, 'item_price'))
        # return api.Cache.get_values(self, self.sale_item_id, 'item_price')

    def write(self, vals):
        for rec in self.sale_item_id:
            sbttl = rec.item_price * rec.quantity

            rec.write({'sale_item_subtotal': sbttl})
        return super(POSCombinedSaleOrder, self).write(vals)

    # @api.onchange('sale_item_id')
    # def onchange_sale_item_subtotal(self):
    #     if self.sale_item_id:
    #         for rec in self:
    #             specific_record = self.env['combined.sale.order'].browse()
    #             if rec.sale_item_id.quantity:
    #                 rec.sale_item_id.sale_item_subtotal = rec.sale_item_id.quantity * rec.sale_item_id.item_price

    def unlink(self):
        if self.sale_status == 'completed':
            raise ValidationError("لا يمكنك ان تزيل امر البيع %s لانه منتهي" % self.sale_serial)
        return super(POSCombinedSaleOrder, self).unlink()

    @api.model
    def create(self, vals):  # save button in the form view
        for rec in self.sale_item_id:
            sbttl = rec.item_price * rec.quantity

            rec.create({'sale_item_subtotal': sbttl})
        if not vals.get('sale_note'):
            vals['sale_note'] = 'تشرفنا بخدمتك'
        if vals.get('sale_serial', _('New')) == _('New'):
            vals['sale_serial'] = self.env['ir.sequence'].next_by_code('combined.sale.order.sequence') or _('New')
        res = super(POSCombinedSaleOrder, self).create(vals)
        return res

    # def write(self, vals):
    #     return super(POSCombinedSaleOrder, self).write(vals)

    def action_wait(self):
        self.sale_status = "wait"

    def action_in_operation(self):
        self.sale_status = "in-operation"

    def action_delivering(self):
        self.sale_status = "delivering"

    def action_completed(self):
        self.sale_status = "completed"

    def action_cancelled(self):
        self.sale_status = "cancelled"
        return {
            'res_model': 'combined.sale.order',
            'view_type': 'tree',
            'view_mode': 'tree',
            'type': 'ir.actions.act_window_close',
            'view_id': self.env.ref('custom_restaurant.view_combined_sale_order_tree').id,
        }
