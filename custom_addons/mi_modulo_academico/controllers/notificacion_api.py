from odoo import http
from odoo.http import request
import json

class NotificacionController(http.Controller):

    # Listar todas las notificaciones (READ - GET)
    @http.route('/api/notificacion', type='http', auth='public', methods=['GET'])
    def get_notificaciones(self):
        try:
            # Obtener todas las notificaciones
            notificaciones = request.env['mi_modulo_academico.notificacion'].sudo().search([])

            # Construir la respuesta
            notificaciones_data = [{
                'id': notificacion.id,
                'estado': notificacion.estado,
                'persona_nombre': notificacion.persona_nombre,
                'comunicado_id': {
                    'id': notificacion.comunicado_id.id,
                    'titulo': notificacion.comunicado_id.titulo
                } if notificacion.comunicado_id else None,
                'persona_id': {
                    'id': notificacion.persona_id.id,
                    'name': notificacion.persona_id.name
                } if notificacion.persona_id else None,
            } for notificacion in notificaciones]

            response = {
                "status": "success",
                "message": "Notificaciones obtenidas exitosamente",
                "data": notificaciones_data
            }
            return http.Response(json.dumps(response), content_type='application/json')

        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

    # Listar todas las notificaciones por persona_id (READ - GET)
    @http.route('/api/notificacion/persona/<int:persona_id>', type='http', auth='public', methods=['GET'])
    def get_notificaciones_por_persona(self, persona_id):
        try:
            # Filtrar las notificaciones por persona_id
            notificaciones = request.env['mi_modulo_academico.notificacion'].sudo().search([
                ('persona_id', '=', persona_id)
            ])

            # Construir la respuesta
            notificaciones_data = [{
                'id': notificacion.id,
                'estado': notificacion.estado,
                'persona_nombre': notificacion.persona_nombre,
                'comunicado_id': {
                    'id': notificacion.comunicado_id.id,
                    'titulo': notificacion.comunicado_id.titulo,
                    'descripcion': notificacion.comunicado_id.descripcion,
                    'enlace': notificacion.comunicado_id.enlace,
                    'archivo_nombre': notificacion.comunicado_id.archivo_nombre,
                } if notificacion.comunicado_id else None,
                'persona_id': {
                    'id': notificacion.persona_id.id,
                    'name': notificacion.persona_id.name
                } if notificacion.persona_id else None,
            } for notificacion in notificaciones]

            response = {
                "status": "success",
                "message": "Notificaciones obtenidas exitosamente",
                "data": notificaciones_data
            }
            return http.Response(json.dumps(response), content_type='application/json')

        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

    # Listar todas las notificaciones no leídas por persona_id (READ - GET)
    @http.route('/api/notificacion/persona/<int:persona_id>/estado', type='http', auth='public', methods=['GET'])
    def get_notificaciones_no_leidas_por_persona(self, persona_id):
        try:
            # Filtrar las notificaciones por persona_id y estado no leído (estado=False)
            notificaciones = request.env['mi_modulo_academico.notificacion'].sudo().search([
                ('persona_id', '=', persona_id),
                ('estado', '=', False)
            ])

            # Construir la respuesta
            notificaciones_data = [{
                'id': notificacion.id,
                'estado': notificacion.estado,
                'persona_nombre': notificacion.persona_nombre,
                'comunicado_id': {
                    'id': notificacion.comunicado_id.id,
                    'titulo': notificacion.comunicado_id.titulo,
                    'descripcion': notificacion.comunicado_id.descripcion,
                    'enlace': notificacion.comunicado_id.enlace,
                    'archivo_nombre': notificacion.comunicado_id.archivo_nombre,
                } if notificacion.comunicado_id else None,
                'persona_id': {
                    'id': notificacion.persona_id.id,
                    'name': notificacion.persona_id.name
                } if notificacion.persona_id else None,
            } for notificacion in notificaciones]

            response = {
                "status": "success",
                "message": "Notificaciones no leídas obtenidas exitosamente",
                "data": notificaciones_data
            }
            return http.Response(json.dumps(response), content_type='application/json')

        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

    # Actualizar el estado de una notificación por notificacion_id enviado en el cuerpo de la solicitud (POST)
    @http.route('/api/notificacion/estado', type='json', auth='public', methods=['POST'])
    def update_estado_notificacion(self, **post):
        try:
            data = post
            if not data['notificacion_id']:
                return http.Response(
                    json.dumps({"status": "error", "message": "ID de notificación no proporcionado"}),
                    status=400,
                    content_type='application/json'
                )

            # Obtener la notificación
            notificacion = request.env['mi_modulo_academico.notificacion'].sudo().search([
                ('id', '=', data['notificacion_id'])
            ])
            if not notificacion.exists():
                return http.Response(
                    json.dumps({"status": "error", "message": "Notificación no encontrada"}),
                    status=404,
                    content_type='application/json'
                )

            # Actualizar el estado de la notificación
            notificacion.write({'estado': True})

            # Guardar los cambios
            request.env.cr.commit()

            response = {
                "status": "success",
                "message": "Estado de notificación actualizado exitosamente"
            }
            return response

        except Exception as e:
            return http.Response(
                json.dumps({"status": "error", "message": str(e)}),
                status=500,
                content_type='application/json'
            )