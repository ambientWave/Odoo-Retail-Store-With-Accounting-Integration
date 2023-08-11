from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class ProductItem(models.Model):
    _name = "new.product.item"  # name of odoo business model that refers to restaurant menu. The dot delimiter is replaced by
    # underscore in some fields inside csv files
    # _inherit = ["mail.thread"]
    _description = "Product Item"
    _rec_name = "product_id"

    product_id = fields.Many2one('new.product')
    product_sku = fields.Char(string='مسلسل تخزين الصنف')
    used_unit = fields.Selection([
        ('kg', 'كيلوجرام'),
        ('piece', 'قطعة'),
        ], required=False, string="نوع الوحدة المستخدمة",
        help="ينقسم نوع الوحدة المستخدمة")
    product_qty_in_stock = fields.Float(string='الكمية المتوفرة') #TODO 112,111
    item_price = fields.Float(string='سعر الوحده', required=True)  # price of food item inside the menu