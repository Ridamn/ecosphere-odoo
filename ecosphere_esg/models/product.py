# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    esg_carbon_footprint = fields.Float(string='Carbon Footprint (kg CO2)')
    esg_recycled_content = fields.Float(string='Recycled Content (%)')
    esg_recyclability_rate = fields.Float(string='Recyclability Rate (%)')
