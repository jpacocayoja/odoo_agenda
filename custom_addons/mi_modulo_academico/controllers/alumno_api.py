import json
from odoo import http
from odoo.http import request

class AlumnoController(http.Controller):
    @http.route('/api/alumno/<int:alumno_id>/detalles', type='http', auth='public', methods=['GET'])
    def get_detalles_alumno(self, alumno_id):
        try:
            # Buscar el boletín del alumno con el `alumno_id` proporcionado
            boletin = request.env['mi_modulo_academico.boletin_alumno'].sudo().search([('alumno_id', '=', alumno_id)], limit=1)

            if not boletin:
                response = {
                    "status": "error",
                    "message": "No se encontraron detalles para este alumno"
                }
                return http.Response(json.dumps(response), status=404, content_type='application/json')

            # Recopilar los detalles del curso, profesor, horario, aula y materias
            curso = boletin.curso_id
            profesor = boletin.profesor_id
            materias_data = []
            for materia in curso.materia_ids:
                materia_data = {
                    'id': materia.id,
                    'nombre': materia.name,
                    'horario': {
                        'id': materia.horario_id.id,
                        'nombre': materia.horario_id.name
                    } if materia.horario_id else None,
                    'aula': {
                        'id': materia.aula_id.id,
                        'nombre': materia.aula_id.name,
                        'numero': materia.aula_id.numero
                    } if materia.aula_id else None,
                    'profesor': {
                        'id': materia.profesor_id.id,
                        'nombre': materia.profesor_id.name
                    } if materia.profesor_id else None
                }
                materias_data.append(materia_data)

            # Estructura de respuesta con los detalles completos
            detalles_data = {
                'curso': {
                    'id': curso.id,
                    'nombre': curso.name,
                    'nivel': curso.nivel,
                    'grado': curso.grado,
                    'turno': curso.turno
                },
                'profesor': {
                    'id': profesor.id,
                    'nombre': profesor.profesor_id.name
                } if profesor else None,
                'materias': materias_data
            }

            response = {
                "status": "success",
                "message": "Detalles del alumno obtenidos exitosamente",
                "data": detalles_data
            }
            return http.Response(json.dumps(response), content_type='application/json')

        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')
