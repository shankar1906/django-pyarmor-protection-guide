from django.db import connection
import json

def get_gauge_config_mapping():
    with connection.cursor() as cursor:
        cursor.execute("SELECT COL1_NAME, COL1_E_D, COL2_NAME, COL2_E_D, COL3_NAME, COL3_E_D, COL4_NAME, COL4_E_D FROM Gauge_Mapping LIMIT 1")
        row = cursor.fetchone()
        if row:
            return {
                "gauge_details_range": {"name": row[0], "status": row[1] == 'True'},
                "actual_pressure_2": {"name": row[2], "status": row[3] == 'True'},
                "set_pressure_2": {"name": row[4], "status": row[5] == 'True'},
                "class_based_range": {"name": row[6], "status": row[7] == 'True'},
            }
        return None

def get_gauge_color_mapping():
    with connection.cursor() as cursor:
        cursor.execute("SELECT RANGE1_VALUE, RANGE1_COLOR, RANGE2_VALUE, RANGE2_COLOR, RANGE3_VALUE, RANGE3_COLOR FROM Gauge_Mapping_Color LIMIT 1")
        row = cursor.fetchone()
        if row:
            return [
                {"range": row[0], "color": row[1]} if row[0] else None,
                {"range": row[2], "color": row[3]} if row[2] else None,
                {"range": row[4], "color": row[5]} if row[4] else None,
            ]
        return []

def get_gauge_class_mapping():
    with connection.cursor() as cursor:
        cursor.execute("SELECT ID, CLASS_NAME, RANGE_IN_BAR, RANGE_IN_PSI, RANGE_IN_KGCM2, MEDIUM FROM Gauge_Mapping_Class")
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "class_name": row[1],
                "range_bar": float(row[2]) if row[2] else 0,
                "range_psi": float(row[3]) if row[3] else 0,
                "range_kgcm2": float(row[4]) if row[4] else 0,
                "medium": row[5]
            } for row in rows
        ]

def save_gauge_config(mapping_data, color_data, class_data):
    with connection.cursor() as cursor:
        # 1. Save Gauge_Mapping (Toggles)
        cursor.execute("DELETE FROM Gauge_Mapping")
        cursor.execute("""
            INSERT INTO Gauge_Mapping (GAUGE_ID, COL1_NAME, COL1_E_D, COL2_NAME, COL2_E_D, COL3_NAME, COL3_E_D, COL4_NAME, COL4_E_D)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            1,
            "Gauge Range in Gauge Details", str(mapping_data.get('gauge_range_visibility', False)),
            "Actual pressure *2", str(mapping_data.get('actual_pressure_2', False)),
            "Set pressure *2", str(mapping_data.get('set_pressure_2', False)),
            "Class Based Range", str(mapping_data.get('class_based_range_enabled', False))
        ])

        # 2. Save Gauge_Mapping_Color
        cursor.execute("DELETE FROM Gauge_Mapping_Color")
        # Ensure we have 3 slots
        ranges = color_data + [{"range": "", "color": "#000000"}] * (3 - len(color_data))
        cursor.execute("""
            INSERT INTO Gauge_Mapping_Color (GAUGE_COLOR_ID, RANGE1_VALUE, RANGE1_COLOR, RANGE2_VALUE, RANGE2_COLOR, RANGE3_VALUE, RANGE3_COLOR)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [
            1,
            ranges[0].get('range', ''), ranges[0].get('color', '#000000'),
            ranges[1].get('range', ''), ranges[1].get('color', '#000000'),
            ranges[2].get('range', ''), ranges[2].get('color', '#000000')
        ])

        # 3. Save Gauge_Mapping_Class
        cursor.execute("DELETE FROM Gauge_Mapping_Class")
        for item in class_data:
            cursor.execute("""
                INSERT INTO Gauge_Mapping_Class (GAUGE_CLASS_ID, CLASS_NAME, RANGE_IN_BAR, RANGE_IN_PSI, RANGE_IN_KGCM2, MEDIUM)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                1,
                item.get('class_name'),
                item.get('range_bar') or 0,
                item.get('range_psi') or 0,
                item.get('range_kgcm2') or 0,
                item.get('medium')
            ])
    return True
