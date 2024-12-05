from odoo import models, fields, api
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    discount_percentage = fields.Float(string='Discount Percentage')
    discounted_price = fields.Monetary(
        string='Discounted Price', compute='_get_discounted_price')
    # compare_list_price

    @api.depends('list_price', 'discount_percentage')
    def _get_discounted_price(self):
        for rec in self:
            rec.discounted_price = (
                    rec.list_price
                    - (rec.list_price * (rec.discount_percentage / 100)))

    @api.constrains('discount_percentage')
    def discount_percent_max_hundred(self):
        for rec in self:
            if 0 > rec.discount_percentage or rec.discount_percentage > 100:
                raise UserError(
                    "Discount percentage should be between 0 and 100")

    def _get_sales_prices(self, pricelist, fiscal_position):
        """
        Overriding method to show proper sale price and discounted price in ecommerce
        :param pricelist:
        :param fiscal_position:
        :return: base_price, price_reduce
        """
        if not self:
            return {}

        pricelist and pricelist.ensure_one()
        pricelist = pricelist or self.env['product.pricelist']
        currency = pricelist.currency_id or self.env.company.currency_id
        date = fields.Date.context_today(self)

        sales_prices = pricelist._get_products_price(self, 1.0)
        show_discount = pricelist and pricelist.discount_policy == 'without_discount'
        show_strike_price = self.env.user.has_group('website_sale.group_product_price_comparison')

        base_sales_prices = self._price_compute('list_price', currency=currency)

        res = {}
        for template in self:
            price_reduce = sales_prices[template.id]

            product_taxes = template.sudo().taxes_id._filter_taxes_by_company(self.env.company)
            taxes = fiscal_position.map_tax(product_taxes)

            base_price = None
            price_list_contains_template = currency.compare_amounts(price_reduce, base_sales_prices[template.id]) != 0

            # Having discount percentage overrides all others
            if template.discount_percentage:
                template_price_vals = {
                    'base_price': template.list_price,
                    'price_reduce': template.discounted_price,
                }
                res[template.id] = template_price_vals
                continue

            elif template.compare_list_price and show_strike_price:
                # The base_price becomes the compare list price and the price_reduce becomes the price
                base_price = template.compare_list_price
                if not price_list_contains_template:
                    price_reduce = base_sales_prices[template.id]

                if template.currency_id != currency:
                    base_price = template.currency_id._convert(
                        base_price,
                        currency,
                        self.env.company,
                        date,
                        round=False
                    )

            elif show_discount and price_list_contains_template:
                base_price = base_sales_prices[template.id]

                # Compare_list_price are never tax included
                base_price = self._apply_taxes_to_price(
                    base_price, currency, product_taxes, taxes, template,
                )

            price_reduce = self._apply_taxes_to_price(
                price_reduce, currency, product_taxes, taxes, template,
            )

            template_price_vals = {
                'price_reduce': price_reduce,
            }
            if base_price:
                template_price_vals['base_price'] = base_price

            res[template.id] = template_price_vals

        return res
