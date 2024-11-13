from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
import hashlib
import os

class Usuario(models.Model):
    _name = 'mi_modulo_academico.usuario'
    _description = 'Usuario'

    email = fields.Char(string='Correo', required=True)
    password = fields.Char(string='Contraseña', required=True)
    salt = fields.Char(string='Salt', readonly=True)
    rol = fields.Selection(
        [('estudiante', 'Estudiante'), ('padre', 'Padre'), ('profesor', 'Profesor')],
        string='Rol', required=True
    )
    partner_id = fields.Many2one('res.partner', string='Persona', required=True)

    @api.constrains('email')
    def _check_email(self):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@(gmail\.com|hotmail\.com|outlook\.com)$'
        for record in self:
            if not re.match(email_pattern, record.email):
                raise ValidationError("El correo debe ser una dirección válida de Gmail o Hotmail/Outlook (ejemplo@gmail.com, ejemplo@hotmail.com)")

    def _hash_password(self, password, salt=None):
        if salt is None:
            salt = os.urandom(32).hex()
        
        salted_password = (password + salt).encode('utf-8')
        hashed = hashlib.sha256(salted_password).hexdigest()
        
        return hashed, salt

    @api.model
    def create(self, vals):
        if 'password' in vals:
            hashed_password, salt = self._hash_password(vals['password'])
            vals['password'] = hashed_password
            vals['salt'] = salt
        return super(Usuario, self).create(vals)

    def write(self, vals):
        if 'password' in vals:
            hashed_password, salt = self._hash_password(vals['password'])
            vals['password'] = hashed_password
            vals['salt'] = salt
        return super(Usuario, self).write(vals)

    def check_password(self, password):
        self.ensure_one()
        hashed_attempt, _ = self._hash_password(password, self.salt)
        return hashed_attempt == self.password
