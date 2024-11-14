from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import re

class Usuario(models.Model):
    _name = 'mi_modulo_academico.usuario'
    _description = 'Usuario'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    email = fields.Char(string='Correo', required=True, tracking=True)
    password = fields.Char(string='Contraseña', required=True, copy=False)
    rol = fields.Selection(
        [('estudiante', 'Estudiante'), ('padre', 'Padre'), ('profesor', 'Profesor')],
        string='Rol', required=True, tracking=True
    )
    partner_id = fields.Many2one('res.partner', string='Persona', required=True, tracking=True)
    display_name = fields.Char(string='Nombre', compute='_compute_display_name', store=True)
    odoo_user_id = fields.Many2one('res.users', string='Usuario Odoo', readonly=True, tracking=True)


    @api.depends('partner_id.name', 'email', 'rol')
    def _compute_display_name(self):
        for user in self:
            if user.partner_id and user.partner_id.name:
                user.display_name = f'{user.partner_id.name} ({user.email}) - {dict(user._fields["rol"].selection).get(user.rol)}'
            else:
                user.display_name = user.email

    @api.model
    def create(self, vals):
        # Crear el registro de usuario
        record = super(Usuario, self).create(vals)
        
        # Si es profesor o estudiante, crear usuario Odoo
        if record.rol in ['profesor', 'estudiante']:
            record._create_odoo_user(vals.get('password'))

        return record

    def write(self, vals):
        # Guardar la contraseña si está presente
        password = vals.get('password')
        
        result = super(Usuario, self).write(vals)
        
        # Si hay cambio de contraseña y tiene usuario Odoo
        if password:
            for record in self:
                if record.odoo_user_id:
                    record.odoo_user_id.sudo().write({'password': password})
        
        return result

    def _create_odoo_user(self, password):
        """Crear usuario Odoo con los grupos correspondientes"""
        self.ensure_one()
        Users = self.env['res.users'].sudo()
        
        # Verificar si ya existe un usuario con este email
        existing_user = Users.search([('login', '=', self.email)], limit=1)
        if existing_user:
            raise UserError(f'Ya existe un usuario de Odoo con el email {self.email}')

        # Grupos base que todos los usuarios deben tener
        groups = [(4, self.env.ref('mi_modulo_academico.group_mimodulo_academico_user').id)]
        
        # Agregar grupos específicos según el rol
        if self.rol == 'profesor':
            groups.append((4, self.env.ref('mi_modulo_academico.group_profesor').id))
        elif self.rol == 'estudiante':
            groups.append((4, self.env.ref('mi_modulo_academico.group_estudiante').id))

        # Crear usuario Odoo
        values = {
            'name': self.partner_id.name,
            'partner_id': self.partner_id.id,
            'login': self.email,
            'password': password,
            'groups_id': groups + [
                (4, self.env.ref('base.group_user').id),
            ]
        }
        
        try:
            odoo_user = Users.create(values)
            self.odoo_user_id = odoo_user.id
        except Exception as e:
            raise UserError(f"Error al crear usuario Odoo: {str(e)}")

    @api.constrains('email')
    def _check_email(self):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@(gmail\.com|hotmail\.com|outlook\.com)$'
        for record in self:
            if not re.match(email_pattern, record.email):
                raise ValidationError("El correo debe ser una dirección válida de Gmail o Hotmail/Outlook (ejemplo@gmail.com, ejemplo@hotmail.com)")

    def check_password(self, password):
        """Verificar contraseña usando el sistema de Odoo para usuarios con acceso web"""
        self.ensure_one()
        
        if self.odoo_user_id:
            # Para usuarios con acceso web, verificar con el sistema de Odoo
            try:
                self.env['res.users'].sudo()._login(self.env.cr.dbname, self.email, password)
                return True
            except Exception:
                return False
        else:
            # Para usuarios sin acceso web (como padres), usar autenticación simple
            return password == self.password

    def unlink(self):
        """Sobrescribir método unlink para eliminar también el usuario Odoo si existe"""
        for record in self:
            if record.odoo_user_id:
                record.odoo_user_id.sudo().unlink()
        return super(Usuario, self).unlink()