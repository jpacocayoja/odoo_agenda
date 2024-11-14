from odoo import models, fields, api

class Tarea(models.Model):
    _name = 'mi_modulo_academico.tarea'
    _description = 'Tarea'
    _rec_name = 'display_name'

    title = fields.Char(string='Título', required=True)
    unidad = fields.Char(string='Unidad', required=True)
    tema = fields.Text(string='Tema', required=True)
    enlace = fields.Char(string='Enlace URL')
    archivo = fields.Binary(string='Archivo Adjunto')
    archivo_nombre = fields.Char(string="Nombre del Archivo")
    materia_id = fields.Many2one('mi_modulo_academico.materia', string='Materia', required=True)
    
    # Relación One2many para ver los envíos de tarea de los alumnos
    envio_tarea_ids = fields.One2many('mi_modulo_academico.envio_tarea', 'tarea_id', string='Envíos de Tarea')

    # Campo computado para mostrar información más completa
    display_name = fields.Char(string='Nombre Completo', compute='_compute_display_name', store=True)

    @api.depends('title', 'unidad', 'tema', 'materia_id')
    def _compute_display_name(self):
        for record in self:
            materia_name = record.materia_id.name if record.materia_id else ''
            record.display_name = f'[{materia_name}] {record.title} - {record.unidad}'