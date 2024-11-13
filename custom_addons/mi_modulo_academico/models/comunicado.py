from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
import requests
import base64
import time
import hashlib
import logging
import pytz

_logger = logging.getLogger(__name__)

class CloudinaryConstants:
    """Constantes para la configuración de Cloudinary"""
    API_KEY = '629354311966981'
    API_SECRET = '_4o1x-VtJVU11MjdPuiQyImtSm4'
    CLOUD_NAME = 'da8obisjx'
    FOLDER = 'odoo'
    RESOURCE_TYPE = 'raw'

class Comunicado(models.Model):
    _name = 'mi_modulo_academico.comunicado'
    _description = 'Comunicado'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Añadido para seguimiento
    _order = 'create_date desc'  # Ordenar por fecha de creación

    # Campos básicos
    titulo = fields.Char(string='Título', required=True, tracking=True)
    descripcion = fields.Text(string='Descripción', required=True, tracking=True)
    enlace = fields.Char(string='Enlace URL', tracking=True)
    archivo = fields.Binary(string='Archivo Adjunto')
    archivo_nombre = fields.Char(string="Nombre del Archivo")
    archivo_url = fields.Char(string="URL del archivo en Cloudinary", readonly=True)
    persona_id = fields.Many2one('res.partner', string='Persona', tracking=True)
    
    # Campos adicionales para seguimiento
    active = fields.Boolean(default=True, string='Activo')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('archived', 'Archivado')
    ], string='Estado', default='draft', tracking=True)
    
    # Campos de fechas
    create_date = fields.Datetime(string='Fecha de Creación', readonly=True)
    write_date = fields.Datetime(string='Última Modificación', readonly=True)

    def _get_signature(self, params_to_sign):
        """Genera la firma para la autenticación con Cloudinary"""
        try:
            # Ordenar los parámetros alfabéticamente
            params = sorted(params_to_sign.items())
            # Formar la cadena con los parámetros
            message = '&'.join([f'{k}={v}' for k, v in params])
            # Agregar el API_SECRET al final de la cadena
            to_sign = message + CloudinaryConstants.API_SECRET
            # Generar el hash SHA1
            signature = hashlib.sha1(to_sign.encode('utf-8')).hexdigest()
            return signature
        except Exception as e:
            _logger.error(f"Error al generar la firma: {str(e)}")
            raise UserError(f"Error al generar la firma: {str(e)}")

    def _upload_to_cloudinary(self, file_data, file_name):
        """Subir archivo a Cloudinary usando requests"""
        try:
            # Generar timestamp
             # Definir la zona horaria de Nueva York
            tz = pytz.timezone('America/New_York')
            # Obtener el tiempo actual en la zona horaria de Nueva York
            ny_time = datetime.now(tz)
            # Convertir a timestamp UNIX
            timestamp = int(ny_time.timestamp())
            
            # Preparar parámetros para la firma
            params = {
                'folder': CloudinaryConstants.FOLDER,
                'timestamp': timestamp,
                #'api_key': CloudinaryConstants.API_KEY,
                
            }
            
            # Generar firma
            signature = self._get_signature(params)

            # URL de subida de Cloudinary
            upload_url = f'https://api.cloudinary.com/v1_1/{CloudinaryConstants.CLOUD_NAME}/{CloudinaryConstants.RESOURCE_TYPE}/upload'

            # Decodificar el archivo de base64
            file_bytes = base64.b64decode(file_data)

            # Preparar datos para la solicitud
            data = {
                'api_key': CloudinaryConstants.API_KEY,
                'timestamp': timestamp,
                'signature': signature,
                'folder': CloudinaryConstants.FOLDER,
            }

            # Preparar el archivo para la subida
            files = {
                'file': (file_name, file_bytes)
            }
            
            # Realizar la solicitud POST
            response = requests.post(upload_url, data=data, files=files)

            # Verificar la respuesta
            if response.status_code != 200:
                _logger.error(f"Error en la respuesta de Cloudinary: {response.text}")
                raise UserError(f'Error al subir archivo: {response.text}')

            # Procesar la respuesta
            result = response.json()
            return result.get('secure_url')

        except requests.exceptions.RequestException as e:
            _logger.error(f"Error de conexión con Cloudinary: {str(e)}")
            raise UserError(f"Error de conexión con Cloudinary: {str(e)}")
        except Exception as e:
            _logger.error(f"Error al subir archivo a Cloudinary: {str(e)}")
            raise UserError(f"Error al subir archivo: {str(e)}")

    @api.model
    def create(self, vals):
        """Sobrescribir método create para manejar la subida de archivos"""
        try:
            # Subir el archivo si existe
            if vals.get('archivo'):
                cloudinary_url = self._upload_to_cloudinary(
                    vals['archivo'],
                    vals.get('archivo_nombre', 'unnamed')
                )
                vals['archivo_url'] = cloudinary_url

            # Crear el registro de comunicado
            comunicado = super(Comunicado, self).create(vals)

            # Crear notificación si hay persona asociada
            if comunicado.persona_id:
                self.env['mi_modulo_academico.notificacion'].create({
                    'estado': False,
                    'comunicado_id': comunicado.id,
                    'persona_id': comunicado.persona_id.id,
                    'persona_nombre': comunicado.persona_id.name
                })

            return comunicado

        except Exception as e:
            _logger.error(f"Error al crear comunicado: {str(e)}")
            raise UserError(f"Error al crear comunicado: {str(e)}")

    def write(self, vals):
        """Sobrescribir método write para manejar la actualización de archivos"""
        try:
            # Subir el archivo si se actualiza
            if vals.get('archivo'):
                cloudinary_url = self._upload_to_cloudinary(
                    vals['archivo'],
                    vals.get('archivo_nombre', self.archivo_nombre or 'unnamed')
                )
                vals['archivo_url'] = cloudinary_url

            return super(Comunicado, self).write(vals)

        except Exception as e:
            _logger.error(f"Error al actualizar comunicado: {str(e)}")
            raise UserError(f"Error al actualizar comunicado: {str(e)}")

    def unlink(self):
        """Sobrescribir método unlink para manejo seguro de eliminación"""
        for record in self:
            # Aquí podrías agregar lógica para eliminar el archivo de Cloudinary si es necesario
            try:
                return super(Comunicado, self).unlink()
            except Exception as e:
                _logger.error(f"Error al eliminar comunicado: {str(e)}")
                raise UserError(f"Error al eliminar comunicado: {str(e)}")

    # Métodos para cambios de estado
    def action_publish(self):
        """Publicar el comunicado"""
        return self.write({'state': 'published'})

    def action_archive(self):
        """Archivar el comunicado"""
        return self.write({'state': 'archived'})

    def action_draft(self):
        """Volver a borrador"""
        return self.write({'state': 'draft'})