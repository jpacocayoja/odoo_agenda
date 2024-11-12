import json
from odoo import http
from odoo.http import request

class ComunicadoController(http.Controller):
    # Listar todos los comunicados (READ - GET)
    @http.route('/api/comunicados', type='http', auth='public', methods=['GET'])
    def get_comunicados(self):
        try:
            comunicados = request.env['mi_modulo_academico.comunicado'].search([])
            comunicados_data = []
            for comunicado in comunicados:
                comunicado_data = {
                    'id': comunicado.id,
                    'titulo': comunicado.titulo,
                    'descripcion': comunicado.descripcion,
                    'enlace': comunicado.enlace,
                    'archivo': comunicado.archivo.decode('utf-8') if comunicado.archivo else None,
                    'archivo_nombre': comunicado.archivo_nombre,
                    'alumno_id': {
                        'id': comunicado.alumno_id.id,
                        'name': comunicado.alumno_id.name
                    } if comunicado.alumno_id else None,
                    'curso_ids': [
                        {
                            'id': curso.id,
                            'name': curso.name,
                            'nivel': curso.nivel,
                            'grado': curso.grado,
                            'turno': curso.turno
                        } for curso in comunicado.curso_ids
                    ]
                }
                comunicados_data.append(comunicado_data)

            response = {
                "status": "success",
                "message": "Comunicados obtenidos exitosamente",
                "data": comunicados_data
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

    # Obtener un comunicado por ID (READ - GET)
    @http.route('/api/comunicados/<int:comunicado_id>', type='http', auth='public', methods=['GET'])
    def get_comunicado(self, comunicado_id):
        try:
            comunicado = request.env['mi_modulo_academico.comunicado'].browse(comunicado_id)
            if not comunicado.exists():
                response = {
                    "status": "error",
                    "message": "Comunicado no encontrado"
                }
                return http.Response(json.dumps(response), status=404, content_type='application/json')

            comunicado_data = {
                'id': comunicado.id,
                'titulo': comunicado.titulo,
                'descripcion': comunicado.descripcion,
                'enlace': comunicado.enlace,
                'archivo': comunicado.archivo.decode('utf-8') if comunicado.archivo else None,
                'archivo_nombre': comunicado.archivo_nombre,
                'alumno_id': {
                    'id': comunicado.alumno_id.id,
                    'name': comunicado.alumno_id.name
                } if comunicado.alumno_id else None,
                'curso_ids': [
                    {
                        'id': curso.id,
                        'name': curso.name,
                        'nivel': curso.nivel,
                        'grado': curso.grado,
                        'turno': curso.turno
                    } for curso in comunicado.curso_ids
                ]
            }

            response = {
                "status": "success",
                "message": "Comunicado obtenido exitosamente",
                "data": comunicado_data
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')


     # Eliminar un comunicado por ID (DELETE - DELETE)
    @http.route('/api/comunicados/<int:comunicado_id>', type='http', auth='public', methods=['DELETE'])
    def delete_comunicado(self, comunicado_id):
        try:
            comunicado = request.env['mi_modulo_academico.comunicado'].browse(comunicado_id)
            if not comunicado.exists():
                response = {
                    "status": "error",
                    "message": "Comunicado no encontrado"
                }
                return http.Response(json.dumps(response), status=404, content_type='application/json')
            
            # Eliminar el comunicado
            comunicado.unlink()

            response = {
                "status": "success",
                "message": "Comunicado eliminado exitosamente"
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
#        // Aquí van los datos del comunicado
#    }
#}      

    # Crear un nuevo comunicado (CREATE - POST)
    @http.route('/api/comunicados', type='json', auth='public', methods=['POST'])
    def create_comunicado(self, **kwargs):
        try:
            # Crear un nuevo registro en el modelo 'mi_modulo_academico.comunicado'
            comunicado = request.env['mi_modulo_academico.comunicado'].create({
                'titulo': kwargs.get('titulo'),
                'descripcion': kwargs.get('descripcion'),
                'enlace': kwargs.get('enlace'),
                'archivo': kwargs.get('archivo'),
                'archivo_nombre': kwargs.get('archivo_nombre'),
                'alumno_id': kwargs.get('alumno_id'),  # Se asume que se recibe el ID del alumno
                'curso_ids': [(6, 0, kwargs.get('curso_ids', []))]  # Se asume que se recibe una lista de IDs de cursos
            })

            response = {
                "status": "success",
                "message": "Comunicado creado exitosamente",
                "data": {
                    "id": comunicado.id,
                    "titulo": comunicado.titulo
                }
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

        
    # Actualizar un comunicado por ID (UPDATE - PUT)
    @http.route('/api/comunicados/<int:comunicado_id>', type='json', auth='public', methods=['PUT'])
    def update_comunicado(self, comunicado_id, **kwargs):
        try:
            comunicado = request.env['mi_modulo_academico.comunicado'].browse(comunicado_id)
            if not comunicado.exists():
                response = {
                    "status": "error",
                    "message": "Comunicado no encontrado"
                }
                return http.Response(json.dumps(response), status=404, content_type='application/json')
            
            # Actualizar los campos del comunicado
            comunicado.write(kwargs)

            response = {
                "status": "success",
                "message": "Comunicado actualizado exitosamente",
                "data": {
                    "id": comunicado.id,
                    "titulo": comunicado.titulo
                }
            }
            return http.Response(json.dumps(response), content_type='application/json')
        except Exception as e:
            response = {
                "status": "error",
                "message": str(e)
            }
            return http.Response(json.dumps(response), status=500, content_type='application/json')

   

    

