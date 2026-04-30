from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from collections import defaultdict
import sqlite3
from datetime import datetime
import calendar


class PDFReportes:

    def generar_pdf(self, file_path, mes, anio):

        # ==========================
        # MAPA DE MESES
        # ==========================
        MESES = {
            "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
            "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
            "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
        }

        # ==========================
        # CONVERSIÓN SEGURA
        # ==========================
        if isinstance(mes, str):
            mes = mes.capitalize()

            if mes.isdigit():
                mes_num = int(mes)
            else:
                mes_num = MESES.get(mes)

            if not mes_num:
                raise ValueError(f"Mes inválido: {mes}")
        else:
            mes_num = int(mes)

        anio = int(anio)

        # ==========================
        # DB
        # ==========================
        conn = sqlite3.connect("personas.db")
        cursor = conn.cursor()

        # 🔥 FILTRAR SOLO PERSONAS CON estado = "true"
        cursor.execute("SELECT id, Nombre_Completo, Cargo FROM personas WHERE estado = 'true' ORDER BY Nombre_Completo")
        usuarios = cursor.fetchall()

        cursor.execute("""
            SELECT persona_id, fecha, hora, tipo, IFNULL(detalles, '')
            FROM asistencias
            WHERE strftime('%m', fecha)=? AND strftime('%Y', fecha)=?
            ORDER BY fecha, hora
        """, (f"{mes_num:02d}", str(anio)))

        data = cursor.fetchall()
        conn.close()

        # ==========================
        # AGRUPAR
        # ==========================
        agrupado = defaultdict(lambda: defaultdict(list))
        for pid, fecha, hora, tipo, detalle in data:
            agrupado[pid][fecha].append((hora, tipo, detalle))

        # ==========================
        # PDF CONFIG
        # ==========================
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            leftMargin=10*mm,
            rightMargin=10*mm,
            topMargin=10*mm,
            bottomMargin=10*mm
        )

        elements = []
        styles = getSampleStyleSheet()

        estilo_titulo = ParagraphStyle(
            'titulo',
            parent=styles['Normal'],
            fontSize=12,
            alignment=1,
            fontName='Helvetica-Bold'
        )

        estilo_info = ParagraphStyle(
            'info',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica'
        )

        dias_es = {
            "Monday": "Lun", "Tuesday": "Mar", "Wednesday": "Mié",
            "Thursday": "Jue", "Friday": "Vie",
            "Saturday": "Sáb", "Sunday": "Dom"
        }

        dias_mes = calendar.monthrange(anio, mes_num)[1]

        # ==========================
        # POR USUARIO (SOLO ACTIVOS)
        # ==========================
        for idx, (persona_id, nombre, cargo) in enumerate(usuarios):

            elements.append(Paragraph(f"CONTROL DE ASISTENCIA - {mes.upper()} {anio}", estilo_titulo))
            elements.append(Spacer(1, 4))
            
            # NOMBRE Y CARGO EN UNA SOLA FILA
            elements.append(Paragraph(f"<b>Nombre:</b> {nombre} &nbsp;&nbsp;&nbsp; <b>Cargo:</b> {cargo if cargo else '-'}", estilo_info))
            elements.append(Spacer(1, 6))

            # ANCHOS AJUSTADOS
            col_widths = [
                25*mm,   # FECHA
                18*mm,   # DIA
                90*mm,   # ING/SAL
                22*mm,   # HORAS
                30*mm    # DETALLES
            ]

            table_data = [["FECHA", "DÍA", "INGRESOS/SALIDAS", "HORAS", "DETALLES"]]

            total_horas = 0
            total_dias_trabajados = 0

            # RECORRER DÍAS
            for dia in range(1, dias_mes + 1):

                fecha_dt = datetime(anio, mes_num, dia)
                fecha_str = fecha_dt.strftime("%Y-%m-%d")

                fecha_display = fecha_dt.strftime("%d/%m")
                dia_txt = dias_es.get(fecha_dt.strftime("%A"), "")

                registros = agrupado[persona_id].get(fecha_str, [])
                registros = sorted(registros, key=lambda x: x[0])

                ingresos = []
                salidas = []
                detalles = []

                for hora, tipo, det in registros:
                    if tipo == "INGRESO":
                        ingresos.append(hora[:5])
                    else:
                        salidas.append(hora[:5])

                    if det:
                        detalles.append(det)

                # ING / SAL (formato claro)
                marcas = []
                for i in range(2):
                    if i < len(ingresos):
                        marcas.append(f"Ing:{ingresos[i]}")
                    if i < len(salidas):
                        marcas.append(f"Sal:{salidas[i]}")

                operaciones = " - ".join(marcas) if marcas else "—"

                # HORAS
                seg = 0
                for i in range(min(len(ingresos), len(salidas))):
                    try:
                        e = datetime.strptime(ingresos[i], "%H:%M")
                        s = datetime.strptime(salidas[i], "%H:%M")
                        seg += (s - e).seconds
                    except:
                        pass

                if seg > 0:
                    h = seg // 3600
                    m = (seg % 3600) // 60
                    horas = f"{h:02d}:{m:02d}"
                    total_horas += seg
                    total_dias_trabajados += 1
                else:
                    horas = "--:--"

                # DETALLE CORTO
                detalle_text = detalles[0][:25] if detalles else ""

                table_data.append([
                    fecha_display,
                    dia_txt,
                    operaciones,
                    horas,
                    detalle_text
                ])

            # TOTAL
            total_txt = f"{total_horas // 3600:02d}:{(total_horas % 3600)//60:02d}"
            table_data.append(["TOTAL", f"Días trabajados: {total_dias_trabajados}", "", total_txt, ""])

            # TABLA
            table = Table(table_data, colWidths=col_widths, repeatRows=1)

            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -2), 0.25, colors.grey),
                ('BOX', (0, 0), (-1, -1), 0.8, colors.black),

                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003049")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

                ('FONTSIZE', (0, 0), (-1, -1), 8),

                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#EAF2F8")),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))

            elements.append(table)

            if idx < len(usuarios) - 1:
                elements.append(PageBreak())

        doc.build(elements)