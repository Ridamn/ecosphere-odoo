# -*- coding: utf-8 -*-
from odoo import models, fields

class EcosphereBadge(models.Model):
    _name = 'ecosphere.badge'
    _description = 'EcoSphere Badge'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description', required=True)
    unlock_rule = fields.Char(string='Unlock Rule')
    metric = fields.Selection([
        ('xp', 'XP'),
        ('challenges', 'Completed Challenges'),
        ('csr', 'CSR Participations')
    ], string='Unlock Metric', required=True)
    threshold = fields.Integer(string='Threshold Value', required=True)
    icon = fields.Char(string='Icon (Emoji/Class)', default='🌱')
