# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class Lead2OpportunityPartner(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'
    
    def _action_convert(self):
        res = super(Lead2OpportunityPartner, self)._action_convert()
        if self.lead_id:
            body="<p>Bonjour,</p><br><p>La piste <strong>%s</strong> est devenu une opportunité</p><p>Vous pouvez consultez vos opportunitées sur votre espace client <a href='https://tahitilogistiqueservices.odoo.com/my/home'>ici</a>" % self.lead_id.name
            vals = {
                'subject': 'Votre piste [%s] du %s est passé en opportunité' % (self.lead_id.name,self.lead_id.create_date.date()),
                'body_html': body,
                'email_to': self.lead_id.partner_id.email_formatted,
                'auto_delete': False,
                'email_from': self.lead_id.user_id.email_formatted,
            }
            mail_id = self.env['mail.mail'].sudo().create(vals)
            mail_id.sudo().send()
        return res