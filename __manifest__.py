# -*- coding: utf-8 -*-
{
    'name': "Product Attribute Code Extension",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Kendroo Limited",
    'website': "https://kendroo.io/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'product_barcode_36_labels'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_attribute_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
