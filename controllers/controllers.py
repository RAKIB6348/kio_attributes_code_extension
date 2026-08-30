# -*- coding: utf-8 -*-
# from odoo import http


# class KioAttributesCodeExtension(http.Controller):
#     @http.route('/kio_attributes_code_extension/kio_attributes_code_extension', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/kio_attributes_code_extension/kio_attributes_code_extension/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('kio_attributes_code_extension.listing', {
#             'root': '/kio_attributes_code_extension/kio_attributes_code_extension',
#             'objects': http.request.env['kio_attributes_code_extension.kio_attributes_code_extension'].search([]),
#         })

#     @http.route('/kio_attributes_code_extension/kio_attributes_code_extension/objects/<model("kio_attributes_code_extension.kio_attributes_code_extension"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('kio_attributes_code_extension.object', {
#             'object': obj
#         })

