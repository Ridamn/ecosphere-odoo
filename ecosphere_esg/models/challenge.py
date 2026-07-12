# -*- coding: utf-8 -*-
from odoo import models, fields

class EcosphereChallenge(models.Model):
    _name = 'ecosphere.challenge'
    _description = 'EcoSphere Challenge'

    title = fields.Char(string='Title', required=True)
    category_id = fields.Many2one('ecosphere.category', string='Category', domain="[('type', '=', 'challenge')]")
    description = fields.Text(string='Description')
    xp = fields.Integer(string='XP Value', required=True, default=100)
    difficulty = fields.Selection([
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ], string='Difficulty', default='easy')
    evidence_required = fields.Boolean(string='Evidence Required', default=True)
    deadline = fields.Date(string='Deadline', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('under_review', 'Under Review'),
        ('completed', 'Completed'),
        ('archived', 'Archived')
    ], string='Status', default='draft')
