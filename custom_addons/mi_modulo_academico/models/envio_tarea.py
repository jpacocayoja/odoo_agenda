from odoo import models, fields

class EnvioTarea(models.Model):
    _name = 'mi_modulo_academico.envio_tarea'
    _description = 'Envio de Tarea'

    tarea_id = fields.Many2one('mi_modulo_academico.tarea', string='Tarea', required=True)  # Relación con la tarea
    alumno_id = fields.Many2one('res.partner', string='Alumno', required=True)  # Alumno que envía la tarea
    fecha_envio = fields.Datetime(string='Fecha de Envío', default=fields.Datetime.now)  # Fecha de envío de la tarea
    archivo_envio = fields.Binary(string='Archivo Enviado')  # Archivo enviado por el alumno
    archivo_nombre = fields.Char(string="Nombre del Archivo")  # Nombre del archivo enviado
    estado = fields.Selection([('pendiente', 'Pendiente'), ('enviado', 'Enviado')], string='Estado', default='pendiente')  # Estado del envío
