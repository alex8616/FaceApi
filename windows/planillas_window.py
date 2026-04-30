from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
import sqlite3
from datetime import datetime
import calendar


def generar_planilla_pdf(file_path, mes, anio):

    meses = {
        "Enero": 1, "Febrero": 2, "Marzo": 3,
        "Abril": 4, "Mayo": 5, "Junio": 6,
        "Julio": 7, "Agosto": 8, "Septiembre": 9,
        "Octubre": 10, "Noviembre": 11, "Diciembre": 12
    }

    mes_num = meses.get(mes, 1)
    mes_upper = mes.upper()

    conn = sqlite3.connect("personas.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, Nombre_Completo, Dni, Cargo, Tiempo
        FROM personas
        WHERE estado = "true"
        ORDER BY Nombre_Completo
    """)

    usuarios = cursor.fetchall()
    conn.close()

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=10*mm,
        rightMargin=10*mm,
        topMargin=8*mm,
        bottomMargin=8*mm
    )

    elements = []
    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        'titulo',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        fontName='Helvetica-Bold'
    )

    estilo_info = ParagraphStyle(
        'info',
        parent=styles['Normal'],
        fontSize=10
    )

    dias_es = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes",
        "Saturday": "Sábado", "Sunday": "Domingo"
    }

    dias_mes = calendar.monthrange(int(anio), mes_num)[1]

    usable_width = letter[0] - doc.leftMargin - doc.rightMargin
    page_height = letter[1]

    usable_height = page_height - doc.topMargin - doc.bottomMargin
    header_height = 25 * mm  # espacio título + info
    table_height = usable_height - header_height

    for idx, (uid, nombre, dni, cargo, tiempo) in enumerate(usuarios):

        tiempo = (tiempo or "MEDIO").upper()

        # =========================
        # ENCABEZADO
        # =========================
        elements.append(Paragraph(f"CONTROL DE ASISTENCIA ({mes_upper} - {anio})", estilo_titulo))
        elements.append(Spacer(1, 4))

        elements.append(Paragraph(
            f"<b>NOMBRE:</b> {nombre} &nbsp;&nbsp;&nbsp; "
            f"<b>C.I.:</b> {dni or '-'} &nbsp;&nbsp;&nbsp; "
            f"<b>CARGO:</b> {cargo or '-'} &nbsp;&nbsp;&nbsp; "
            f"<b>TIEMPO:</b> {tiempo}",
            estilo_info
        ))

        elements.append(Spacer(1, 6))

        # =========================
        # COLUMNAS
        # =========================
        if tiempo == "COMPLETO":

            proporciones = [
                0.09, 0.09,
                0.07, 0.07,
                0.07, 0.07,
                0.07, 0.07,
                0.07, 0.07,
                0.16
            ]

            header1 = [
                "FECHA", "DIA",
                "INGRESO", "",
                "SALIDA", "",
                "INGRESO", "",
                "SALIDA", "",
                "OBSERVACION"
            ]

            header2 = [
                "", "",
                "HORA", "FIRMA",
                "HORA", "FIRMA",
                "HORA", "FIRMA",
                "HORA", "FIRMA",
                ""
            ]

        else:

            proporciones = [
                0.14, 0.14,
                0.11, 0.11,
                0.11, 0.11,
                0.28
            ]

            header1 = [
                "FECHA", "DIA",
                "INGRESO", "",
                "SALIDA", "",
                "OBSERVACION"
            ]

            header2 = [
                "", "",
                "HORA", "FIRMA",
                "HORA", "FIRMA",
                ""
            ]

        total = sum(proporciones)
        col_widths = [(p / total) * usable_width for p in proporciones]

        table_data = [header1, header2]

        # =========================
        # FILAS
        # =========================
        for dia in range(1, dias_mes + 1):

            fecha = f"{anio}-{mes_num:02d}-{dia:02d}"

            try:
                dia_nombre = datetime.strptime(fecha, "%Y-%m-%d").strftime("%A")
                dia_es = dias_es.get(dia_nombre, dia_nombre)
            except:
                dia_es = "-"

            if tiempo == "COMPLETO":
                fila = [fecha, dia_es] + [""] * 9
            else:
                fila = [fecha, dia_es] + [""] * 5

            table_data.append(fila)

        # =========================
        # ALTURA PERFECTA A PÁGINA
        # =========================
        total_filas = len(table_data)

        row_height = table_height / total_filas
        alturas = [row_height] * total_filas

        table = Table(
            table_data,
            colWidths=col_widths,
            rowHeights=alturas,
            repeatRows=2
        )

        # =========================
        # ESTILO
        # =========================
        estilos = [
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.8, colors.black),

            ('BACKGROUND', (0, 0), (-1, 1), colors.HexColor('#2E4053')),
            ('TEXTCOLOR', (0, 0), (-1, 1), colors.white),

            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),

            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]

        # =========================
        # SPANS
        # =========================
        if tiempo == "COMPLETO":

            estilos += [
                ('SPAN', (0, 0), (0, 1)),
                ('SPAN', (1, 0), (1, 1)),

                ('SPAN', (2, 0), (3, 0)),
                ('SPAN', (4, 0), (5, 0)),
                ('SPAN', (6, 0), (7, 0)),
                ('SPAN', (8, 0), (9, 0)),

                ('SPAN', (10, 0), (10, 1)),
            ]

        else:

            estilos += [
                ('SPAN', (0, 0), (0, 1)),
                ('SPAN', (1, 0), (1, 1)),

                ('SPAN', (2, 0), (3, 0)),
                ('SPAN', (4, 0), (5, 0)),

                ('SPAN', (6, 0), (6, 1)),
            ]

        table.setStyle(TableStyle(estilos))

        elements.append(table)

        if idx < len(usuarios) - 1:
            elements.append(PageBreak())

    doc.build(elements)