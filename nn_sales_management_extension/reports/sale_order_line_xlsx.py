from odoo import models


class SaleOrderLineXlsx(models.AbstractModel):
    _name = 'report.nn_sales_management_extension.sale_order_line_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('Sales Order Lines')

        # Define the formats
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        row_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter'
        })

        # Set column widths for better spacing
        sheet.set_column(0, 0, 20)  # 'Date Order'
        sheet.set_column(1, 1, 30)  # 'Order ID'
        sheet.set_column(2, 2, 40)  # 'Client'
        sheet.set_column(3, 3, 50)  # 'Product'
        sheet.set_column(4, 4, 50)  # 'Description'
        sheet.set_column(5, 5, 15)  # 'Quantity'
        sheet.set_column(6, 6, 15)  # 'Price Unit'
        sheet.set_column(7, 7, 15)  # 'Discounted Price'
        sheet.set_column(8, 8, 15)  # 'Margin Product'
        sheet.set_column(9, 9, 15)  # 'Qty Delivered'
        sheet.set_column(10, 10, 15)  # 'Qty Invoiced'
        sheet.set_column(11, 11, 20)  # 'Amount (HT)'

        # Write headers
        headers = [
            'Date Order', 'Order ID', 'Client', 'Product', 'Description', 'Quantity',
            'Price Unit', 'Discounted Price', 'Margin Product', 'Qty Delivered',
            'Qty Invoiced', 'Amount (HT)'
        ]

        for col_num, header in enumerate(headers):
            sheet.write(0, col_num, header, header_format)

        # Write data rows
        row = 1
        for line in lines:
            sheet.write(row, 0, line.order_id.date_order, row_format)
            sheet.write(row, 1, line.order_id.name, row_format)
            sheet.write(row, 2, line.order_partner_id.name, row_format)
            sheet.write(row, 3, line.product_id.name, row_format)
            sheet.write(row, 4, line.name, row_format)
            sheet.write(row, 5, line.product_uom_qty, row_format)
            sheet.write(row, 6, line.price_unit, row_format)
            sheet.write(row, 7, line.pu_remise, row_format)
            sheet.write(row, 8, line.margin_product, row_format)
            sheet.write(row, 9, line.qty_delivered, row_format)
            sheet.write(row, 10, line.qty_invoiced, row_format)
            sheet.write(row, 11, line.price_subtotal, row_format)
            row += 1
