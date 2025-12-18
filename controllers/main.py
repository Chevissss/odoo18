from odoo import http
from odoo.http import request
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class WebsiteReserva(http.Controller):

    @http.route('/reservas', type='http', auth="public", website=True)
    def index(self, **kw):
        """Lista las canchas disponibles"""
        canchas = request.env['reserva.cancha'].sudo().search([('active', '=', True)])
        return request.render('reserva_canchas.website_cancha_list', {
            'canchas': canchas
        })

    @http.route('/reservas/cancha/<model("reserva.cancha"):cancha>', type='http', auth="public", website=True)
    def form_view(self, cancha, **kw):
        """Muestra formulario de reserva para una cancha específica"""
        return request.render('reserva_canchas.website_reserva_form', {
            'cancha': cancha
        })

    @http.route('/reservas/submit', type='http', auth="public", methods=['POST'], website=True)
    def submit_reserva(self, **post):
        """Recibe los datos, busca/crea cliente y crea la reserva"""
        cancha_id = int(post.get('cancha_id'))
        nombre = post.get('nombre')
        email = post.get('email')
        fecha_str = post.get('start_date') # Formato del input HTML: YYYY-MM-DDTHH:MM

        try:
            # 1. Gestionar Cliente (Evitar duplicados por email)
            Partner = request.env['res.partner'].sudo()
            partner = Partner.search([('email', '=', email)], limit=1)
            if not partner:
                partner = Partner.create({
                    'name': nombre,
                    'email': email
                })

            # 2. Parsear Fecha
            start_dt = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M')

            # 3. Crear Reserva (Sudo es necesario porque public user tiene permisos limitados)
            reserva = request.env['reserva.order'].sudo().create({
                'cancha_id': cancha_id,
                'partner_id': partner.id,
                'start_date': start_dt,
                'duration': 1.0, # Fijo 1 hora, o traerlo del form si deseas
                'state': 'confirmed' # Confirmamos directamente o 'draft' si requiere revisión
            })
            
            return request.render('reserva_canchas.website_success', {'reserva': reserva})

        except Exception as e:
            _logger.error(f"Error al reservar: {e}")
            return request.render('reserva_canchas.website_error', {'error_msg': str(e)})