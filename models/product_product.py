# -*- coding: utf-8 -*-

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals_list):
        products = super().create(vals_list)
        products._sync_generated_barcode()
        return products

    def write(self, vals):
        res = super().write(vals)
        tracked_fields = {
            'barcode',
            'categ_id',
            'product_template_attribute_value_ids',
            'product_template_variant_value_ids',
        }
        if tracked_fields.intersection(vals):
            self._sync_generated_barcode()
        return res

    def _get_variant_attribute_value(self, attribute_name):
        self.ensure_one()
        attribute_name = attribute_name.lower()
        values = self.product_template_attribute_value_ids.filtered(
            lambda value: (value.attribute_id.name or '').strip().lower() == attribute_name
        )
        return values[:1]

    def _missing_barcode_component(self, message, raise_if_missing):
        if raise_if_missing:
            raise ValidationError(message)
        return False

    def _get_barcode_components(self, raise_if_missing=False):
        self.ensure_one()

        size_value = self._get_variant_attribute_value('Size')
        if not size_value:
            return self._missing_barcode_component(
                _('Please configure a Size for this product variant.'),
                raise_if_missing,
            )
        size_code = self._normalize_barcode_part(size_value.product_attribute_value_id.value_code)
        if not size_code:
            return self._missing_barcode_component(
                _('Please configure the Value Code for Size "%s".') % size_value.name,
                raise_if_missing,
            )

        color_value = self._get_variant_attribute_value('Color')
        if not color_value:
            return self._missing_barcode_component(
                _('Please configure a Color for this product variant.'),
                raise_if_missing,
            )

        color_code = self._normalize_barcode_part(color_value.product_attribute_value_id.value_code)
        if not color_code:
            return self._missing_barcode_component(
                _('Please configure the Value Code for Color "%s".') % color_value.name,
                raise_if_missing,
            )

        category = self.categ_id
        category_code = self._normalize_barcode_part(category.code)
        if not category_code:
            return self._missing_barcode_component(
                _('Please configure the Code for product category "%s".') % category.display_name,
                raise_if_missing,
            )

        return {
            'size_value_code': size_code,
            'color_value_code': color_code,
            'category': category,
            'category_code': category_code,
        }

    def _build_generated_barcode(self, raise_if_missing=False):
        self.ensure_one()
        components = self._get_barcode_components(raise_if_missing=raise_if_missing)
        if not components:
            return False

        category_serial = components['category']._next_category_barcode_sequence()
        return ''.join([
            category_serial,
            components['size_value_code'],
            components['category_code'],
            components['color_value_code'],
        ])

    def _sync_generated_barcode(self):
        if self.env.context.get('skip_generated_barcode_sync'):
            return

        for product in self.filtered(lambda prod: not prod.barcode):
            generated_barcode = product._build_generated_barcode()
            if generated_barcode:
                product.with_context(skip_generated_barcode_sync=True).barcode = generated_barcode

    def action_generate_dynamic_barcode(self):
        for product in self:
            generated_barcode = product._build_generated_barcode(raise_if_missing=True)
            product.with_context(skip_generated_barcode_sync=True).barcode = generated_barcode
        return True

    @staticmethod
    def _normalize_barcode_part(value):
        return ''.join((value or '').split())
