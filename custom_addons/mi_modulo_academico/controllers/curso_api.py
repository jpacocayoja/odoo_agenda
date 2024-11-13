import json
from odoo import http
from odoo.http import request

class CursoController(http.Controller):
    # Listar todos los cursos (READ - GET)
    @http.route('/api/cursos', type='http', auth='public', methods=['GET'])
    def get_cursos(self):
        try:
            cursos = request.env['mi_modulo_academico.curso'].search([])
            cursos_data = [{
                'id': curso.id,
                'name': curso.name,
                'nivel': curso.nivel,
                'grado': curso.grado,
                'turno': curso.turno,
            } for curso in cursos]
            
            response = {
                "status": "success",
                "message": "Cursos obtenidos exitosamente",
                "data": cursos_data
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

    # Obtener un curso por ID (READ - GET)
    @http.route('/api/cursos/<int:curso_id>', type='http', auth='public', methods=['GET'])
    def get_curso(self, curso_id):
        try:
            curso = request.env['mi_modulo_academico.curso'].browse(curso_id)
            if not curso.exists():
                response = {
                    "status": "error",
                    "message": "Curso no encontrado"
                }
                return http.Response(json.dumps(response), status=404, content_type='application/json')

            curso_data = {
                'id': curso.id,
                'name': curso.name,
                'nivel': curso.nivel,
                'grado': curso.grado,
                'turno': curso.turno,
            }
            
            response = {
                "status": "success",
                "message": "Curso obtenido exitosamente",
                "data": curso_data
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

# PARA LOS type='json' SE DEBE PONER ESTA CABECERA DESDE EL CLIENTE
#{
#   "jsonrpc": "2.0",
#   "id": null,
#   "method": "call",
#   "params": {
#        // Aquí van los datos del curso
#    }
#}
    # Crear un nuevo curso (CREATE - POST)
    @http.route('/api/cursos', type='json', auth='public', methods=['POST'])
    def create_curso(self, **post):
        try:
            # En Odoo, cuando el type es 'json', los datos ya vienen parseados
            # y están disponibles directamente en el parámetro **post
            data = post

            if not data:
                return {
                    "status": "error",
                    "message": "No se recibieron datos JSON válidos."
                }

            # Validamos que los campos requeridos estén presentes
            required_fields = ['name', 'nivel', 'grado', 'turno']
            for field in required_fields:
                if field not in data:
                    return {
                        "status": "error",
                        "message": f"El campo {field} es requerido"
                    }

            # Validación de 'nivel' y 'turno'
            if data['nivel'] not in ['primaria', 'secundaria']:
                return {
                    "status": "error",
                    "message": "El nivel debe ser 'primaria' o 'secundaria'"
                }

            if data['turno'] not in ['mañana', 'tarde']:
                return {
                    "status": "error",
                    "message": "El turno debe ser 'mañana' o 'tarde'"
                }

            # Crear el nuevo curso en la base de datos
            curso = request.env['mi_modulo_academico.curso'].sudo().create({
                'name': data['name'],
                'nivel': data['nivel'],
                'grado': data['grado'],
                'turno': data['turno']
            })

            # Respuesta de éxito
            return {
                "status": "success",
                "message": "Curso creado exitosamente",
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
        
    # Actualizar un curso (UPDATE - PUT)
    @http.route('/api/cursos/<int:curso_id>', type='json', auth='public', methods=['PUT'])
    def update_curso(self, curso_id):
        try:
            curso = request.env['mi_modulo_academico.curso'].browse(curso_id)
            if not curso.exists():
                response = {
                    "status": "error",
                    "message": "Curso no encontrado"
                }
                return http.Response(json.dumps(response), content_type='application/json', status=404)

            data = request.jsonrequest

            # Validar nivel si se proporciona
            if 'nivel' in data and data['nivel'] not in ['primaria', 'secundaria']:
                response = {
                    "status": "error",
                    "message": "El nivel debe ser 'primaria' o 'secundaria'"
                }
                return http.Response(json.dumps(response), content_type='application/json', status=400)

            # Validar turno si se proporciona
            if 'turno' in data and data['turno'] not in ['mañana', 'tarde']:
                response = {
                    "status": "error",
                    "message": "El turno debe ser 'mañana' o 'tarde'"
                }
                return http.Response(json.dumps(response), content_type='application/json', status=400)

            curso.write(data)

            response = {
                "status": "success",
                "message": "Curso actualizado exitosamente",
                "data": {
                    'id': curso.id,
                    'name': curso.name,
                    'nivel': curso.nivel,
                    'grado': curso.grado,
                    'turno': curso.turno
                }
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), content_type='application/json', status=500)

    # Eliminar un curso (DELETE)
    @http.route('/api/cursos/<int:curso_id>', type='json', auth='public', methods=['DELETE'])
    def delete_curso(self, curso_id):
        try:
            curso = request.env['mi_modulo_academico.curso'].browse(curso_id)
            if not curso.exists():
                response = {
                    "status": "error",
                    "message": "Curso no encontrado"
                }
                return http.Response(json.dumps(response), content_type='application/json', status=404)

            curso.unlink()

            response = {
                "status": "success",
                "message": "Curso eliminado exitosamente"
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), content_type='application/json', status=500)
