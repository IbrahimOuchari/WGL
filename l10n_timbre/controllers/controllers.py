# -*- coding: utf-8 -*-
from odoo import http

# class L10nTimbre(http.Controller):
#     @http.route('/l10n_timbre/l10n_timbre/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_timbre/l10n_timbre/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_timbre.listing', {
#             'root': '/l10n_timbre/l10n_timbre',
#             'objects': http.request.env['l10n_timbre.l10n_timbre'].search([]),
#         })

#     @http.route('/l10n_timbre/l10n_timbre/objects/<model("l10n_timbre.l10n_timbre"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_timbre.object', {
#             'object': obj
#         })