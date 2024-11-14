from werkzeug.exceptions import BadRequest, NotFound

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
                'persona_id': usuario.partner_id.id,
                'nombre': usuario.partner_id.name,
                'email': usuario.email,
                'rol': usuario.rol
            }
        else:
            return {'status': 'error', 'message': 'Contraseña incorrecta'}

    @http.route('/api/token', type='json', auth='public', methods=['POST'])
    def gestionar_token(self, **kwargs):
        token_value = kwargs.get('token')
        persona_id = kwargs.get('persona_id')

        # Validar que los parámetros requeridos estén presentes
        if not token_value or not persona_id:
            raise BadRequest(description="Faltan parámetros: 'token' y 'persona_id' son requeridos")

        # Buscar si el token ya existe en la base de datos
        Token = request.env['mi_modulo_academico.token'].sudo()
        token_existente = Token.search([('token', '=', token_value)], limit=1)

        # Si el token existe
        if token_existente:
            # Si el token está asociado con la misma persona, no hacer nada
            if token_existente.persona_id.id == persona_id:
                return {
                    'status': 'success',
                    'message': 'El token ya está asociado a la misma persona, no se realizaron cambios.'
                }
            else:
                # Actualizar el `persona_id` asociado con el token existente
                token_existente.persona_id = persona_id
                return {
                    'status': 'success',
                    'message': 'Token existente actualizado con un nuevo persona_id.'
                }
        else:
            # Si el token no existe, crear un nuevo registro de token
            Token.create({
                'token': token_value,
                'persona_id': persona_id
            })
            return {
                'status': 'success',
                'message': 'Token creado y asociado con la persona.'
            }

    # GET general para obtener todos los tokens
    @http.route('/api/tokens', type='http', auth='public', methods=['GET'])
    def get_all_tokens(self):
        try:
            tokens = request.env['mi_modulo_academico.token'].sudo().search([])
            tokens_data = [
                {
                    'token': token.token,
                    'persona_id': token.persona_id.id,
                    'nombre_persona': token.persona_id.name
                }
                for token in tokens
            ]

            response = {
                "status": "success",
                "message": "Tokens obtenidos exitosamente",
                "data": tokens_data
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

    # GET para obtener los tokens asociados a una persona específica
    @http.route('/api/tokens/<int:persona_id>', type='http', auth='public', methods=['GET'])
    def get_tokens_by_persona(self, persona_id):
        try:
            tokens = request.env['mi_modulo_academico.token'].sudo().search([('persona_id', '=', persona_id)])

            # Verificar si hay tokens asociados a la persona
            if not tokens:
                response = {
                    "status": "error",
                    "message": "No se encontraron tokens para esta persona"
                }
                return http.Response(json.dumps(response), status=404, content_type='application/json')

            tokens_data = [
                {
                    'token': token.token,
                    'persona_id': token.persona_id.id,
                    'nombre_persona': token.persona_id.name
                }
                for token in tokens
            ]

            response = {
                "status": "success",
                "message": "Tokens obtenidos exitosamente",
                "data": tokens_data
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')