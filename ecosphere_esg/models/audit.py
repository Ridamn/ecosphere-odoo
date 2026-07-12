# -*- coding: utf-8 -*-
from odoo import models, fields

class EcosphereAudit(models.Model):
    _name = 'ecosphere.audit'
    _description = 'EcoSphere Internal Audit'

    title = fields.Char(string='Title', required=True)
    scope = fields.Char(string='Scope')
    auditor = fields.Char(string='Auditor Organization', required=True)
    audit_date = fields.Date(string='Audit Date', required=True, default=fields.Date.today)
    score = fields.Float(string='Score (%)', required=True, default=100.0)
    findings = fields.Text(string='Findings & Recommendations')
    status = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='planned')
