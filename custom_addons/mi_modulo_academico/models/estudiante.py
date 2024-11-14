from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Estudiante(models.Model):
    _name = 'mi_modulo_academico.estudiante'
    _description = 'Estudiante'
    _rec_name = 'partner_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Campos relacionados con la persona/usuario
    partner_id = fields.Many2one('res.partner', string='Estudiante', required=True, tracking=True)
    usuario_id = fields.Many2one('mi_modulo_academico.usuario', string='Usuario',
                                domain=[('rol', '=', 'estudiante')],
                                tracking=True)
    
    # Campos académicos
    curso_id = fields.Many2one('mi_modulo_academico.curso', string='Curso', 
                              required=True, tracking=True)
    materia_ids = fields.Many2many(
        'mi_modulo_academico.materia',
        'estudiante_materia_rel',
        'estudiante_id',
        'materia_id',
        string='Materias',
        tracking=True
    )
    
    # Campos para profesores
    profesor_asignado_ids = fields.Many2many(
        'mi_modulo_academico.usuario',
        'estudiante_profesor_asignado_rel',
        'estudiante_id',
        'profesor_id',
        string='Profesores Asignados',
        domain=[('rol', '=', 'profesor')],
        tracking=True
    )
    profesor_ids = fields.Many2many(
        'mi_modulo_academico.usuario',
        'estudiante_profesor_rel',
        'estudiante_id',
        'profesor_id',
        string='Todos los Profesores',
        compute='_compute_profesores',
        store=True
    )
    
    # Campos de control
    active = fields.Boolean(default=True, tracking=True)
    
    @api.depends('materia_ids.profesor_id', 'profesor_asignado_ids')
    def _compute_profesores(self):
        """Calcula todos los profesores (de materias y asignados directamente)"""
        for estudiante in self:
            # Obtener profesores de las materias
            profesor_materias = self.env['mi_modulo_academico.usuario'].search([
                ('rol', '=', 'profesor'),
                ('partner_id', 'in', estudiante.materia_ids.mapped('profesor_id').ids)
            ])
            # Combinar con profesores asignados directamente
            estudiante.profesor_ids = profesor_materias | estudiante.profesor_asignado_ids

    @api.constrains('usuario_id')
    def _check_usuario_estudiante(self):
        """Verifica que el usuario asignado tenga rol de estudiante"""
        for record in self:
            if record.usuario_id and record.usuario_id.rol != 'estudiante':
                raise ValidationError("El usuario debe tener rol de estudiante")

    @api.constrains('profesor_asignado_ids')
    def _check_profesor_asignado(self):
        """Verifica que los profesores asignados tengan rol de profesor"""
        for record in self:
            for profesor in record.profesor_asignado_ids:
                if profesor.rol != 'profesor':
                    raise ValidationError(f"El usuario {profesor.partner_id.name} debe tener rol de profesor")

    @api.model
    def create(self, vals):
        """Sobrescribe el método create para validaciones adicionales"""
        # Verificar si ya existe un estudiante con el mismo partner_id
        if vals.get('partner_id'):
            existing = self.search([('partner_id', '=', vals['partner_id'])])
            if existing:
                raise ValidationError("Ya existe un estudiante registrado para esta persona")
        return super(Estudiante, self).create(vals)

    def write(self, vals):
        """Sobrescribe el método write para validaciones adicionales"""
        if vals.get('partner_id'):
            existing = self.search([
                ('partner_id', '=', vals['partner_id']),
                ('id', '!=', self.id)
            ])
            if existing:
                raise ValidationError("Ya existe un estudiante registrado para esta persona")
        return super(Estudiante, self).write(vals)