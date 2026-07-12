# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EcosphereErpRecord(models.Model):
    _name = 'ecosphere.erp.record'
    _description = 'EcoSphere ERP Record'

    type = fields.Selection([
        ('purchase', 'Purchase'),
        ('manufacturing', 'Manufacturing'),
        ('expense', 'Expense'),
        ('fleet', 'Fleet')
    ], string='Record Type', required=True)
    description = fields.Char(string='Description')
    amount = fields.Float(string='Amount', required=True)
    unit = fields.Char(string='Unit', required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    emission_factor_id = fields.Many2one('ecosphere.emission.factor', string='Emission Factor')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('processed', 'Processed')
    ], string='Status', default='pending')

    def action_process_record(self):
        for record in self:
            if record.status == 'processed':
                continue
            
            # Check config settings
            auto_calc = self.env['ir.config_parameter'].sudo().get_param('ecosphere.auto_emission_calculation', default='True')
            
            if auto_calc == 'True' and record.emission_factor_id:
                emissions = record.amount * record.emission_factor_id.factor
                
                # Create Carbon Transaction
                self.env['ecosphere.carbon.transaction'].create({
                    'transaction_date': record.date,
                    'department_id': record.department_id.id,
                    'source_type': record.type,
                    'source_reference': str(record.id),
                    'activity_amount': record.amount,
                    'emission_factor_id': record.emission_factor_id.id,
                    'calculated_emissions': emissions,
                })
            
            record.status = 'processed'
