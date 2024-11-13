import json
from odoo import http
from odoo.http import request

class HorarioController(http.Controller):
    # Listar todos los horarios (READ - GET)
    @http.route('/api/horarios', type='http', auth='public', methods=['GET'])
    def get_horarios(self):
        try:
            horarios = request.env['mi_modulo_academico.horario'].search([])
            horarios_data = [{
                'id': horario.id,
                'name': horario.name,
                'hora_inicio': horario.hora_inicio,
                'hora_fin': horario.hora_fin
            } for horario in horarios]
            
            response = {
                "status": "success",
                "message": "Horarios obtenidos exitosamente",
                "data": horarios_data
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

    # Obtener un horario por ID (READ - GET)
    @http.route('/api/horarios/<int:horario_id>', type='http', auth='public', methods=['GET'])
    def get_horario(self, horario_id):
        try:
            horario = request.env['mi_modulo_academico.horario'].browse(horario_id)
            if not horario.exists():
                response = {
                    "status": "error",
                    "message": "Horario no encontrado"
                }
                return http.Response(json.dumps(response), status=404, content_type='application/json')

            horario_data = {
                'id': horario.id,
                'name': horario.name,
                'hora_inicio': horario.hora_inicio,
                'hora_fin': horario.hora_fin
            }
            
            response = {
                "status": "success",
                "message": "Horario obtenido exitosamente",
                "data": horario_data
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

    # Crear un nuevo horario (CREATE - POST)
    @http.route('/api/horarios', type='json', auth='public', methods=['POST'])
    def create_horario(self, **post):
        try:
            data = post
            if not data:
                return {
                    "status": "error",
                    "message": "No se recibieron datos JSON válidos."
                }

            required_fields = ['name', 'hora_inicio', 'hora_fin']
            for field in required_fields:
                if field not in data:
                    return {
                        "status": "error",
                        "message": f"El campo {field} es requerido"
                    }

            horario = request.env['mi_modulo_academico.horario'].sudo().create({
                'name': data['name'],
                'hora_inicio': data['hora_inicio'],
                'hora_fin': data['hora_fin']
            })

            return {
                "status": "success",
                "message": "Horario creado exitosamente"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    # Actualizar un horario (UPDATE - PUT)
    @http.route('/api/horarios/<int:horario_id>', type='json', auth='public', methods=['PUT'])
    def update_horario(self, horario_id):
        try:
            horario = request.env['mi_modulo_academico.horario'].browse(horario_id)
            if not horario.exists():
                response = {
                    "status": "error",
                    "message": "Horario no encontrado"
                }
                return http.Response(json.dumps(response), content_type='application/json', status=404)

            data = request.jsonrequest
            horario.write(data)

            response = {
                "status": "success",
                "message": "Horario actualizado exitosamente",
                "data": {
                    'id': horario.id,
                    'name': horario.name,
                    'hora_inicio': horario.hora_inicio,
                    'hora_fin': horario.hora_fin
                }
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), content_type='application/json', status=500)

    # Eliminar un horario (DELETE)
    @http.route('/api/horarios/<int:horario_id>', type='json', auth='public', methods=['DELETE'])
    def delete_horario(self, horario_id):
        try:
            horario = request.env['mi_modulo_academico.horario'].browse(horario_id)
            if not horario.exists():
                response = {
                    "status": "error",
                    "message": "Horario no encontrado"
                }
                return http.Response(json.dumps(response), content_type='application/json', status=404)

            horario.unlink()

            response = {
                "status": "success",
                "message": "Horario eliminado exitosamente"
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), content_type='application/json', status=500)
