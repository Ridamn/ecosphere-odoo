# -*- coding: utf-8 -*-
from odoo import models, fields

class EcosphereEnvironmentalGoal(models.Model):
    _name = 'ecosphere.environmental.goal'
    _description = 'EcoSphere Environmental Goal'

    title = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    target_value = fields.Float(string='Target Value', required=True)
    current_value = fields.Float(string='Current Value', default=0.0)
    unit = fields.Char(string='Unit', required=True)
    deadline = fields.Date(string='Deadline', required=True)
    status = fields.Selection([
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('achieved', 'Achieved')
    ], string='Status', default='on_track')
