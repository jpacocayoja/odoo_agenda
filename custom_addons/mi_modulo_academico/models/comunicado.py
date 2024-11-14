from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
import requests
import base64
import hashlib
import logging
import pytz
import firebase_admin
from firebase_admin import credentials, messaging
import os

_logger = logging.getLogger(__name__)

# Inicialización de constantes de Cloudinary
class CloudinaryConstants:
    API_KEY = '629354311966981'
    API_SECRET = '_4o1x-VtJVU11MjdPuiQyImtSm4'
    CLOUD_NAME = 'da8obisjx'
    FOLDER = 'odoo'
    RESOURCE_TYPE = 'raw'

# Inicialización de Firebase
firebase_initialized = False

def initialize_firebase():
    global firebase_initialized
    if not firebase_initialized:
        dir_path = os.path.dirname(os.path.abspath(__file__))
        firebase_credential_path = os.path.join(dir_path, 'firebase.json')
        cred = credentials.Certificate(firebase_credential_path)
        firebase_admin.initialize_app(cred)
        firebase_initialized = True

def send_push_notification(tokens, title, body):
    """Envía una notificación push a través de Firebase"""
    _logger.info(f"Sending push notification: {title} - {body}")
    _logger.info(f"Tokens: {tokens}")
    try:
        initialize_firebase()
        message = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(title=title, body=body)
        )
        responses = messaging.send_each_for_multicast(message)

        # Logueo de éxito y fallos por token
        for idx, response in enumerate(responses.responses):
            if response.success:
                _logger.info(f"Push notification sent to token[{idx}] successfully.")
            else:
                _logger.error(f"Failed to send notification to token[{idx}]: {response.exception}")

    except Exception as e:
        _logger.error(f"Error sending push notification: {str(e)}")
        raise UserError(f"Error sending push notification: {str(e)}")

class Comunicado(models.Model):
    _name = 'mi_modulo_academico.comunicado'
    _description = 'Comunicado'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    titulo = fields.Char(string='Título', required=True, tracking=True)
    descripcion = fields.Text(string='Descripción', required=True, tracking=True)
    enlace = fields.Char(string='Enlace URL', tracking=True)
    archivo = fields.Binary(string='Archivo Adjunto')
    archivo_nombre = fields.Char(string="Nombre del Archivo")
    archivo_url = fields.Char(string="URL del archivo en Cloudinary", readonly=True)
    persona_id = fields.Many2one('res.partner', string='Persona', tracking=True)
    active = fields.Boolean(default=True, string='Activo')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('archived', 'Archivado')
    ], string='Estado', default='draft', tracking=True)
    create_date = fields.Datetime(string='Fecha de Creación', readonly=True)
    write_date = fields.Datetime(string='Última Modificación', readonly=True)

    def _get_signature(self, params_to_sign):
        """Genera la firma para Cloudinary"""
        try:
            params = sorted(params_to_sign.items())
            message = '&'.join([f'{k}={v}' for k, v in params])
            to_sign = message + CloudinaryConstants.API_SECRET
            signature = hashlib.sha1(to_sign.encode('utf-8')).hexdigest()
            return signature
        except Exception as e:
            _logger.error(f"Error al generar la firma: {str(e)}")
            raise UserError(f"Error al generar la firma: {str(e)}")

    def _upload_to_cloudinary(self, file_data, file_name):
        """Sube el archivo a Cloudinary usando requests"""
        try:
            tz = pytz.timezone('America/New_York')
            timestamp = int(datetime.now(tz).timestamp())
            params = {'folder': CloudinaryConstants.FOLDER, 'timestamp': timestamp}
            signature = self._get_signature(params)
            upload_url = f'https://api.cloudinary.com/v1_1/{CloudinaryConstants.CLOUD_NAME}/{CloudinaryConstants.RESOURCE_TYPE}/upload'
            file_bytes = base64.b64decode(file_data)
            data = {
                'api_key': CloudinaryConstants.API_KEY,
                'timestamp': timestamp,
                'signature': signature,
                'folder': CloudinaryConstants.FOLDER,
            }
            files = {'file': (file_name, file_bytes)}
            response = requests.post(upload_url, data=data, files=files)
            if response.status_code != 200:
                _logger.error(f"Error en la respuesta de Cloudinary: {response.text}")
                raise UserError(f'Error al subir archivo: {response.text}')
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
        """Sobrescribir método create para manejar la subida de archivos y notificación push"""
        try:
            if vals.get('archivo'):
                cloudinary_url = self._upload_to_cloudinary(
                    vals['archivo'],
                    vals.get('archivo_nombre', 'unnamed')
                )
                vals['archivo_url'] = cloudinary_url

            comunicado = super(Comunicado, self).create(vals)

            if comunicado.persona_id:
                self.env['mi_modulo_academico.notificacion'].create({
                    'estado': False,
                    'comunicado_id': comunicado.id,
                    'persona_id': comunicado.persona_id.id,
                    'persona_nombre': comunicado.persona_id.name
                })

                # Obtener tokens asociados a la persona
                tokens = self.env['mi_modulo_academico.token'].sudo().search([
                    ('persona_id', '=', comunicado.persona_id.id)
                ]).mapped('token')

                if tokens:
                    send_push_notification(
                        tokens=tokens,
                        title=comunicado.titulo,
                        body=comunicado.descripcion
                    )

            return comunicado

        except Exception as e:
            _logger.error(f"Error al crear comunicado: {str(e)}")
            raise UserError(f"Error al crear comunicado: {str(e)}")

    def write(self, vals):
        """Sobrescribir método write para manejar la actualización de archivos"""
        try:
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
        """Método unlink para eliminar comunicados"""
        for record in self:
            try:
                return super(Comunicado, self).unlink()
            except Exception as e:
                _logger.error(f"Error al eliminar comunicado: {str(e)}")
                raise UserError(f"Error al eliminar comunicado: {str(e)}")

    def action_publish(self):
        """Publicar el comunicado"""
        return self.write({'state': 'published'})

    def action_archive(self):
        """Archivar el comunicado"""
        return self.write({'state': 'archived'})

    def action_draft(self):
        """Volver a borrador"""
        return self.write({'state': 'draft'})
