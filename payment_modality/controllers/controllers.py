# -*- coding: utf-8 -*-
# from odoo import http


# class Custom/addons/paymentModality(http.Controller):
#     @http.route('/custom/addons/payment_modality/custom/addons/payment_modality/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom/addons/payment_modality/custom/addons/payment_modality/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom/addons/payment_modality.listing', {
#             'root': '/custom/addons/payment_modality/custom/addons/payment_modality',
#             'objects': http.request.env['custom/addons/payment_modality.custom/addons/payment_modality'].search([]),
#         })

#     @http.route('/custom/addons/payment_modality/custom/addons/payment_modality/objects/<model("custom/addons/payment_modality.custom/addons/payment_modality"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom/addons/payment_modality.object', {
#             'object': obj
#         })
