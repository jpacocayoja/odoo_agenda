from odoo import models, fields

class Token(models.Model):
    _name = 'mi_modulo_academico.token'
    _description = 'Token'

    token = fields.Char(string='Token', required=True)
    persona_id = fields.Many2one('res.partner', string='Persona', ondelete='cascade')

