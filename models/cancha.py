from odoo import models, fields

class CanchaSport(models.Model):
    _name = 'reserva.cancha'
    _description = 'Instalación Deportiva'
    _inherit = ['mail.thread', 'image.mixin']

    name = fields.Char(string='Nombre de la Cancha', required=True, tracking=True)
    description = fields.Text(string='Descripción')
    sport_type = fields.Selection([
        ('futbol', 'Fútbol'),
        ('tenis', 'Tenis'),
        ('padel', 'Pádel'),
        ('basket', 'Baloncesto')
    ], string='Deporte', required=True, default='futbol')
    
    hourly_rate = fields.Monetary(string='Precio por Hora', required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)
    
    active = fields.Boolean(default=True, string="Disponible")
    
    # Campo para mostrar estado en la vista kanban
    color = fields.Integer('Color Index')