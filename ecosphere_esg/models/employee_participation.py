# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EcosphereEmployeeParticipation(models.Model):
    _name = 'ecosphere.employee.participation'
    _description = 'EcoSphere Employee CSR Participation'
    _sql_constraints = [
        ('uniq_employee_activity', 'unique(employee_id, activity_id)', 'Employee is already registered for this CSR activity.')
    ]

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    activity_id = fields.Many2one('ecosphere.csr.activity', string='CSR Activity', required=True)
    proof_file = fields.Char(string='Proof file/link')
    approval_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Approval Status', default='pending')
    points_earned = fields.Integer(string='Points Earned', default=0)
    completion_date = fields.Date(string='Completion Date')

    def action_approve_participation(self):
        for record in self:
            if record.approval_status == 'approved':
                continue
            
            # Check evidence required toggle
            evidence_req = self.env['ir.config_parameter'].sudo().get_param('ecosphere.evidence_requirement', default='True')
            if evidence_req == 'True' and not record.proof_file:
                raise ValidationError("Proof file is required to approve this CSR participation.")
                
            record.write({
                'approval_status': 'approved',
                'points_earned': record.activity_id.points_value,
                'completion_date': fields.Date.today()
            })
            
            # Award points to employee
            record.employee_id.esg_points += record.activity_id.points_value
            record.employee_id.esg_xp += record.activity_id.points_value
            
            # Auto-award badges
            self._check_badges(record.employee_id)

    def action_reject_participation(self):
        for record in self:
            record.approval_status = 'rejected'

    def _check_badges(self, employee):
        badge_award = self.env['ir.config_parameter'].sudo().get_param('ecosphere.badge_auto_award', default='True')
        if badge_award != 'True':
            return
            
        csr_count = self.search_count([
            ('employee_id', '=', employee.id),
            ('approval_status', '=', 'approved')
        ])
        
        # Check matching badges not already unlocked
        badges = self.env['ecosphere.badge'].search([
            ('metric', '=', 'csr'),
            ('threshold', '<=', csr_count),
            ('id', 'not in', employee.esg_badge_ids.ids)
        ])
        
        if badges:
            employee.esg_badge_ids = [(4, b.id) for b in badges]
            
            # Post a message/notification on employee chatter if mail module is installed
            # For simplicity, we just log it in Odoo.
