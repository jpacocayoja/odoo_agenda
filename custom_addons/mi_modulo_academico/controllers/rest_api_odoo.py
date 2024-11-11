import json
from odoo import http
from odoo.http import request

class ApiController(http.Controller):
    @http.route('/api/holamundo', type='http', auth='public', methods=['GET'])
    def hola_mundo(self):
        return http.Response(
            json.dumps({"message": "Hola Mundo"}),
            content_type='application/json'
        )
