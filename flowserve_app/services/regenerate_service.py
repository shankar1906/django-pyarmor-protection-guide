from django.db import connection
from datetime import datetime

class RegenerateService:
    """Service for handling regenerate report operations"""
    
    @staticmethod
    def get_serial_numbers():
        """Get distinct serial numbers from pressure_analysis table"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT VALVE_SER_NO 
                    FROM pressure_analysis 
                    WHERE VALVE_SER_NO IS NOT NULL 
                    ORDER BY VALVE_SER_NO
                """)
                rows = cursor.fetchall()
                
                return [{'serial_number': row[0]} for row in rows]
        except Exception as e:
            print(f"Error fetching serial numbers: {e}")
            return []
    
    @staticmethod
    def get_reports_by_serial(serial_number):
        """Get report data for a specific serial number grouped by COUNT_ID"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT_ID,
                        VALVE_SER_NO,
                        COALESCE(
                            DATE_FORMAT(MAX(DATE_TIME), '%%Y-%%m-%%d %%H:%%i:%%s'),
                            DATE_FORMAT(MAX(CREATED_DATE), '%%Y-%%m-%%d %%H:%%i:%%s'),
                            'N/A'
                        ) as date,
                        COUNT(*) as test_count,
                        MIN(ID) as first_id
                    FROM pressure_analysis 
                    WHERE VALVE_SER_NO = %s
                    GROUP BY COUNT_ID, VALVE_SER_NO
                    ORDER BY COUNT_ID DESC
                """, [serial_number])
                
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    results.append({
                        'id': row[0],  # COUNT_ID
                        'serial_number': row[1],
                        'date': row[2],
                        'count': row[3]  # Number of tests in this cycle
                    })
                
                return results
        except Exception as e:
            print(f"Error fetching reports: {e}")
            return []
    
    @staticmethod
    def get_report_data_for_pdf(serial_number, report_id):
        """Get detailed report data for PDF generation"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * 
                    FROM pressure_analysis 
                    WHERE VALVE_SER_NO = %s AND id = %s
                """, [serial_number, report_id])
                
                columns = [col[0] for col in cursor.description]
                row = cursor.fetchone()
                
                if row:
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            print(f"Error fetching report data for PDF: {e}")
            return None
