import json
from odoo import http
from odoo.http import request
import base64
import mimetypes
from odoo.http import content_disposition

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
                    'tipo_destinatario': comunicado.tipo_destinatario,
                    'curso_id': comunicado.curso_id.id if comunicado.curso_id else None,
                    'materia_id': comunicado.materia_id.id if comunicado.materia_id else None,
                    'padre_id': comunicado.padre_id.id if comunicado.padre_id else None,
                    'state': comunicado.state
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
                'persona_id': {
                    'id': comunicado.persona_id.id,
                    'name': comunicado.persona_id.name
                } if comunicado.persona_id else None
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
                'persona_id': kwargs.get('persona_id'),  # ID de la persona asociada al comunicado
            })

            # Si tiene persona_id, crear una notificación
            if comunicado.persona_id:
                request.env['mi_modulo_academico.notificacion'].create({
                    'estado': False,  # Estado inicial de la notificación
                    'comunicado_id': comunicado.id,
                    'persona_id': comunicado.persona_id.id,
                    'persona_nombre': comunicado.persona_id.name
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

    @http.route(['/web/content/mi_modulo_academico.comunicado/<int:id>/archivo/<string:filename>'], 
                type='http', auth="public")
    def download_comunicado_file(self, id, filename, **kw):
        try:
            comunicado = request.env['mi_modulo_academico.comunicado'].sudo().browse(id)
            if not comunicado.exists() or not comunicado.archivo:
                return request.not_found()
                
            if comunicado.archivo_url:
                # Si tenemos una URL de Cloudinary, redirigimos a ella
                return http.redirect(comunicado.archivo_url)
            else:
                # Si el archivo está almacenado en Odoo
                filecontent = base64.b64decode(comunicado.archivo)
                content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                
                return request.make_response(
                    filecontent,
                    headers=[
                        ('Content-Type', content_type),
                        ('Content-Disposition', content_disposition(filename)),
                        ('Content-Length', len(filecontent)),
                    ]
                )
        except Exception as e:
            return request.not_found()
        

    @http.route('/api/comunicados/marcar_leido', type='json', auth='public', methods=['POST'])
    def marcar_comunicado_leido(self, **kwargs):
        try:
            comunicado_id = kwargs.get('comunicado_id')
            persona_id = kwargs.get('persona_id')
            
            if not comunicado_id or not persona_id:
                return {
                    'status': 'error',
                    'message': 'Se requieren comunicado_id y persona_id'
                }
            
            # Buscar el registro de seguimiento
            tracking = request.env['mi_modulo_academico.comunicado_tracking'].sudo().search([
                ('comunicado_id', '=', int(comunicado_id)),
                ('persona_id', '=', int(persona_id))
            ], limit=1)
            
            if not tracking:
                return {
                    'status': 'error',
                    'message': 'No se encontró registro de seguimiento'
                }
            
            # Actualizar el registro como leído
            tracking.write({
                'leido': True,
                'fecha_lectura': fields.Datetime.now()
            })
            
            return {
                'status': 'success',
                'message': 'Comunicado marcado como leído'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/comunicados/estadisticas/<int:comunicado_id>', type='http', auth='user', methods=['GET'])
    def get_estadisticas_lectura(self, comunicado_id):
        try:
            comunicado = request.env['mi_modulo_academico.comunicado'].browse(comunicado_id)
            if not comunicado.exists():
                return request.make_response(json.dumps({
                    'status': 'error',
                    'message': 'Comunicado no encontrado'
                }), headers={'Content-Type': 'application/json'}, status=404)
            
            # Obtener estadísticas detalladas
            tracking_data = {
                'total_destinatarios': comunicado.total_destinatarios,
                'total_leidos': comunicado.total_leidos,
                'porcentaje_lectura': comunicado.porcentaje_lectura,
                'detalles': {
                    'estudiantes': {
                        'total': len(comunicado.tracking_ids.filtered(lambda x: x.tipo_destinatario == 'estudiante')),
                        'leidos': len(comunicado.tracking_ids.filtered(lambda x: x.tipo_destinatario == 'estudiante' and x.leido)),
                    },
                    'padres': {
                        'total': len(comunicado.tracking_ids.filtered(lambda x: x.tipo_destinatario == 'padre')),
                        'leidos': len(comunicado.tracking_ids.filtered(lambda x: x.tipo_destinatario == 'padre' and x.leido)),
                    },
                    'no_leido': [{
                        'id': t.persona_id.id,
                        'nombre': t.persona_id.name,
                        'tipo': t.tipo_destinatario,
                    } for t in comunicado.tracking_ids.filtered(lambda x: not x.leido)]
                }
            }
            
            return request.make_response(
                json.dumps({'status': 'success', 'data': tracking_data}),
                headers={'Content-Type': 'application/json'}
            )
            
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json'},
                status=500
            )