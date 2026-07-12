# -*- coding: utf-8 -*-
from odoo import models, fields

class EcosphereEmissionFactor(models.Model):
    _name = 'ecosphere.emission.factor'
    _description = 'EcoSphere Emission Factor'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    factor = fields.Float(string='Factor (kg CO2 / Unit)', required=True)
    unit = fields.Char(string='Unit', required=True)
    category = fields.Selection([
        ('purchase', 'Purchase'),
        ('manufacturing', 'Manufacturing'),
        ('expense', 'Expense'),
        ('fleet', 'Fleet')
    ], string='Category', required=True)
