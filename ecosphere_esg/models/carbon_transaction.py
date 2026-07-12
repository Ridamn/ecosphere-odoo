# -*- coding: utf-8 -*-
from odoo import models, fields

class EcosphereCarbonTransaction(models.Model):
    _name = 'ecosphere.carbon.transaction'
    _description = 'EcoSphere Carbon Transaction'

    transaction_date = fields.Date(string='Date', required=True, default=fields.Date.today)
    department_id = fields.Many2one('hr.department', string='Department')
    source_type = fields.Selection([
        ('purchase', 'Purchase'),
        ('manufacturing', 'Manufacturing'),
        ('expense', 'Expense'),
        ('fleet', 'Fleet'),
        ('manual', 'Manual')
    ], string='Source', required=True)
    source_reference = fields.Char(string='Source Reference')
    activity_amount = fields.Float(string='Activity Amount', required=True)
    emission_factor_id = fields.Many2one('ecosphere.emission.factor', string='Emission Factor')
    calculated_emissions = fields.Float(string='Calculated Emissions (kg CO2)', required=True)
