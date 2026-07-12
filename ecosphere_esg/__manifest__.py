# -*- coding: utf-8 -*-
{
    'name': 'EcoSphere ESG Management',
    'summary': 'Carbon accounting, CSR activities, Audits, Policies and Gamification.',
    'description': """
        EcoSphere ESG Management Platform:
        - Environmental: Carbon transactions, Emission factors, Carbon accounting.
        - Social: CSR Activities, employee volunteering.
        - Governance: Compliance issues, corporate policies, internal audits.
        - Gamification: Challenges, Badge auto-awards, Rewards redemption.
    """,
    'author': 'Omkar Gunde',
    'category': 'Sustainability',
    'version': '1.0',
    'depends': ['base', 'hr', 'product'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/menus.xml',
    ],
    'application': True,
    'installable': True,
}
