# -*- coding: utf-8 -*-
from odoo import models, fields, api

class EcosphereComplianceIssue(models.Model):
    _name = 'ecosphere.compliance.issue'
    _description = 'EcoSphere Compliance Issue'

    audit_id = fields.Many2one('ecosphere.audit', string='Linked Audit')
    severity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Severity', required=True, default='medium')
    description = fields.Text(string='Issue Description', required=True)
    owner_id = fields.Many2one('hr.employee', string='Responsible Owner', required=True)
    due_date = fields.Date(string='Due Date', required=True)
    status = fields.Selection([
        ('open', 'Open'),
        ('resolved', 'Resolved'),
        ('overdue', 'Overdue')
    ], string='Status', default='open')

    @api.model
    def check_overdue_issues(self):
        """Cron function to scan and flag overdue issues."""
        today = fields.Date.today()
        open_issues = self.search([
            ('status', '=', 'open'),
            ('due_date', '<', today)
        ])
        if open_issues:
            open_issues.write({'status': 'overdue'})
            # Auto-flagging logic complete
