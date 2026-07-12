# -*- coding: utf-8 -*-
from odoo import models, fields

class EcosphereReward(models.Model):
    _name = 'ecosphere.reward'
    _description = 'EcoSphere Redeemable Reward'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    points_required = fields.Integer(string='Points Required', required=True)
    stock = fields.Integer(string='Stock Count', default=0)
    status = fields.Selection([
        ('active', 'Active'),
        ('out_of_stock', 'Out of Stock')
    ], string='Status', default='active')
