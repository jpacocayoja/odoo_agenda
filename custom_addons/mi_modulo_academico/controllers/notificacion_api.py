from odoo import http
from odoo.http import request
import json

class NotificacionController(http.Controller):

    # Listar todas las notificacion (READ - GET)
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
                'comunicado_id': notificacion.comunicado_id.id,      
                'persona_id': notificacion.persona_id,
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
