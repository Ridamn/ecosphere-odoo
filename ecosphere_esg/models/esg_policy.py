# -*- coding: utf-8 -*-
from odoo import models, fields

class EcosphereEsgPolicy(models.Model):
    _name = 'ecosphere.esg.policy'
    _description = 'EcoSphere ESG Policy'

    title = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    category = fields.Selection([
        ('environmental', 'Environmental'),
        ('social', 'Social'),
        ('governance', 'Governance')
    ], string='Category', required=True)
    effective_date = fields.Date(string='Effective Date', required=True)
    version = fields.Char(string='Version', default='1.0', required=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('archived', 'Archived')
    ], string='Status', default='active')
