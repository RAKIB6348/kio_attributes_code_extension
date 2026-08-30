# -*- coding: utf-8 -*-

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _is_size_only_variant(self):
        self.ensure_one()
        variant_lines = self.product_tmpl_id.valid_product_template_attribute_line_ids
        return (
            bool(self.product_template_attribute_value_ids)
            and len(variant_lines) == 1
            and (variant_lines.attribute_id.name or '').strip().lower() == 'size'
        )

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
        if len(color_code) != 4 or not color_code.isdigit():
            return self._missing_barcode_component(
                _('Please configure a valid 4-digit Color Value Code for color "%s".')
                % color_value.name,
                raise_if_missing,
            )

        category = self.categ_id
        category_code = self._normalize_barcode_part(category.code)
        if len(category_code) != 3 or not category_code.isdigit():
            return self._missing_barcode_component(
                _('Please configure a valid 3-digit Category Code for category "%s".')
                % category.display_name,
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
        if self._is_size_only_variant():
            return self._build_size_only_fallback_barcode()

        components = self._get_barcode_components(raise_if_missing=raise_if_missing)
        if not components:
            return False

        category_serial = components['category']._next_category_barcode_sequence()
        barcode = ''.join([
            category_serial,
            components['size_value_code'],
            components['category_code'],
            components['color_value_code'],
        ])
        if len(barcode) != 12 or not barcode.isdigit():
            raise ValidationError(_('The generated barcode must contain exactly 12 digits.'))
        return barcode

    def _build_size_only_fallback_barcode(self):
        self.ensure_one()
        size_value = self._get_variant_attribute_value('Size')
        size_code = self._normalize_barcode_part(
            size_value.product_attribute_value_id.value_code
        ) if size_value else ''
        if len(size_code) != 1 or not size_code.isdigit():
            raise ValidationError(
                _('Please configure a valid 1-digit Size Value Code for size "%s".')
                % (size_value.name if size_value else _('Size'))
            )

        category = self.categ_id
        category_code = self._normalize_barcode_part(category.code)
        if len(category_code) != 3 or not category_code.isdigit():
            raise ValidationError(
                _('Please configure a valid 3-digit Category Code for category "%s".')
                % category.display_name
            )

        serial = category._next_size_only_barcode_sequence()
        if not serial or not serial.isdigit() or int(serial) > 9999:
            raise ValidationError(
                _('The Size-only barcode serial must fit within 4 digits.')
            )
        serial = str(int(serial)).zfill(4)

        barcode = '%s%s%s0000' % (serial, size_code, category_code)
        if len(barcode) != 12 or not barcode.isdigit():
            raise ValidationError(
                _('The Size-only fallback barcode must contain exactly 12 digits.')
            )
        if self.search_count([('barcode', '=', barcode), ('id', '!=', self.id)]):
            raise ValidationError(_('The generated barcode "%s" is already in use.') % barcode)
        return barcode

    def _sync_generated_barcode(self):
        if self.env.context.get('skip_generated_barcode_sync'):
            return

        for product in self.filtered(lambda prod: not prod.barcode):
            generated_barcode = product._build_generated_barcode()
            if generated_barcode:
                product.with_context(skip_generated_barcode_sync=True).barcode = generated_barcode

    def action_generate_dynamic_barcode(self):
        for product in self:
            if product._is_size_only_variant() and product.barcode:
                continue
            generated_barcode = product._build_generated_barcode(raise_if_missing=True)
            product.with_context(skip_generated_barcode_sync=True).barcode = generated_barcode
        return True

    @staticmethod
    def _normalize_barcode_part(value):
        return ''.join((value or '').split())
