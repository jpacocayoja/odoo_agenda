from odoo import models, fields

class Notificacion(models.Model):
    _name = 'mi_modulo_academico.notificacion'
    _description = 'Notificación'

    estado = fields.Boolean(
        string='Estado', 
        default=False,
        help="Indica si la notificación ha sido leída."
    )
    comunicado_id = fields.Many2one(
        'mi_modulo_academico.comunicado', 
        string='Comunicado', 
        required=True,
        help="Referencia al comunicado asociado a la notificación."
    )
    
    partner_id = fields.Many2one(
        'res.partner', 
        string='Persona', 
        required=True,
        help="Persona a quien va dirigida la notificación."
    )
