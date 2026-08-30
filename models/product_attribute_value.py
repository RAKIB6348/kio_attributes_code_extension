# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    value_code = fields.Char(string='Value Code')

    @api.constrains('attribute_id', 'value_code')
    def _check_size_value_code(self):
        for value in self:
            if (value.attribute_id.name or '').strip().lower() != 'size':
                continue

            value_code = (value.value_code or '').strip()
            if len(value_code) != 1 or not value_code.isdigit():
                raise ValidationError(
                    _('Size Value Code must contain exactly one digit (0-9).')
                )


class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    value_code = fields.Char(
        related='product_attribute_value_id.value_code',
        string='Value Code',
        readonly=False,
    )
