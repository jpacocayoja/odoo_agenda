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
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # Campos básicos
    titulo = fields.Char(string='Título', required=True, tracking=True)
    descripcion = fields.Text(string='Descripción', required=True, tracking=True)
    enlace = fields.Char(string='Enlace URL', tracking=True)
    archivo = fields.Binary(string='Archivo Adjunto')
    archivo_nombre = fields.Char(string="Nombre del Archivo")
    archivo_url = fields.Char(string="URL del archivo en Cloudinary", readonly=True)

    # Campos para el audio  
    audio = fields.Binary(string='Mensaje de Voz')
    audio_nombre = fields.Char(string="Nombre del Audio")
    audio_url = fields.Char(string="URL del audio en Cloudinary", readonly=True)
    tiene_audio = fields.Boolean(string="Tiene mensaje de voz", compute='_compute_tiene_audio', store=True)
    duracion_audio = fields.Float(string="Duración (segundos)", digits=(6, 2))
    
    # Nuevos campos para destinatarios
    tipo_destinatario = fields.Selection([
        ('curso', 'Curso'),
        ('materia', 'Materia'),
        ('padre', 'Padre Específico')
    ], string='Tipo de Destinatario', required=True, tracking=True)
    
    curso_id = fields.Many2one('mi_modulo_academico.curso', string='Curso',
                              tracking=True)
    materia_id = fields.Many2one('mi_modulo_academico.materia', string='Materia',
                                tracking=True)
    padre_id = fields.Many2one('mi_modulo_academico.padre', string='Padre',
                              tracking=True)
    
    # Nuevo campo para control de envío a padres
    enviar_padres = fields.Boolean(
        string='Enviar a Padres', 
        default=True,
        help="Si está marcado, el comunicado se enviará también a los padres de los estudiantes"
    )

    
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

    tracking_ids = fields.One2many(
        'mi_modulo_academico.comunicado_tracking',
        'comunicado_id',
        string='Seguimiento de Lectura'
    )
    total_destinatarios = fields.Integer(string='Total Destinatarios', 
        compute='_compute_estadisticas_lectura', store=True)
    total_leidos = fields.Integer(string='Total Leídos', 
        compute='_compute_estadisticas_lectura', store=True)
    porcentaje_lectura = fields.Float(string='Porcentaje de Lectura', 
        compute='_compute_estadisticas_lectura', store=True)


    @api.depends('audio', 'audio_url')
    def _compute_tiene_audio(self):
        for record in self:
            record.tiene_audio = bool(record.audio or record.audio_url)

    def _validate_audio_file(self, audio_data):
        """Validar el archivo de audio"""
        if not audio_data:
            return True
            
        try:
            # Intentar decodificar los primeros bytes del archivo
            header = base64.b64decode(audio_data[:32])
            
            # Si el archivo comienza con RIFF (formato WAV) o es lo suficientemente largo, considéralo válido
            if header.startswith(b'RIFF') or len(audio_data) > 100:
                return True
                
            raise UserError('El archivo debe ser un archivo de audio válido')
                
        except Exception as e:
            if "Invalid audio file" in str(e):
                raise UserError('El archivo debe ser un archivo de audio válido')
            raise UserError(f'Error al validar el archivo de audio: {str(e)}')

    def _upload_audio_to_cloudinary(self, audio_data, audio_name):
        """Subir archivo de audio a Cloudinary"""
        try:
            timestamp = str(int(time.time()))
            
            # Parámetros para la firma
            params_to_sign = {
                'folder': CloudinaryConstants.FOLDER,
                'timestamp': timestamp,
            }
            
            # Obtener firma
            signature = self._get_cloudinary_signature(params_to_sign)
            
            # URL de subida para audio
            upload_url = f'https://api.cloudinary.com/v1_1/{CloudinaryConstants.CLOUD_NAME}/video/upload'
            
            # Datos completos para la solicitud
            data = {
                'api_key': CloudinaryConstants.API_KEY,
                'folder': CloudinaryConstants.FOLDER,
                'timestamp': timestamp,
                'signature': signature,
            }
            
            # Preparar archivo
            audio_bytes = base64.b64decode(audio_data)
            files = {'file': (audio_name, audio_bytes)}
            
            # Realizar la solicitud POST
            response = requests.post(upload_url, data=data, files=files)
            
            if response.status_code != 200:
                _logger.error(f"Error en respuesta de Cloudinary: {response.text}")
                raise UserError(f'Error al subir audio: {response.text}')
                
            result = response.json()
            return result.get('secure_url'), result.get('duration', 0)
            
        except Exception as e:
            _logger.error(f"Error al subir audio: {str(e)}")
            raise UserError(f"Error al subir audio: {str(e)}")


    @api.depends('tracking_ids', 'tracking_ids.leido')
    def _compute_estadisticas_lectura(self):
        for record in self:
            record.total_destinatarios = len(record.tracking_ids)
            record.total_leidos = len(record.tracking_ids.filtered(lambda x: x.leido))
            record.porcentaje_lectura = (record.total_leidos / record.total_destinatarios * 100) if record.total_destinatarios > 0 else 0

    @api.onchange('tipo_destinatario')
    def _onchange_tipo_destinatario(self):
        """Limpiar campos relacionados cuando cambia el tipo de destinatario"""
        self.curso_id = False
        self.materia_id = False
        self.padre_id = False

    @api.constrains('tipo_destinatario', 'curso_id', 'materia_id', 'padre_id')
    def _check_destinatario(self):
        """Validar que se haya seleccionado el destinatario correcto según el tipo"""
        for record in self:
            if record.tipo_destinatario == 'curso' and not record.curso_id:
                raise UserError('Debe seleccionar un curso')
            elif record.tipo_destinatario == 'materia' and not record.materia_id:
                raise UserError('Debe seleccionar una materia')
            elif record.tipo_destinatario == 'padre' and not record.padre_id:
                raise UserError('Debe seleccionar un padre')

    def _get_padres_destinatarios(self):
        """Obtener los padres destinatarios según el tipo de comunicado"""
        self.ensure_one()
        padres_ids = []
        
        if self.tipo_destinatario == 'padre':
            # Si es un padre específico, solo enviar a ese padre
            padres_ids = [self.padre_id.padre_id.id]
        
        elif self.tipo_destinatario == 'curso':
            # Obtener estudiantes del curso
            estudiantes = self.env['mi_modulo_academico.estudiante'].search([
                ('curso_id', '=', self.curso_id.id)
            ])
            if self.enviar_padres:
                # Si se debe enviar a padres, obtener los padres de los estudiantes
                for estudiante in estudiantes:
                    padres = self.env['mi_modulo_academico.padre'].search([
                        ('alumno_ids', 'in', [estudiante.partner_id.id])
                    ])
                    padres_ids.extend(padres.mapped('padre_id').ids)
            
        elif self.tipo_destinatario == 'materia':
            # Obtener estudiantes que están en la materia Y en el curso de la materia
            estudiantes = self.env['mi_modulo_academico.estudiante'].search([
                ('materia_ids', 'in', [self.materia_id.id]),
                ('curso_id', '=', self.materia_id.curso_id.id)
            ])
            if self.enviar_padres:
                # Si se debe enviar a padres, obtener los padres de los estudiantes
                for estudiante in estudiantes:
                    padres = self.env['mi_modulo_academico.padre'].search([
                        ('alumno_ids', 'in', [estudiante.partner_id.id])
                    ])
                    padres_ids.extend(padres.mapped('padre_id').ids)
        
        return list(set(padres_ids))  # Eliminar duplicados

    def _get_download_url(self, cloudinary_url):
        """Convierte una URL de Cloudinary en una URL de descarga directa"""
        if not cloudinary_url:
            return False
        # Agrega el parámetro fl_attachment y fl_attachment_filename para forzar la descarga
        filename = self.archivo_nombre or 'download'
        # Reemplaza http:// por https:// si es necesario
        secure_url = cloudinary_url.replace('http://', 'https://')
        # Agrega parámetros para forzar la descarga
        download_url = f"{secure_url}?fl_attachment=true&fl_attachment_filename={filename}"
        return download_url

    def _get_signature(self, params_to_sign):
        """Genera la firma para la autenticación con Cloudinary"""
        try:
            # Ordenar los parámetros alfabéticamente
            sorted_params = dict(sorted(params_to_sign.items()))
            
            # Formar la cadena con los parámetros
            message = '&'.join([f'{k}={v}' for k, v in sorted_params.items()])
            
            # Agregar el API_SECRET al final de la cadena
            to_sign = message + CloudinaryConstants.API_SECRET
            
            _logger.info(f"String to sign: {to_sign}")  # Para debugging
            
            # Generar el hash SHA1
            signature = hashlib.sha1(to_sign.encode('utf-8')).hexdigest()
            
            return signature
        except Exception as e:
            _logger.error(f"Error al generar la firma: {str(e)}")
            raise UserError(f"Error al generar la firma: {str(e)}")
        

    def _get_cloudinary_signature(self, params):
        """
        Genera la firma para Cloudinary usando los parámetros ordenados
        """
        # Ordenar los parámetros por clave
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        
        # Construir la cadena para firmar
        string_to_sign = '&'.join(f'{k}={v}' for k, v in sorted_params)
        
        # Agregar el API_SECRET
        string_to_sign += CloudinaryConstants.API_SECRET
        
        # Generar y retornar la firma
        return hashlib.sha1(string_to_sign.encode('utf-8')).hexdigest()


    
    @api.model
    def create(self, vals):
        """Sobrescribir método create para manejar archivos, audios y seguimiento"""
        try:
            # Manejar archivo si existe
            if vals.get('archivo'):
                cloudinary_url = self._upload_to_cloudinary(
                    vals['archivo'],
                    vals.get('archivo_nombre', 'unnamed'),
                    'raw'  # tipo de recurso para archivos
                )
                vals['archivo_url'] = cloudinary_url

            # Manejar audio si existe
            if vals.get('audio'):
                self._validate_audio_file(vals['audio'])
                audio_url = self._upload_to_cloudinary(
                    vals['audio'],
                    vals.get('audio_nombre', 'audio.mp3'),
                    'video'  # Cloudinary usa 'video' para archivos de audio
                )
                vals['audio_url'] = audio_url

            # Crear el comunicado
            comunicado = super(Comunicado, self).create(vals)
            
            # Crear registros de seguimiento para estudiantes
            if comunicado.tipo_destinatario in ['curso', 'materia']:
                estudiantes = []
                if comunicado.tipo_destinatario == 'curso':
                    estudiantes = comunicado.env['mi_modulo_academico.estudiante'].search([
                        ('curso_id', '=', comunicado.curso_id.id)
                    ])
                else:  # materia
                    estudiantes = comunicado.env['mi_modulo_academico.estudiante'].search([
                        ('materia_ids', 'in', [comunicado.materia_id.id]),
                        ('curso_id', '=', comunicado.materia_id.curso_id.id)
                    ])
                
                # Crear registros de seguimiento para estudiantes
                for estudiante in estudiantes:
                    self.env['mi_modulo_academico.comunicado_tracking'].create({
                        'comunicado_id': comunicado.id,
                        'persona_id': estudiante.partner_id.id,
                        'tipo_destinatario': 'estudiante'
                    })
            
            # Crear registros de seguimiento para padres
            if comunicado.tipo_destinatario == 'padre' or comunicado.enviar_padres:
                padres_ids = comunicado._get_padres_destinatarios()
                for padre_id in padres_ids:
                    self.env['mi_modulo_academico.comunicado_tracking'].create({
                        'comunicado_id': comunicado.id,
                        'persona_id': padre_id,
                        'tipo_destinatario': 'padre'
                    })
            
            return comunicado
            
        except Exception as e:
            _logger.error(f"Error al crear comunicado: {str(e)}")
            raise UserError(f"Error al crear comunicado: {str(e)}")

    def write(self, vals):
        """Sobrescribir método write para manejar la actualización de archivos y audio"""
        try:
            # Manejar actualización de archivo
            if vals.get('archivo'):
                cloudinary_url = self._upload_to_cloudinary(
                    vals['archivo'],
                    vals.get('archivo_nombre', self.archivo_nombre or 'unnamed'),
                    'raw'  # tipo de recurso para archivos
                )
                vals['archivo_url'] = cloudinary_url

            # Manejar actualización de audio
            if vals.get('audio'):
                self._validate_audio_file(vals['audio'])
                audio_url = self._upload_to_cloudinary(
                    vals['audio'],
                    vals.get('audio_nombre', self.audio_nombre or 'audio.mp3'),
                    'video'  # Cloudinary usa 'video' para archivos de audio
                )
                vals['audio_url'] = audio_url

            return super(Comunicado, self).write(vals)

        except Exception as e:
            _logger.error(f"Error al actualizar comunicado: {str(e)}")
            raise UserError(f"Error al actualizar comunicado: {str(e)}")

    def _validate_audio_file(self, audio_data):
        """Validar el archivo de audio"""
        if not audio_data:
            return True
            
        # Decodificar el inicio del archivo para verificar el tipo
        try:
            audio_header = base64.b64decode(audio_data[:32])
            # Lista de firmas de archivo comunes para formatos de audio
            audio_signatures = {
                b'RIFF': 'wav',
                b'ID3': 'mp3',
                b'OggS': 'ogg',
                b'\xFF\xFB': 'mp3',
                b'\xFF\xF3': 'mp3',
                b'\xFF\xF2': 'mp3',
                b'fLaC': 'flac'
            }
            
            # Verificar si el archivo comienza con alguna de las firmas conocidas
            is_valid = False
            for signature in audio_signatures:
                if audio_header.startswith(signature):
                    is_valid = True
                    break
                    
            if not is_valid:
                raise UserError('El archivo debe ser un archivo de audio válido (WAV, MP3, OGG, FLAC)')
                
        except Exception as e:
            raise UserError(f'Error al validar el archivo de audio: {str(e)}')
        
        return True

    def _upload_to_cloudinary(self, file_data, file_name, resource_type='raw'):
        """Subir archivo a Cloudinary usando requests"""
        try:
            timestamp = str(int(time.time()))
            
            # Parámetros para la firma
            params_to_sign = {
                'folder': CloudinaryConstants.FOLDER,
                'timestamp': timestamp,
            }
            
            # Obtener firma
            signature = self._get_cloudinary_signature(params_to_sign)
            
            # URL de subida
            upload_url = f'https://api.cloudinary.com/v1_1/{CloudinaryConstants.CLOUD_NAME}/{resource_type}/upload'
            
            # Datos completos para la solicitud
            data = {
                'api_key': CloudinaryConstants.API_KEY,
                'folder': CloudinaryConstants.FOLDER,
                'timestamp': timestamp,
                'signature': signature,
            }
            
            # Preparar archivo
            file_bytes = base64.b64decode(file_data)
            files = {'file': (file_name, file_bytes)}
            
            # Realizar la solicitud POST
            response = requests.post(upload_url, data=data, files=files)
            
            if response.status_code != 200:
                _logger.error(f"Error en respuesta de Cloudinary: {response.text}")
                raise UserError(f'Error al subir archivo: {response.text}')
                
            result = response.json()
            # Si es un archivo normal, convertir a URL de descarga
            if resource_type == 'raw':
                return self._get_download_url(result.get('secure_url'))
            # Si es un audio u otro tipo, retornar la URL directa
            return result.get('secure_url')
            
        except Exception as e:
            _logger.error(f"Error al subir archivo: {str(e)}")
            raise UserError(f"Error al subir archivo: {str(e)}")



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
    
    def action_download_file(self):
        """Método para descargar el archivo adjunto"""
        self.ensure_one()
        if not self.archivo:
            raise UserError('No hay archivo para descargar.')
            
        # Preparar la acción de descarga
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/mi_modulo_academico.comunicado/{self.id}/archivo/{self.archivo_nombre}?download=true',
            'target': 'self',
        }