from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class Product(models.Model):
    _name = "new.product"  # name of odoo business model that refers to restaurant menu. The dot delimiter is replaced by
    # underscore in some fields inside csv files
    # _inherit = ["mail.thread"]
    _description = "Traded Item"
    _rec_name = "item_name"

    item_serial = fields.Char(string="مسلسل الصنف", required=True, copy=False, readonly=True, index=True,
                              default=lambda self: _("صنف جديد"))
    # any Onew2many field must have Many2one fields in the corresponding table but not neccessarily vice versa
    category_id = fields.Many2one('new.product.category')
    item_img = fields.Image("صورة الصنف")
    item_image = fields.Binary(string='صورة الصنف')
    item_name = fields.Char(string='اسم الصنف', required=False, tracking=True)  # name of food item inside the menu
    item_description = fields.Text(string='صنف الصنف')


    # item_price = fields.Float(string='سعر الوحده', required=True)  # price of food item inside the menu
    # quantity = fields.Float(string="الكمية", default=lambda self: _(0), store=True)
    # sale_item_subtotal = fields.Float(string="اجمالي حساب الصنف", default=lambda self: _(0), store=True)#, compute='_compute_sale_subtotal_total_credit')
    # sale_order_test = fields.Many2one('combined.sale.order', string='test')
    # sale_order_test2 = fields.One2many('combined.sale.order', 'sale_item_test2', string='test')
    # item_category = fields.Selection([
    #     ('salted pie', 'فطير حادق'),
    #     ('sweetened pie', 'فطير حلو'),
    #     ('sandwich', 'ساندويتش'),
    #     ('appetizer', 'اضافات'),
    # ], required=False, string="نوع الصنف")
    # no_of_orders_per_month = fields.Float(string='عدد الطلبات في الشهر', required=False)
    # note = fields.Text(string='وصف الصنف')


    # @api.model
    # def create(self, vals):  # save button in the form view
    #     # for topping in vals.get('topping_ids_2', []):
    #     #     topping[2].update({'topping_category': 2})
    #     # for topping in vals.get('topping_ids_3', []):
    #     #     topping[2].update({'topping_category': 3})
    #     # if not vals.get('sale_note'):
    #     #     vals['sale_note'] = 'تشرفنا بخدمتك'
    #     if vals.get('item_serial', _('New')) == _('New'):
    #         vals['item_serial'] = self.env['ir.sequence'].next_by_code('new.product.sequence') or _('New')

    #     return super(Product, self).create(vals)