from odoo import models, fields

class Tarea(models.Model):
    _name = 'mi_modulo_academico.tarea'
    _description = 'Tarea'

    unidad = fields.Char(string='Unidad', required=True)
    tema = fields.Text(string='Tema', required=True)
    enlace = fields.Char(string='Enlace URL')  # Campo para almacenar un enlace URL
    archivo = fields.Binary(string='Archivo Adjunto')  # Campo para subir archivos
    archivo_nombre = fields.Char(string="Nombre del Archivo")  # Nombre del archivo
    materia_id = fields.Many2one('mi_modulo_academico.materia', string='Materia', required=True)
    
    # Relación One2many para ver los envíos de tarea de los alumnos
    envio_tarea_ids = fields.One2many('mi_modulo_academico.envio_tarea', 'tarea_id', string='Envíos de Tarea')
    





