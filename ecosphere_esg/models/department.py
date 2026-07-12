# -*- coding: utf-8 -*-
from odoo import models, fields

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    esg_env_score = fields.Float(string='Environmental Score', default=100.0)
    esg_soc_score = fields.Float(string='Social Score', default=100.0)
    esg_gov_score = fields.Float(string='Governance Score', default=100.0)
    esg_total_score = fields.Float(string='Total ESG Score', default=100.0)
