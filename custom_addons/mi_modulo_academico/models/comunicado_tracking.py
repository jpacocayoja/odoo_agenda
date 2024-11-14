from odoo import models, fields, api
from datetime import datetime
import pytz

class ComunicadoTracking(models.Model):
    _name = 'mi_modulo_academico.comunicado_tracking'
    _description = 'Seguimiento de Lectura de Comunicados'
    _rec_name = 'comunicado_id'
    
    comunicado_id = fields.Many2one(
        'mi_modulo_academico.comunicado', 
        string='Comunicado',
        required=True,
        ondelete='cascade'  # Si se elimina el comunicado, se elimina el tracking
    )
    persona_id = fields.Many2one(
        'res.partner', 
        string='Persona', 
        required=True
    )
    fecha_lectura = fields.Datetime(string='Fecha de Lectura')
    leido = fields.Boolean(string='Leído', default=False)
    tipo_destinatario = fields.Selection([
        ('estudiante', 'Estudiante'),
        ('padre', 'Padre')
    ], string='Tipo de Destinatario', required=True)
    
    _sql_constraints = [
        ('unique_comunicado_persona', 
         'unique(comunicado_id, persona_id)', 
         'Ya existe un registro de seguimiento para esta persona y comunicado.')
    ]