from odoo import models, fields, api
import base64
import requests
from openai import OpenAI
from odoo.exceptions import ValidationError
import json
from PIL import Image
import io
import PyPDF2
import logging

_logger = logging.getLogger(__name__)

class EnvioTarea(models.Model):
    _name = 'mi_modulo_academico.envio_tarea'
    _description = 'Envío de Tarea'
    _order = 'fecha_envio desc'

    tarea_id = fields.Many2one('mi_modulo_academico.tarea', string='Tarea', required=True)
    alumno_id = fields.Many2one(
        'res.partner', 
        string='Alumno', 
        required=True,
        domain=lambda self: [
            ('id', 'in', self.env['mi_modulo_academico.estudiante'].search([]).mapped('partner_id').ids)
        ]
    )
    fecha_envio = fields.Datetime(string='Fecha de Envío', default=fields.Datetime.now)
    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('revisado', 'Revisado'),
        ('plagio', 'Posible Plagio')
    ], string='Estado', default='pendiente')
    archivo_envio = fields.Binary(string='Archivo de Tarea', required=True)
    archivo_nombre = fields.Char(string='Nombre del Archivo')

    es_prueba = fields.Boolean(string='Envío de Prueba', default=False, 
        help='Marcar si este es un envío de prueba para verificar el análisis de IA')
    
    # Campos para el análisis
    texto_extraido = fields.Text(string='Texto Extraído', readonly=True)
    probabilidad_plagio = fields.Float(string='Probabilidad de Plagio (%)', readonly=True)
    probabilidad_ia = fields.Float(string='Probabilidad de uso de IA (%)', readonly=True)
    resultado_analisis = fields.Text(string='Resultado del Análisis', readonly=True)
    detalles_plagio = fields.Text(string='Detalles de Coincidencias', readonly=True)

    def _get_chatgpt_response(self, prompt, contenido=None):
        """Método para interactuar con la API de ChatGPT usando la librería oficial"""
        try:
            # Cliente de OpenAI con API key directa
            client = OpenAI(api_key='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')
            #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
            # Preparar el mensaje
            if contenido and not contenido.startswith('http'):
                # Si hay una imagen, usar GPT-4 Vision
                messages = [{
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': prompt
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:image/jpeg;base64,{contenido}'
                            }
                        }
                    ]
                }]
                model = 'gpt-4o-mini'  # Actualizado al modelo correcto
                max_tokens = 100
            else:
                # Si solo hay texto, usar GPT-4
                messages = [{
                    'role': 'user',
                    'content': prompt
                }]
                model = 'gpt-4o-mini'  # Actualizado al modelo más reciente
                max_tokens = 100

            # Realizar la llamada a la API
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            error_msg = str(e)
            _logger.error(f"Error en la llamada a OpenAI API: {error_msg}")
            raise ValidationError(f'Error al procesar la solicitud: {error_msg}')

    # El resto del código permanece igual...
    def _procesar_archivo(self):
        """Procesa el archivo subido y lo convierte a formato adecuado para ChatGPT"""
        try:
            archivo_binario = base64.b64decode(self.archivo_envio)
            nombre_archivo = self.archivo_nombre.lower()

            # Si es un PDF, extraer el texto
            if nombre_archivo.endswith('.pdf'):
                pdf_file = io.BytesIO(archivo_binario)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                # Convertir cada página en texto
                textos_paginas = []
                for pagina in pdf_reader.pages:
                    texto = pagina.extract_text()
                    if texto:
                        textos_paginas.append(texto)
                
                return textos_paginas
            else:
                # Si es una imagen, devolverla en base64
                return [self.archivo_envio.decode()]

        except Exception as e:
            return []

    def _analizar_plagio(self, texto):
        """Analiza el texto en busca de similitudes con otros trabajos"""
        otras_tareas = self.search([
            ('tarea_id', '=', self.tarea_id.id),
            ('id', '!=', self.id),
            ('texto_extraido', '!=', False)
        ])
        
        coincidencias = []
        max_similitud = 0
        
        for otra_tarea in otras_tareas:
            from difflib import SequenceMatcher
            ratio = SequenceMatcher(None, texto, otra_tarea.texto_extraido).ratio()
            similitud = ratio * 100
            
            if similitud > 60:
                coincidencias.append({
                    'alumno': otra_tarea.alumno_id.name,
                    'similitud': similitud
                })
                max_similitud = max(max_similitud, similitud)
        
        return max_similitud, coincidencias

    def verificar_tarea(self):
        """Método para verificar la tarea con IA"""
        texto_completo = ""
        contenidos = self._procesar_archivo()
        
        for contenido in contenidos:
            if self.archivo_nombre.lower().endswith('.pdf'):
                texto_completo += contenido + "\n"
            else:
                prompt_extraccion = """
                Por favor, extrae todo el texto visible en esta imagen, incluyendo texto manuscrito.
                Ignora cualquier marca de agua o elementos decorativos.
                Solo devuelve el texto extraído, sin comentarios adicionales.
                """
                texto_parcial = self._get_chatgpt_response(prompt_extraccion, contenido)
                texto_completo += texto_parcial + "\n"
        
        self.texto_extraido = texto_completo

        # Analizar plagio
        prob_plagio, coincidencias = self._analizar_plagio(texto_completo)
        self.probabilidad_plagio = prob_plagio
        
        if coincidencias:
            detalles = "Coincidencias encontradas:\n"
            for c in coincidencias:
                detalles += f"- Similitud del {c['similitud']:.1f}% con la tarea de {c['alumno']}\n"
            self.detalles_plagio = detalles

        # Analizar uso de IA
        prompt_ia = """
        Analiza este texto y determina la probabilidad de que haya sido generado por IA.
        Considera aspectos como:
        - Naturalidad del lenguaje
        - Variaciones en el estilo
        - Errores típicos humanos vs. patrones de IA
        Responde solo con un número del 0 al 100.
        """
        resultado_ia = self._get_chatgpt_response(prompt_ia)
        print("analizando la probabilidad de uso de IA")
        print(resultado_ia)
        try:
            self.probabilidad_ia = float(resultado_ia)
        except ValueError:
            self.probabilidad_ia = 0

        # Actualizar estado y resultado
        if self.probabilidad_plagio > 80 or self.probabilidad_ia > 80:
            self.estado = 'plagio'
        else:
            self.estado = 'revisado'

        self.resultado_analisis = f"""
        Análisis completado el {fields.Datetime.now()}:
        
        1. Análisis de Plagio:
        - Similitud máxima con otras tareas: {self.probabilidad_plagio:.1f}%
        {self.detalles_plagio or 'No se encontraron coincidencias significativas'}
        
        2. Análisis de IA:
        - Probabilidad de contenido generado por IA: {self.probabilidad_ia:.1f}%
        
        Estado final: {'Posible plagio detectado' if self.estado == 'plagio' else 'Revisión completada'}
        """

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.onchange('es_prueba')
    def _onchange_es_prueba(self):
        """Actualiza la descripción cuando se marca como prueba"""
        if self.es_prueba and not self.archivo_nombre:
            self.archivo_nombre = 'prueba_analisis.pdf'