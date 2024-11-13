import json
from odoo import http
from odoo.http import request

class AsistenciaController(http.Controller):
    
    # Listar todas las asistencias (READ - GET)
    @http.route('/api/asistencias', type='http', auth='public', methods=['GET'])
    def get_asistencias(self):
        try:
            asistencias = request.env['mi_modulo_academico.asistencia'].search([])
            asistencias_data = [{
                'id': asistencia.id,
                'fecha': asistencia.fecha.isoformat() if asistencia.fecha else None,
                'alumno': {
                    'id': asistencia.alumno_id.id,
                    'nombre': asistencia.alumno_id.name,
                    'email': asistencia.alumno_id.email,
                    'telefono': asistencia.alumno_id.phone
                } if asistencia.alumno_id else None,
                'profesor': {
                    'id': asistencia.profesor_id.id,
                    'nombre': asistencia.profesor_id.name,
                    'email': asistencia.profesor_id.email,
                    'telefono': asistencia.profesor_id.phone
                } if asistencia.profesor_id else None,
            } for asistencia in asistencias]
            
            response = {
                "status": "success",
                "message": "Asistencias obtenidas exitosamente",
                "data": asistencias_data
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

    # Obtener una asistencia por ID (READ - GET)
    @http.route('/api/asistencias/<int:asistencia_id>', type='http', auth='public', methods=['GET'])
    def get_asistencia(self, asistencia_id):
        try:
            asistencia = request.env['mi_modulo_academico.asistencia'].browse(asistencia_id)
            if not asistencia.exists():
                response = {
                    "status": "error",
                    "message": "Asistencia no encontrada"
                }
                return http.Response(json.dumps(response), status=404, content_type='application/json')

            asistencia_data = {
                'id': asistencia.id,
                'fecha': asistencia.fecha.isoformat() if asistencia.fecha else None,
                'alumno': {
                    'id': asistencia.alumno_id.id,
                    'nombre': asistencia.alumno_id.name,
                    'email': asistencia.alumno_id.email,
                    'telefono': asistencia.alumno_id.phone
                } if asistencia.alumno_id else None,
                'profesor': {
                    'id': asistencia.profesor_id.id,
                    'nombre': asistencia.profesor_id.name,
                    'email': asistencia.profesor_id.email,
                    'telefono': asistencia.profesor_id.phone
                } if asistencia.profesor_id else None,
            }
            
            response = {
                "status": "success",
                "message": "Asistencia obtenida exitosamente",
                "data": asistencia_data
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')
