# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models


class InventoryStock(models.Model):
    _name = "inventory.stock"
    # _inherit = "product.template"  # name of odoo business model that refers to inventory stock. The dot delimiter is replaced by
    # underscore in some fields inside csv files
    _rec_name = "stock_name"
    _description = "Stock inventory"

    stock_name = fields.Char(string='اسم الصنف', required=True)  # name of stock item
    stock_price = fields.Float(string='سعر شراء الوحده بالجنيه', required=True)  # price of stock unit
    stock_qty = fields.Float(string='الكمية بالكيلوجرام', required=True)
    vendor_name = fields.Char(string='اسم المورد', required=True)
    vendor_contact_phone_number = fields.Char(string='رقم التواصل الخاص بالمورد', required=True)
    last_purchase_timestamp = fields.Datetime(string='تاريخ الطلبية/اخر طلبية', required=True, default=datetime.now())
    last_purchase_invoice_serial = fields.Integer(string='مسلسل اخر فاتورة الشراء', required=True)
    accountable_user = fields.Many2one('res.users', string='اسم المستخدم المسؤول', required=True)
    note = fields.Text(string='ملاحظات')
