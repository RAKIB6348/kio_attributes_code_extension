# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    barcode_sequence_id = fields.Many2one(
        'ir.sequence',
        string='Barcode Sequence',
        copy=False,
        help='Internal sequence used for category-wise product variant barcodes.',
    )

    def _get_or_create_barcode_sequence(self):
        self.ensure_one()
        if self.barcode_sequence_id:
            return self.barcode_sequence_id

        self.env.cr.execute(
            'SELECT id FROM product_category WHERE id = %s FOR UPDATE',
            [self.id],
        )
        self.invalidate_recordset(['barcode_sequence_id'])
        if self.barcode_sequence_id:
            return self.barcode_sequence_id

        sequence_code = 'kio.product.barcode.category.%s' % self.id
        sequence = self.env['ir.sequence'].search([('code', '=', sequence_code)], limit=1)
        if not sequence:
            sequence = self.env['ir.sequence'].create({
                'name': 'Product Barcode - %s' % self.display_name,
                'code': sequence_code,
                'padding': 4,
                'number_increment': 1,
                'number_next': 1,
                'implementation': 'standard',
            })
        self.barcode_sequence_id = sequence
        return sequence

    def _get_highest_existing_barcode_sequence(self):
        self.ensure_one()
        self.env.cr.execute(
            """
            SELECT pp.barcode
              FROM product_product pp
              JOIN product_template pt ON pt.id = pp.product_tmpl_id
             WHERE pt.categ_id = %s
               AND pp.barcode IS NOT NULL
               AND pp.barcode <> ''
            """,
            [self.id],
        )
        highest_sequence = 0
        for (barcode,) in self.env.cr.fetchall():
            sequence_part = (barcode or '')[:4]
            if sequence_part.isdigit():
                highest_sequence = max(highest_sequence, int(sequence_part))
        return highest_sequence

    def _next_category_barcode_sequence(self):
        self.ensure_one()
        self.env.cr.execute(
            'SELECT id FROM product_category WHERE id = %s FOR UPDATE',
            [self.id],
        )
        self.invalidate_recordset(['barcode_sequence_id'])

        sequence = self._get_or_create_barcode_sequence()
        highest_existing_sequence = self._get_highest_existing_barcode_sequence()
        if sequence.number_next_actual <= highest_existing_sequence:
            sequence.number_next = highest_existing_sequence + 1

        return sequence.next_by_id()
