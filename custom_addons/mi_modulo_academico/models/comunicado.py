from odoo import models, fields

class Comunicado(models.Model):
    _name = 'mi_modulo_academico.comunicado'
    _description = 'Comunicado'

    titulo = fields.Char(string='Título', required=True)
    descripcion = fields.Text(string='Descripción', required=True)
    enlace = fields.Char(string='Enlace URL')  # Campo para almacenar un enlace URL
    archivo = fields.Binary(string='Archivo Adjunto')  # Campo para subir archivos
    archivo_nombre = fields.Char(string="Nombre del Archivo")  # Nombre del archivo
    alumno_id = fields.Many2one('res.partner', string='Alumno')
    curso_ids = fields.One2many('mi_modulo_academico.curso', 'comunicado_id', string='Cursos')
    





