# -*- coding: utf-8 -*-
from odoo import models, fields

class EcospherePolicyAcknowledgement(models.Model):
    _name = 'ecosphere.policy.acknowledgement'
    _description = 'EcoSphere Policy Acknowledgement'
    _sql_constraints = [
        ('uniq_employee_policy', 'unique(employee_id, policy_id)', 'Employee has already acknowledged this policy.')
    ]

    policy_id = fields.Many2one('ecosphere.esg.policy', string='ESG Policy', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    acknowledgement_date = fields.Datetime(string='Acknowledgement Date', default=fields.Datetime.now, required=True)
