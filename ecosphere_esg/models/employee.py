# -*- coding: utf-8 -*-
from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    esg_xp = fields.Integer(string='ESG XP', default=0)
    esg_points = fields.Integer(string='ESG Points Balance', default=0)
    esg_badge_ids = fields.Many2many('ecosphere.badge', 'employee_badge_rel', 'employee_id', 'badge_id', string='Unlocked Badges')
