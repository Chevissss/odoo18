from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class ReservaOrder(models.Model):
    _name = 'reserva.order'
    _description = 'Orden de Reserva'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default=lambda self: 'Borrador')
    
    cancha_id = fields.Many2one('reserva.cancha', string='Cancha', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True, tracking=True)
    
    start_date = fields.Datetime(string='Inicio', required=True, tracking=True)
    duration = fields.Float(string='Duración (Horas)', default=1.0, required=True)
    end_date = fields.Datetime(string='Fin', compute='_compute_end_date', store=True)
    
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('done', 'Finalizado'),
        ('cancel', 'Cancelado')
    ], string='Estado', default='draft', tracking=True)

    # Cálculo automático de fecha fin
    @api.depends('start_date', 'duration')
    def _compute_end_date(self):
        for r in self:
            if r.start_date and r.duration:
                r.end_date = r.start_date + timedelta(hours=r.duration)
            else:
                r.end_date = r.start_date

    # --- RESTRICCIONES (LOGIC) ---

    @api.constrains('start_date')
    def _check_past_date(self):
        for r in self:
            if r.start_date and r.start_date < fields.Datetime.now():
                raise ValidationError("Error: No se pueden crear reservas en el pasado.")

    @api.constrains('start_date', 'end_date', 'cancha_id')
    def _check_overlap(self):
        for r in self:
            if r.state == 'cancel':
                continue
            # Buscar reservas que solapen: (StartA < EndB) and (EndA > StartB)
            overlapping = self.search([
                ('id', '!=', r.id),
                ('cancha_id', '=', r.cancha_id.id),
                ('state', '!=', 'cancel'),
                ('start_date', '<', r.end_date),
                ('end_date', '>', r.start_date)
            ])
            if overlapping:
                raise ValidationError(f"La cancha '{r.cancha_id.name}' ya está reservada en este horario.")

    # --- GENERACIÓN DE SECUENCIA (ID Único) ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Borrador') == 'Borrador':
                vals['name'] = self.env['ir.sequence'].next_by_code('reserva.order') or 'RES-000'
        return super().create(vals_list)

    def action_confirm(self):
        self.state = 'confirmed'

    def action_cancel(self):
        self.state = 'cancel'
        
    def action_done(self):
        self.state = 'done'