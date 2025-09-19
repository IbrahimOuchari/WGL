from odoo import models

class ProductTemplateXlsx(models.AbstractModel):
    _name = 'report.nn_custom_product_costing.product_template_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, produits):
        feuille = workbook.add_worksheet('Analyse des Produits')

        # Format for centered, bold headers with larger width
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        # Format for centered rows
        row_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'
        })

        # Set column widths for better spacing
        feuille.set_column(0, 0, 50)  # Column for 'Nom'
        feuille.set_column(1, 1, 30)  # Column for 'Description'
        feuille.set_column(2, 2, 20)  # Column for 'Référence Interne'
        feuille.set_column(3, 3, 25)  # Column for 'Coût de la Nomenclature'
        feuille.set_column(4, 4, 25)  # Column for 'Coût d’Exploitation'
        feuille.set_column(5, 5, 25)  # Column for 'Coût Total'

        # Write headers
        en_tetes = ['Nom', 'Description', 'Référence Interne', 'Coût de la Nomenclature', 'Coût d’Exploitation', 'Coût Total']
        for col_num, en_tete in enumerate(en_tetes):
            feuille.write(0, col_num, en_tete, header_format)

        # Write product data with centered rows
        ligne = 1
        for produit in produits:
            feuille.write(ligne, 0, produit.name, row_format)
            feuille.write(ligne, 1, produit.description_sale or '', row_format)
            feuille.write(ligne, 2, produit.default_code or '', row_format)
            feuille.write(ligne, 3, produit.bom_cost, row_format)
            feuille.write(ligne, 4, produit.exploitation_cost, row_format)
            feuille.write(ligne, 5, produit.total_cost, row_format)
            ligne += 1
