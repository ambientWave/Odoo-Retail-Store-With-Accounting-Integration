from odoo import api, fields, models, _

class ProductCategory(models.Model):
    _name = "new.product.category"  # name of odoo business model that refers to restaurant menu. The dot delimiter is replaced by
    # underscore in some fields inside csv files
    # _inherit = ["mail.thread"]
    _description = "Menu Item Category"
    _rec_name = "item_category"

    item_category = fields.Selection([
    ('salted pie', 'مشروبات'),
    ('sweetened pie', 'اكياس ومعلبات'),
    ('sandwich', 'بقالة'),
    ('appetizer', 'مثلجات'),
], required=False, string="نوع الصنف")
