from odoo.exceptions import UserError
from xml.dom import minidom
import base64
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class InvoiceSupplierImport(models.Model):
    _name = 'invoice.supplier.import'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Importar XML de Proveedores'

    name = fields.Char(string='Nombre')
    company_id = fields.Many2one('res.company', string='Compañía', required=True,
                                 readonly=False, default=lambda self: self.env.company)
    journal_id = fields.Many2one('account.journal', string="Diario por defecto", domain=[
        ("type", "=", "purchase")], required=True)
    account_id = fields.Many2one(
        "account.account", string="Cuenta contable por defecto", required=True)
    product_id = fields.Many2one(
        "product.product", string="Producto por defecto", required=True)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[(
        'res_model', '=', 'invoice.supplier.import')], string='Archivos')
    account_move_ids = fields.One2many(
        "account.move", "invoice_supplier_import_id", string="Facturas de proveedores")
    invoice_count = fields.Integer(
        string='Cantidad de facturas', compute='_compute_invoice_count', readonly=True)

    @api.depends('account_move_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.account_move_ids)

    def action_view_invoice(self):
        """
            Abre el tree de las facturas
        """
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_in_invoice_type")
        action['domain'] = [('id', 'in', self.account_move_ids.ids)]
        action['context'] = {
            'default_move_type': 'in_invoice',
        }
        return action

    def action_import_attachments(self):
        """
            Importa solo los XML para convertirlos a facturas
        """
        for attachment in self.attachment_ids:
            # try:
            _logger.info('Importando XML: ' + attachment.name)
            if attachment.mimetype.split('/')[1] != 'xml':
                continue
            decoded_data = base64.b64decode(attachment.datas)
            try:
                dom = minidom.parseString(decoded_data)
                self.import_invoice_from_xml(
                    dom, attachment.datas, attachment.name)
            except Exception as e:
                raise UserError(
                    'Error al importar el XML: ' + attachment.name + '\n' + str(e))

    def get_invoice_pdf_from_name(self, name):
        """
            Obtiene el PDF de la factura
        """
        pdf_files = self.attachment_ids.filtered(lambda x: x.name == name)
        if pdf_files:
            pdf_datas = pdf_files[0].datas
        else:
            pdf_datas = False
        return pdf_datas

    def create_model_registry_if_not_exists(self, model, model_field, model_field_value, model_registry_data):
        """
            Crea un registro en el modelo de registro si no existe
        """
        model_registry = self.env[model].search(
            [(model_field, '=', model_field_value)], limit=1)
        if not model_registry:
            model_registry = self.env[model].create(model_registry_data)
        return model_registry

    def get_taxes_from_xml(self, xml_data_line, nombre_binario):
        """
            Obtiene los impuestos de la factura XML
        """
        data_taxes_node = xml_data_line.getElementsByTagName("cac:TaxSubtotal")
        tax_ids = []
        for tax_node in data_taxes_node:
            tax_code = tax_node.getElementsByTagName("cac:TaxScheme")[0].getElementsByTagName("cbc:ID")[
                0].firstChild.data
            tax = self.env["account.tax"].search(
                [("type_tax_use", "=", "purchase"), ('l10n_pe_edi_tax_code', '=', tax_code.strip()),
                 ("price_include", "=", False)], limit=1)
            if tax:
                tax_ids.append((4,tax.id,0))
            else:
                raise UserError(
                    'No se encontró el impuesto con código: ' + tax_code + ' en: ' + nombre_binario)
        return tax_ids

    def get_move_lines_from_xml(self, xml_data, nombre_binario):
        """
            Obtiene los lineas de la factura XML
        """
        details = xml_data.getElementsByTagName("cac:InvoiceLine")
        account_move_lines = []
        for detail in details:
            # Producto
            data_producto = detail.getElementsByTagName("cac:Item")[0]
            product_name = data_producto.getElementsByTagName("cbc:Description")[
                0].firstChild.data
            # Cantidad
            data_quantity_node = detail.getElementsByTagName(
                "cbc:InvoicedQuantity")[0]
            quantity = data_quantity_node.firstChild.data
            # Precio unitario
            unit_price = detail.getElementsByTagName(
                "cac:Price")[0].getElementsByTagName("cbc:PriceAmount")[0].firstChild.data

            # Impuestos
            taxes = self.get_taxes_from_xml(detail, nombre_binario)

            detail_data = (0, 0, {
                "product_id": self.product_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                "name": product_name,
                "quantity": float(quantity),
                "price_unit": float(unit_price),
                "tax_ids": taxes,
                'account_id': self.account_id.id,
            })
            account_move_lines.append(detail_data)
        return account_move_lines

    def get_currency_from_xml(self, xml_data, nombre_binario):
        """
            Obtiene la moneda de la factura XML
        """
        currency_code = xml_data.getElementsByTagName(
            "cbc:DocumentCurrencyCode")[0].firstChild.data
        currency_id = self.env["res.currency"].search(
            [("name", "=", currency_code)], limit=1)
        if not currency_id:
            raise UserError(
                'No se encontró la moneda con código: ' + currency_code)
        return currency_id

    def get_document_type_from_xml(self, xml_data, nombre_binario):
        """
            Obtiene el tipo de documento de la factura XML
        """
        if xml_data.getElementsByTagName(
                "cbc:InvoiceTypeCode"):
            document_type_node = xml_data.getElementsByTagName(
                "cbc:InvoiceTypeCode")
        elif xml_data.getElementsByTagName(
                "cbc:DocumentTypeCode"):
            document_type_node = xml_data.getElementsByTagName(
                "cbc:DocumentTypeCode")
        else:
            raise UserError(
                'No se encontró el tipo de documento InvoiceTypeCode en el XML:' + nombre_binario)
        document_type_code = document_type_node[0].firstChild.data
        document_type_id = self.env["l10n_latam.document.type"].search(
            [("code", "=", document_type_code)], limit=1)
        return document_type_id

    def get_supplier_from_xml(self, xml_data, nombre_binario):
        supplier_node = xml_data.getElementsByTagName(
            "cac:AccountingSupplierParty")
        if not supplier_node:
            raise UserError(
                'No se encontró información del proveedor AccountingSupplierParty en: ' + nombre_binario)
        supplier_node = supplier_node[0]
        vat = supplier_node.getElementsByTagName("cbc:ID")[0].firstChild.data
        #name = supplier_node.getElementsByTagName("cbc:Party")
        name = supplier_node.getElementsByTagName(
            "cbc:RegistrationName")[0].firstChild.data
        identification_type_id = self.env["l10n_latam.identification.type"].search(
            [("name", "=", "RUC")], limit=1)
        address_node = supplier_node.getElementsByTagName(
            "cac:RegistrationAddress")[0]
        try:
            district = address_node.getElementsByTagName("cbc:District")[
                0].firstChild.data
            l10n_pe_district_id = self.env["l10n_pe.res.city.district"].search(
                [("name", "=", district)], limit=1)
        except:
            l10n_pe_district_id = False
        try:
            street = address_node.getElementsByTagName("cbc:Line")
            street = street[0].firstChild.data
        except:
            street = False
        supplier_data = {
            'name': name,
            'company_type': 'company',
            'l10n_latam_identification_type_id': identification_type_id.id,
            'vat': vat,
            'street': street,
            'country_id': self.env.ref('base.pe').id,
            # 'l10n_pe_district': l10n_pe_district_id.id,
        }
        return self.create_model_registry_if_not_exists('res.partner', 'vat', vat, supplier_data)

    def get_account_move_from_xml(self, xml_data, nombre_binario):
        # Proveedor
        supplier_id = self.get_supplier_from_xml(xml_data, nombre_binario)
        invoice_date = xml_data.getElementsByTagName("cbc:IssueDate")[
            0].firstChild.data
        currency_id = self.get_currency_from_xml(xml_data, nombre_binario)
        document_type_id = self.get_document_type_from_xml(
            xml_data, nombre_binario)
        data_serie = xml_data.getElementsByTagName(
            "cac:Signature")[0].getElementsByTagName("cbc:ID")[0]
        serie_correlativo = data_serie.firstChild.data

        account_move_data = {
            'invoice_user_id': self.env.user.id,
            'partner_id': supplier_id.id,
            'company_id': self.company_id.id,
            'invoice_date': invoice_date,
            'move_type': 'in_invoice',
            'invoice_supplier_import_id': self.id,
            'currency_id': currency_id.id,
            'l10n_latam_document_type_id': document_type_id.id,
            'ref': serie_correlativo
        }
        return account_move_data

    def import_invoice_from_xml(self, xml_data, archivo_binario, nombre_binario):
        in_invoice = self.env["account.move"].search(
            [("datas_fname", "=", nombre_binario)])
        if in_invoice:
            raise UserError(
                'Ya existe una factura creada a partir de: ' + nombre_binario)

        # Cabecera de Factura de proveedor
        account_move_data = self.get_account_move_from_xml(
            xml_data, nombre_binario)
        # Detalle de factura
        account_move_lines = self.get_move_lines_from_xml(
            xml_data, nombre_binario)
        # PDF
        nombre_pdf = nombre_binario.replace(".xml", ".pdf")
        pdf_binary = self.get_invoice_pdf_from_name(nombre_pdf)

        account_move_data.update({
            'data_xml': archivo_binario,
            'datas_fname': nombre_binario,
            "data_pdf": pdf_binary,
            "datas_fname_pdf": nombre_pdf,
        })

        invoice_id = self.env['account.move'].create(account_move_data)
        invoice_id.invoice_line_ids = account_move_lines
        invoice_id._onchange_invoice_line_ids()
        # for line in invoice_id.invoice_line_ids:
        #    line._onchange_account_id()
        #    line._onchange_price_subtotal()
        return invoice_id
