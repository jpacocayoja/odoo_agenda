from odoo import models, fields

class BoletinAlumno(models.Model):
    _name = 'mi_modulo_academico.boletin_alumno'
    _description = 'Boletín de Alumno'

    alumno_id = fields.Many2one('res.partner', string='Alumno', required=True)
    curso_id = fields.Many2one('mi_modulo_academico.curso', string='Curso', required=True)
    profesor_id = fields.Many2one('mi_modulo_academico.profesor', string='Profesor', required=True)

    # Obtener las materias relacionadas con el curso mediante un campo related
    materia_ids = fields.One2many(
        related='curso_id.materia_ids',
        string='Materias',
        readonly=True
    )

    nota_ids = fields.One2many('mi_modulo_academico.nota_alumno', 'boletin_id', string='Notas')