from odoo import models, fields

class Profesor(models.Model):
    _name = 'mi_modulo_academico.profesor'
    _description = 'Profesor'

    profesor_id = fields.Many2one('res.partner', string='Profesor', required=True)
