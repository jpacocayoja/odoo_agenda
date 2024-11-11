import json
from odoo import http
from odoo.http import request

class MateriaController(http.Controller):
    # Listar todas las materias (READ - GET)
    @http.route('/api/materias', type='http', auth='public', methods=['GET'])
    def get_materias(self):
        try:
            materias = request.env['mi_modulo_academico.materia'].search([])
            materias_data = []
            for materia in materias:
                materia_data = {
                    'id': materia.id,
                    'name': materia.name,
                    'curso_id': {
                        'id': materia.curso_id.id,
                        'name': materia.curso_id.name,
                        'nivel': materia.curso_id.nivel,
                        'grado': materia.curso_id.grado,
                        'turno': materia.curso_id.turno
                    } if materia.curso_id else None,
                    'aula_id': {
                        'id': materia.aula_id.id,
                        'name': materia.aula_id.name,
                        'numero': materia.aula_id.numero
                    } if materia.aula_id else None,
                    'horario_id': {
                        'id': materia.horario_id.id,
                        'name': materia.horario_id.name,
                        'hora_inicio': materia.horario_id.hora_inicio,
                        'hora_fin': materia.horario_id.hora_fin
                    } if materia.horario_id else None,
                    'profesor_id': {
                        'id': materia.profesor_id.id,
                        'name': materia.profesor_id.name,
                        'email': materia.profesor_id.email
                    } if materia.profesor_id else None,
                    'boletin_id': {
                        'id': materia.boletin_id.id,
                        'alumno_id': materia.boletin_id.alumno_id.name,
                        'curso_id': materia.boletin_id.curso_id.name,
                        'profesor_id': materia.boletin_id.profesor_id.name
                    } if materia.boletin_id else None,
                }
                materias_data.append(materia_data)

            response = {
                "status": "success",
                "message": "Materias obtenidas exitosamente",
                "data": materias_data
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

    # Obtener una materia por ID (READ - GET)
    @http.route('/api/materias/<int:materia_id>', type='http', auth='public', methods=['GET'])
    def get_materia(self, materia_id):
        try:
            materia = request.env['mi_modulo_academico.materia'].browse(materia_id)
            if not materia.exists():
                response = {
                    "status": "error",
                    "message": "Materia no encontrada"
                }
                return http.Response(json.dumps(response), status=404, content_type='application/json')

            materia_data = {
                'id': materia.id,
                'name': materia.name,
                'curso_id': {
                    'id': materia.curso_id.id,
                    'name': materia.curso_id.name,
                    'nivel': materia.curso_id.nivel,
                    'grado': materia.curso_id.grado,
                    'turno': materia.curso_id.turno
                } if materia.curso_id else None,
                'aula_id': {
                    'id': materia.aula_id.id,
                    'name': materia.aula_id.name,
                    'numero': materia.aula_id.numero
                } if materia.aula_id else None,
                'horario_id': {
                    'id': materia.horario_id.id,
                    'name': materia.horario_id.name,
                    'hora_inicio': materia.horario_id.hora_inicio,
                    'hora_fin': materia.horario_id.hora_fin
                } if materia.horario_id else None,
                'profesor_id': {
                    'id': materia.profesor_id.id,
                    'name': materia.profesor_id.name,
                    'email': materia.profesor_id.email
                } if materia.profesor_id else None,
                'boletin_id': {
                    'id': materia.boletin_id.id,
                    'alumno_id': materia.boletin_id.alumno_id.name,
                    'curso_id': materia.boletin_id.curso_id.name,
                    'profesor_id': materia.boletin_id.profesor_id.name
                } if materia.boletin_id else None,
            }

            response = {
                "status": "success",
                "message": "Materia obtenida exitosamente",
                "data": materia_data
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

    # Actualizar una materia por ID (UPDATE - PUT)
    @http.route('/api/materias/<int:materia_id>', type='json', auth='public', methods=['PUT'])
    def update_materia(self, materia_id, **kwargs):
        try:
            materia = request.env['mi_modulo_academico.materia'].browse(materia_id)
            if not materia.exists():
                response = {
                    "status": "error",
                    "message": "Materia no encontrada"
                }
                return http.Response(json.dumps(response), status=404, content_type='application/json')
            
            # Actualizar los campos de la materia
            materia.write(kwargs)

            response = {
                "status": "success",
                "message": "Materia actualizada exitosamente",
                "data": {
                    "id": materia.id,
                    "name": materia.name
                }
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

    # Eliminar una materia por ID (DELETE - DELETE)
    @http.route('/api/materias/<int:materia_id>', type='http', auth='public', methods=['DELETE'])
    def delete_materia(self, materia_id):
        try:
            materia = request.env['mi_modulo_academico.materia'].browse(materia_id)
            if not materia.exists():
                response = {
                    "status": "error",
                    "message": "Materia no encontrada"
                }
                return http.Response(json.dumps(response), status=404, content_type='application/json')
            
            # Eliminar la materia
            materia.unlink()

            response = {
                "status": "success",
                "message": "Materia eliminada exitosamente"
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')
