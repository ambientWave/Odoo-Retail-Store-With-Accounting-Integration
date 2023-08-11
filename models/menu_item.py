# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import psycopg2

# initiate connection to the db
con = psycopg2.connect(host='127.0.0.1', database='odoo', user='odoo', password='admin', port='5432')
cur = con.cursor()


class MenuItem(models.Model):
    _name = "menu.item"  # name of odoo business model that refers to restaurant menu. The dot delimiter is replaced by
    # underscore in some fields inside csv files
    _inherit = ["mail.thread"]
    _description = "Menu Item"

    item_serial = fields.Char(string="مسلسل الصنف", required=True, copy=False, readonly=True, index=True, default=lambda self: _("صنف جديد"))
    item_img = fields.Image("صورة الصنف")
    item_name = fields.Char(string='اسم الصنف', required=False, tracking=True)  # name of food item inside the menu
    item_price = fields.Float(string='سعر الوحده', required=False) # price of food item inside the menu
    item_category = fields.Selection([
        ('salted pie', 'فطير حادق'),
        ('sweetened pie', 'فطير حلو'),
        ('sandwich', 'ساندويتش'),
        ('appetizer', 'اضافات'),
        ], required=False, string="نوع الصنف",
        help="نوع الصنف ينقسم الي اربعة انواع."
             "فطير حادق، فطير حلو، ساندويتش، اضافات")
    no_of_orders_per_month = fields.Float(string='عدد الطلبات في الشهر', required=False)
    note = fields.Text(string='وصف الصنف')
    type_of_record = fields.Selection([('menu item', 'صنف'),
                                       ('sale transaction', 'امر بيع'),],
                                      string="نوع السجل", required=True)
    sale_serial = fields.Char(string="مسلسل امر البيع", required=True, copy=False, readonly=True, index=True, default=lambda self: _("امر بيع جديد"))  #
    sale_timestamp = fields.Datetime(string='تاريخ الفاتورة', required=False)
    sale_item_id = fields.Many2one('menu.item', string='الاصناف المباعة')
    sale_item = fields.Char(string='اسم الصنف', required=False, tracking=False, related='sale_item_id.item_name')
    sale_total_credit = fields.Float(string='اجمالي الفاتورة', required=False) # , compute='_compute_sale_total_credit')  #
    sale_total_credit2 = fields.Float(string='اجمالي الفاتورة 2', required=False) # , compute='_compute_sale_total_credit')
    sale_status = fields.Selection([
        ('wait', 'انتظار'),
        ('in-operation', 'جاري العمل'),
        ('delivering', 'توصيل'),
        ('completed', 'تم الانتهاء'),
        ('cancelled', 'امر بيع ملغي'),
    ], required=False, string="حالة الطلب", tracking=True)
    sale_note = fields.Text(string='ملاحظات')
    assigned_deliveryman = fields.Char(string='مندوب التوصيل')

    customer_name = fields.Many2one(comodel_name="res.partner", string="اسم العميل")
    # customer_phone =
    # customer_address =

    def _compute_sale_total_credit(self):
        cur.execute("select item_name, item_price from item_menu")
        rows = cur.fetchall()
        for r in rows:
            print(f"item name {r[0]} name {r[1]}")
        cur.close()
        for rec in self:
            total = sum(rec.sale_item_id.mapped('item_price'))
            rec.sale_total_credit = total

    def _compute_sale_total_credit2(self):
        sale_total_credit_sum = self.env['menu.item'].search_count([])
        self.sale_total_credit2 = sale_total_credit_sum

    def action_wait(self):
        self.sale_status = "wait"

    def action_in_operation(self):
        self.sale_status = "in-operation"

    def action_delivering(self):
        self.sale_status = "delivering"

    def action_completed(self):
        self.sale_status = "completed"

    @api.model
    def create(self, vals):  # save button in the form view
        # for topping in vals.get('topping_ids_2', []):
        #     topping[2].update({'topping_category': 2})
        # for topping in vals.get('topping_ids_3', []):
        #     topping[2].update({'topping_category': 3})
        if not vals.get('sale_note'):
            vals['sale_note'] = 'تشرفنا بخدمتك'
        if vals.get('item_serial', _('New')) == _('New'):
            vals['item_serial'] = self.env['ir.sequence'].next_by_code('menu.item.sequence') or _('New')
        if vals.get('sale_serial', _('New')) == _('New'):
            vals['sale_serial'] = self.env['ir.sequence'].next_by_code('menu.item.sale.sequence') or _('New')

        return super(MenuItem, self).create(vals)

    def action_cancelled(self):
        self.sale_status = "cancelled"
        return {
            'res_model': 'menu.item',
            'view_type': 'tree',
            'view_mode': 'tree',
            'type': 'ir.actions.act_window_close',
            'view_id': self.env.ref('custom_restaurant.view_sale_order_tree').id,
        }

    def edit_sale_order(self):
        return {
            'res_model': 'menu.item',
            'res_id': self.env.ref('id'),
            'view_type': 'form',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('custom_restaurant.view_sale_order_form').id,
        }

    @api.onchange('sale_item_id')  # multiple field names can be passed by using comma then type the field name
    # with separate quotes
    def onchange_sale_item_id(self):
        if self.sale_item_id:  # if sale_item_id contains something selected by user i.e. True
            if self.sale_item_id.item_category:
                self.item_category = self.sale_item_id.item_category
        else:
            self.item_category = ''


# con.close()
