from django.db import connection
from weasyprint import HTML
from django.template.loader import render_to_string
import io

def get_abrs_value():
    with connection.cursor() as cursor:
        cursor.execute("""select COL1_VALUE,COL2_VALUE,COL3_VALUE from abrs_value_table""")

class PDFService:
    """Service for PDF generation"""
    
    @staticmethod
    def generate_report_pdf(report_data):
        """Generate PDF from report data"""
        try:
            # Create a simple HTML template for the PDF
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        padding: 20px;
                    }}
                    h1 {{
                        color: #333;
                        border-bottom: 2px solid #007bff;
                        padding-bottom: 10px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #007bff;
                        color: white;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f2f2f2;
                    }}
                </style>
            </head>
            <body>
                <h1>Pressure Analysis Report</h1>
                <p><strong>Serial Number:</strong> {report_data.get('VALVE_SER_NO', 'N/A')}</p>
                <p><strong>Report ID:</strong> {report_data.get('id', 'N/A')}</p>
                
                <table>
                    <thead>
                        <tr>
                            <th>Field</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            # Add all fields from report_data
            for key, value in report_data.items():
                html_content += f"""
                        <tr>
                            <td>{key}</td>
                            <td>{value if value is not None else 'N/A'}</td>
                        </tr>
                """
            
            html_content += """
                    </tbody>
                </table>
            </body>
            </html>
            """
            
            # Generate PDF
            pdf_buffer = io.BytesIO()
            HTML(string=html_content).write_pdf(pdf_buffer)
            pdf_buffer.seek(0)
            
            return pdf_buffer
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise

