from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied
import json

class UsuarioController(http.Controller):

    @http.route('/api/login', type='json', auth='public', methods=['POST'])
    def verificar_usuario(self, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        
        if not email or not password:
            return {'status': 'error', 'message': 'Faltan parámetros: email y password son requeridos'}

        usuario = request.env['mi_modulo_academico.usuario'].sudo().search([('email', '=', email)], limit=1)
        
        if not usuario:
            return {'status': 'error', 'message': 'Usuario no encontrado'}

        if usuario.check_password(password):
            return {
                'status': 'success',
                'message': 'Autenticación exitosa',
                'usuario_id': usuario.partner_id.id,
                'nombre': usuario.partner_id.name,
                'rol': usuario.rol
            }
        else:
            return {'status': 'error', 'message': 'Contraseña incorrecta'}
