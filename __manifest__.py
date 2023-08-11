# -*- coding: utf-8 -*-

{
    'name': 'بقالة الرحمة',
    'version': '1.0',
    'sequence': -102,
    'category': 'Accounting/Accounting',
    'summary': '',
    'description': """
نظام ادارة المتجر يتكون من جزء لادارة البضاعة والمشتريات وجزء لادارة المبيعات.
    """,
    'depends': ['sales_team', 'payment', 'portal', 'utm', 'sale', 'mail', 'crm', 'l10n_co',
                'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        # 'wizard/remove_invoice_views.xml',
        'views/new_retail_order_views.xml',
        # 'views/pos_combined.xml',
        # 'views/BackendAssets.xml',
        # 'views/custom_pos_template.xml',
        # 'views/inventory_stock.xml',
        # 'report/report_sale_receipt_template.xml',
        # 'report/report.xml',
             ],
    'qweb': [
        # 'static/src/xml/custom_pos.xml',
        # 'static/src/xml/myButton.xml',
        # 'static/src/xml/currencyExRatesPopup.xml',
        # 'static/src/xml/AddButtonToPOSDashboardOrdersListView.xml'
            ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
