from odoo import models, fields, api

class Comunicado(models.Model):
    _name = 'mi_modulo_academico.comunicado'
    _description = 'Comunicado'

    titulo = fields.Char(string='Título', required=True)
    descripcion = fields.Text(string='Descripción', required=True)
    enlace = fields.Char(string='Enlace URL')  # Campo para almacenar un enlace URL
    archivo = fields.Binary(string='Archivo Adjunto')  # Campo para subir archivos
    archivo_nombre = fields.Char(string="Nombre del Archivo")  # Nombre del archivo
    persona_id = fields.Many2one('res.partner', string='Persona')  # Persona asociada al comunicado

    @api.model
    def create(self, vals):
        # Crear el registro del comunicado
        comunicado = super(Comunicado, self).create(vals)
        
        # Verificar que el comunicado tiene un `persona_id` para crear la notificación
        if comunicado.persona_id:
            # Crear el registro de notificación relacionado
            self.env['mi_modulo_academico.notificacion'].create({
                'estado': False,  # Estado inicial de la notificación
                'comunicado_id': comunicado.id,
                'persona_id': comunicado.persona_id.id,  # ID de la persona
                'persona_nombre': comunicado.persona_id.name  # Nombre de la persona
            })
        
        return comunicado





