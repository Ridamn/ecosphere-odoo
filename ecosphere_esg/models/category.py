# -*- coding: utf-8 -*-
from odoo import models, fields

class EcosphereCategory(models.Model):
    _name = 'ecosphere.category'
    _description = 'EcoSphere Category'

    name = fields.Char(string='Name', required=True)
    type = fields.Selection([
        ('csr', 'CSR Activity'),
        ('challenge', 'Challenge')
    ], string='Type', required=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], string='Status', default='active')
