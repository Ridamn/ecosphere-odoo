# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EcosphereChallengeParticipation(models.Model):
    _name = 'ecosphere.challenge.participation'
    _description = 'EcoSphere Challenge Participation'
    _sql_constraints = [
        ('uniq_employee_challenge', 'unique(employee_id, challenge_id)', 'Employee is already registered for this Challenge.')
    ]

    challenge_id = fields.Many2one('ecosphere.challenge', string='Challenge', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    progress = fields.Integer(string='Progress (%)', default=0)
    proof_file = fields.Char(string='Proof file/link')
    approval_status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Approval Status', default='pending')
    xp_awarded = fields.Integer(string='XP Awarded', default=0)
    completion_date = fields.Date(string='Completion Date')

    def action_approve_participation(self):
        for record in self:
            if record.approval_status == 'approved':
                continue
            
            # Check evidence required toggle
            if record.challenge_id.evidence_required and not record.proof_file:
                raise ValidationError("Proof file/description is required to approve this challenge completion.")
                
            record.write({
                'approval_status': 'approved',
                'xp_awarded': record.challenge_id.xp,
                'completion_date': fields.Date.today()
            })
            
            # Award XP & points to employee
            record.employee_id.esg_xp += record.challenge_id.xp
            record.employee_id.esg_points += record.challenge_id.xp
            
            # Auto-award badges
            self._check_badges(record.employee_id)

    def action_reject_participation(self):
        for record in self:
            record.approval_status = 'rejected'

    def _check_badges(self, employee):
        badge_award = self.env['ir.config_parameter'].sudo().get_param('ecosphere.badge_auto_award', default='True')
        if badge_award != 'True':
            return
            
        challenge_count = self.search_count([
            ('employee_id', '=', employee.id),
            ('approval_status', '=', 'approved'),
            ('progress', '=', 100)
        ])
        
        # Check matching badges not already unlocked
        badges = self.env['ecosphere.badge'].search([
            ('metric', '=', 'challenges'),
            ('threshold', '<=', challenge_count),
            ('id', 'not in', employee.esg_badge_ids.ids)
        ])
        
        # Also check general XP badges
        xp_badges = self.env['ecosphere.badge'].search([
            ('metric', '=', 'xp'),
            ('threshold', '<=', employee.esg_xp),
            ('id', 'not in', employee.esg_badge_ids.ids)
        ])
        
        target_badges = badges + xp_badges
        if target_badges:
            employee.esg_badge_ids = [(4, b.id) for b in target_badges]
