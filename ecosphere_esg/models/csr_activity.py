# -*- coding: utf-8 -*-
from odoo import models, fields

class EcosphereCsrActivity(models.Model):
    _name = 'ecosphere.csr.activity'
    _description = 'EcoSphere CSR Activity'

    title = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    category_id = fields.Many2one('ecosphere.category', string='Category', domain="[('type', '=', 'csr')]")
    date = fields.Date(string='Date', required=True)
    points_value = fields.Integer(string='Points Value', required=True, default=50)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed')
    ], string='Status', default='draft')
