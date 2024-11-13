from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import base64
import time
import hashlib
import logging

_logger = logging.getLogger(__name__)

class CloudinaryConstants:
    """Constantes para la configuración de Cloudinary"""
    API_KEY = '281217171317886'
    API_SECRET = 'SGcS7K5qbrJYq4pZ1HjcuJLC24Q'
    CLOUD_NAME = 'dg2ugi96k'
    FOLDER = 'odoo'
    RESOURCE_TYPE = 'auto'

class Comunicado(models.Model):
    _name = 'mi_modulo_academico.comunicado'
    _description = 'Comunicado'

    titulo = fields.Char(string='Título', required=True)
    descripcion = fields.Text(string='Descripción', required=True)
    enlace = fields.Char(string='Enlace URL')
    archivo = fields.Binary(string='Archivo Adjunto')
    archivo_nombre = fields.Char(string="Nombre del Archivo")
    archivo_url = fields.Char(string="URL del archivo en Cloudinary", readonly=True)
    persona_id = fields.Many2one('res.partner', string='Persona')

    def _get_signature(self, params_to_sign):
        """Genera la firma para la autenticación con Cloudinary"""
        params = sorted(params_to_sign.items())
        message = '&'.join([f'{k}={v}' for k, v in params])
        # Concatenar el API_SECRET después de formar la cadena
        to_sign = f"{message}{CloudinaryConstants.API_SECRET}"
        return hashlib.sha1(to_sign.encode('utf-8')).hexdigest()

    def _upload_to_cloudinary(self, file_data, file_name):
        """Subir archivo a Cloudinary usando requests"""
        try:
            timestamp = str(int(time.time()))
            params = {
                'timestamp': timestamp,
                'api_key': CloudinaryConstants.API_KEY,
                'folder': CloudinaryConstants.FOLDER,
            }
            # Generar firma
            signature = self._get_signature(params)

            # URL de subida de Cloudinary
            upload_url = f'https://api.cloudinary.com/v1_1/{CloudinaryConstants.CLOUD_NAME}/{CloudinaryConstants.RESOURCE_TYPE}/upload'

            # Preparar archivo en binario
            file_bytes = base64.b64decode(file_data)

            # Parámetros para la solicitud
            data = {
                'api_key': CloudinaryConstants.API_KEY,
                'timestamp': timestamp,
                'signature': signature,
                'folder': CloudinaryConstants.FOLDER,
            }

            # Realizar la subida con archivos
            files = {
                'file': (file_name, file_bytes)
            }
            response = requests.post(upload_url, data=data, files=files)

            if response.status_code != 200:
                raise UserError(f'Error al subir archivo: {response.text}')

            result = response.json()
            return result.get('secure_url')

        except Exception as e:
            _logger.error(f"Error al subir archivo a Cloudinary: {str(e)}")
            raise UserError(f"Error al subir archivo: {str(e)}")

    @api.model
    def create(self, vals):
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

    def write(self, vals):
        # Subir el archivo si se actualiza
        if vals.get('archivo'):
            cloudinary_url = self._upload_to_cloudinary(
                vals['archivo'],
                vals.get('archivo_nombre', self.archivo_nombre or 'unnamed')
            )
            vals['archivo_url'] = cloudinary_url

        return super(Comunicado, self).write(vals)