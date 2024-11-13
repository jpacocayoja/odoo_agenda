from odoo import models, fields

class Notificacion(models.Model):
    _name = 'mi_modulo_academico.notificacion'
    _description = 'Notificación'

    estado = fields.Boolean(string='Leido', default=False,help="Indica si la notificación ha sido leída."
    )   
     
    comunicado_id = fields.Many2one('mi_modulo_academico.comunicado', string='Comunicado',
        required=True,
        help="Referencia al comunicado asociado a la notificación."
    )
    
    persona_nombre = fields.Char(string='Persona', required=True)
    
    persona_id = fields.Integer(
        string='ID de Contacto',
        required=True
    )
    
   
    
    
    
    
