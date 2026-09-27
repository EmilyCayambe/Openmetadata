#!/usr/bin/env python3
"""
generar_presentacion.py
Generador automático de la presentación en PowerPoint (.pptx) para:
"Backup de Bases de Datos, Telemetría y Optimización de Consultas SQL"
Curso: Almacenamiento y Minería de Datos

Genera gráficos vectoriales/alta resolución con Matplotlib e inserta
diapositivas modernas con formato 16:9, paleta tecnológica oscura, tarjetas
de contenido y notas para los 3 expositores.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
import matplotlib.pyplot as plt
import numpy as np

# Configurar directorio base
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
OUTPUT_PPTX = os.path.join(SCRIPT_DIR, "Presentacion_Telemetria_Optimizacion.pptx")
os.makedirs(ASSETS_DIR, exist_ok=True)

# ==============================================================================
# 1. PALETA DE COLORES MODERNA (SLATE & NEON TECH)
# ==============================================================================
BG_DARK = RGBColor(11, 19, 43)        # #0B132B (Fondo principal)
CARD_BG = RGBColor(28, 37, 65)        # #1C2541 (Fondo tarjetas)
CARD_BORDER = RGBColor(58, 80, 107)   # #3A506B (Bordes)
CYAN_ACCENT = RGBColor(72, 202, 228)  # #48CAE4 (Color primario / títulos)
GREEN_ACCENT = RGBColor(6, 214, 160)  # #06D6A0 (Éxito / optimización)
AMBER_ACCENT = RGBColor(255, 209, 102)# #FFD166 (Alertas / notas)
RED_ACCENT = RGBColor(239, 71, 111)   # #EF476F (Desastre / problemas)
TEXT_WHITE = RGBColor(245, 247, 250)  # #F5F7FA (Texto principal)
TEXT_MUTED = RGBColor(160, 174, 192)  # #A0AEC0 (Texto secundario)

# ==============================================================================
# 2. GENERADOR DE GRÁFICOS ILUSTRATIVOS CON MATPLOTLIB
# ==============================================================================
def generar_grafico_paradoja_logs():
    """Genera gráfico comparativo: Crecimiento de Logs vs Crecimiento de Tabla"""
    path = os.path.join(ASSETS_DIR, "grafico_paradoja_logs.png")
    fig, ax = plt.subplots(figsize=(6.5, 3.8), facecolor='#1C2541')
    ax.set_facecolor('#1C2541')

    updates = np.array([0, 50, 100, 200, 350, 500, 750, 1000])
    tabla_mb = np.array([12.1, 12.12, 12.15, 12.18, 12.22, 12.25, 12.29, 12.33]) # Casi plano
    logs_mb = np.array([0.1, 8.5, 18.2, 39.5, 71.0, 105.4, 162.8, 224.0])        # Exponencial

    ax.plot(updates, logs_mb, color='#EF476F', linewidth=3.5, marker='o', label='Volumen de Logs y WALs (MB)', zorder=4)
    ax.plot(updates, tabla_mb, color='#06D6A0', linewidth=3.5, marker='s', label='Tamaño de Tabla en Disco (MB)', zorder=4)
    ax.fill_between(updates, logs_mb, color='#EF476F', alpha=0.18)

    ax.set_title("La Paradoja: Volumen de Logs vs Tamaño de Tabla", color='#48CAE4', fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel("Número de Sentencias Transaccionales (UPDATES)", color='#A0AEC0', fontsize=10)
    ax.set_ylabel("Megabytes (MB)", color='#A0AEC0', fontsize=10)
    ax.tick_params(colors='#F5F7FA', labelsize=9)
    ax.grid(True, linestyle='--', alpha=0.25, color='#48CAE4')

    for spine in ax.spines.values():
        spine.set_color('#3A506B')

    legend = ax.legend(facecolor='#0B132B', edgecolor='#3A506B', fontsize=9)
    for text in legend.get_texts():
        text.set_color('#F5F7FA')

    plt.tight_layout()
    plt.savefig(path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    return path

def generar_grafico_optimizacion():
    """Genera gráfico de barras: Rendimiento Antes vs Después de Índices"""
    path = os.path.join(ASSETS_DIR, "grafico_optimizacion_benchmark.png")
    fig, ax = plt.subplots(figsize=(6.5, 3.8), facecolor='#1C2541')
    ax.set_facecolor('#1C2541')

    casos = ['Caso 1: DNI\n(B-Tree)', 'Caso 2: Cuentas\n(Compuesto)', 'Caso 3: LOWER()\n(Funcional)']
    sin_indice = [13.71, 28.50, 42.10]
    con_indice = [0.12, 0.45, 0.28]

    x = np.arange(len(casos))
    width = 0.32

    rects1 = ax.bar(x - width/2, sin_indice, width, label='Sin Índice (Seq Scan)', color='#EF476F', edgecolor='#0B132B', zorder=3)
    rects2 = ax.bar(x + width/2, con_indice, width, label='Con Índice (Index Scan)', color='#06D6A0', edgecolor='#0B132B', zorder=3)

    ax.set_title("Impacto de Optimización: Tiempo de Ejecución (ms)", color='#48CAE4', fontsize=12, fontweight='bold', pad=12)
    ax.set_ylabel("Milisegundos (ms) - Menor es mejor", color='#A0AEC0', fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(casos, color='#F5F7FA', fontsize=9, fontweight='semibold')
    ax.tick_params(colors='#F5F7FA', labelsize=9)
    ax.grid(True, axis='y', linestyle='--', alpha=0.25, color='#48CAE4')

    # Añadir etiquetas de valor
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f'{h:.1f}ms', xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                    color='#EF476F', fontsize=8.5, fontweight='bold')

    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f'{h:.2f}ms', xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                    color='#06D6A0', fontsize=8.5, fontweight='bold')

    for spine in ax.spines.values():
        spine.set_color('#3A506B')

    legend = ax.legend(facecolor='#0B132B', edgecolor='#3A506B', fontsize=9)
    for text in legend.get_texts():
        text.set_color('#F5F7FA')

    plt.tight_layout()
    plt.savefig(path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    return path

def generar_diagrama_backups():
    """Genera infografía conceptual de los tipos de backup y RTO"""
    path = os.path.join(ASSETS_DIR, "grafico_tipos_backups.png")
    fig, ax = plt.subplots(figsize=(6.5, 3.8), facecolor='#1C2541')
    ax.set_facecolor('#1C2541')

    dias = ['Dom', 'Lun', 'Mar', 'Mie', 'Jue']
    full = [100, 0, 0, 0, 0]
    incr = [0, 15, 18, 22, 25]
    diff = [0, 15, 33, 55, 80]

    x = np.arange(len(dias))
    width = 0.28

    ax.bar(x - width, full, width, label='Full Backup (Base)', color='#48CAE4', zorder=3)
    ax.bar(x, incr, width, label='Incremental (Solo cambios del día)', color='#FFD166', zorder=3)
    ax.bar(x + width, diff, width, label='Diferencial (Acumulado desde Full)', color='#06D6A0', zorder=3)

    ax.set_title("Estrategias de Backup: Espacio Requerido por Día (MB)", color='#48CAE4', fontsize=12, fontweight='bold', pad=12)
    ax.set_ylabel("Espacio de Almacenamiento Estimado", color='#A0AEC0', fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(dias, color='#F5F7FA', fontsize=9, fontweight='semibold')
    ax.tick_params(colors='#F5F7FA', labelsize=9)
    ax.grid(True, axis='y', linestyle='--', alpha=0.25, color='#48CAE4')

    for spine in ax.spines.values():
        spine.set_color('#3A506B')

    legend = ax.legend(facecolor='#0B132B', edgecolor='#3A506B', fontsize=8.5)
    for text in legend.get_texts():
        text.set_color('#F5F7FA')

    plt.tight_layout()
    plt.savefig(path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    return path

# ==============================================================================
# 3. HELPER FUNCTIONS PARA PYTHON-PPTX (DISEÑO SLATE TECH 16:9)
# ==============================================================================
def create_base_slide(prs, category_tag="ALMACENAMIENTO Y MINERÍA DE DATOS", title_text=""):
    """Crea una diapositiva con fondo oscuro, franjas y cabecera estándar."""
    blank_layout = prs.slide_layouts[6] # Blank
    slide = prs.slides.add_slide(blank_layout)

    # Fondo general
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_DARK
    bg.line.fill.background()

    # Barra superior de acento
    accent_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = CYAN_ACCENT
    accent_bar.line.fill.background()

    # Tag de categoría / Módulo
    if category_tag:
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_tag.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = GREEN_ACCENT

    # Título principal
    if title_text:
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

    return slide

def add_card(slide, left, top, width, height, title="", border_color=CARD_BORDER):
    """Crea un contenedor tipo tarjeta con bordes y fondo oscuro."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)

    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = CYAN_ACCENT
    return card

def add_bullet_list(slide, left, top, width, height, items, font_size=13, text_color=TEXT_WHITE):
    """Añade una lista de viñetas con formato profesional."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"•  {item}"
        p.font.size = Pt(font_size)
        p.font.color.rgb = text_color
        p.space_after = Pt(8)
    return tb

# ==============================================================================
# 4. CONSTRUCCIÓN DE CADA DIAPOSITIVA DE LA PRESENTACIÓN
# ==============================================================================
def generar_presentacion_completa():
    prs = Presentation()
    # Configurar formato panorámico 16:9
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    print(">>> Generando gráficos analíticos...")
    img_paradoja = generar_grafico_paradoja_logs()
    img_optimizacion = generar_grafico_optimizacion()
    img_backups = generar_diagrama_backups()

    print(">>> Construyendo diapositivas...")

    # --------------------------------------------------------------------------
    # SLIDE 1: PORTADA
    # --------------------------------------------------------------------------
    s1 = prs.slides.add_slide(prs.slide_layouts[6])
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = BG_DARK
    bg1.line.fill.background()

    # Barra decorativa de portada
    dec_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.6), Inches(1.2), Inches(0.08))
    dec_bar.fill.solid()
    dec_bar.fill.fore_color.rgb = CYAN_ACCENT
    dec_bar.line.fill.background()

    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.9), Inches(11.7), Inches(2.2))
    tf = t_box.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "Backups, Telemetría y Optimización SQL"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE

    p2 = tf.add_paragraph()
    p2.text = "Arquitectura Desacoplada, Resiliencia y Tuning en Bases de Datos Relacionales"
    p2.font.size = Pt(18)
    p2.font.color.rgb = CYAN_ACCENT
    p2.space_before = Pt(10)

    # Tarjetas de datos del curso y equipo
    c1 = add_card(s1, Inches(0.8), Inches(4.5), Inches(5.6), Inches(2.0), "Materia y Contexto")
    add_bullet_list(s1, Inches(1.0), Inches(5.1), Inches(5.2), Inches(1.2), [
        "Curso: Almacenamiento y Minería de Datos",
        "Ciclo: 8vo Ciclo Universitario",
        "Entorno: 100% Dockerizado & Infraestructura como Código"
    ], font_size=12, text_color=TEXT_MUTED)

    c2 = add_card(s1, Inches(6.8), Inches(4.5), Inches(5.7), Inches(2.0), "Equipo de Expositores (3 Estudiantes)")
    add_bullet_list(s1, Inches(7.0), Inches(5.1), Inches(5.3), Inches(1.2), [
        "Estudiante 1: Resiliencia, Backups (Full/Incr/Diff) & PITR",
        "Estudiante 2: Telemetría, Servidor Desacoplado & Loki/Grafana",
        "Estudiante 3: Ingesta Masiva & Optimización de Consultas SQL"
    ], font_size=12, text_color=TEXT_MUTED)

    # --------------------------------------------------------------------------
    # SLIDE 2: OBJETIVO Y PROBLEMÁTICA REAL
    # --------------------------------------------------------------------------
    s2 = create_base_slide(prs, "1. PROBLEMÁTICA Y OBJETIVOS", "¿Por qué las bases de datos colapsan en producción?")

    add_card(s2, Inches(0.8), Inches(1.7), Inches(3.6), Inches(4.8), "1. Pérdida de Datos", border_color=RED_ACCENT)
    add_bullet_list(s2, Inches(1.0), Inches(2.4), Inches(3.2), Inches(3.8), [
        "Desastres humanos (DROP TABLE accidental) o fallos de hardware.",
        "Un backup diario (Full) no es suficiente: se pierden horas de transacciones.",
        "Meta: RPO cercano a 0 segundos mediante archivado continuo (WAL)."
    ], font_size=13)

    add_card(s2, Inches(4.8), Inches(1.7), Inches(3.6), Inches(4.8), "2. La Paradoja de los Logs", border_color=AMBER_ACCENT)
    add_bullet_list(s2, Inches(5.0), Inches(2.4), Inches(3.2), Inches(3.8), [
        "Cada sentencia genera logs de auditoría, locks y registros WAL.",
        "Los logs crecen mucho más rápido que las tablas mismas.",
        "Si compiten por disco e I/O en producción, el servidor colapsa por disco lleno."
    ], font_size=13)

    add_card(s2, Inches(8.8), Inches(1.7), Inches(3.7), Inches(4.8), "3. Degradación de Consultas", border_color=GREEN_ACCENT)
    add_bullet_list(s2, Inches(9.0), Inches(2.4), Inches(3.3), Inches(3.8), [
        "Con millones de registros, los escaneos secuenciales agotan la memoria RAM.",
        "Falta de índices o anti-patrones con funciones (ej. LOWER).",
        "Meta: Reducir tiempos de ejecución de 50ms a <0.2ms usando B-Tree y planes óptimos."
    ], font_size=13)

    # --------------------------------------------------------------------------
    # SLIDE 3: ARQUITECTURA DEL LABORATORIO (DOCKER)
    # --------------------------------------------------------------------------
    s3 = create_base_slide(prs, "2. ARQUITECTURA TÉCNICA", "Laboratorio Desacoplado Multi-Contenedor (Docker)")

    add_card(s3, Inches(0.8), Inches(1.7), Inches(5.7), Inches(5.0), "Topología de Servicios Aislados")
    add_bullet_list(s3, Inches(1.0), Inches(2.3), Inches(5.3), Inches(4.2), [
        "db-primary (PostgreSQL 16): Motor transaccional con 600,000 registros sintéticos y logging activo (log_statement='all').",
        "promtail-agent: Agente ligero que extrae los logs en streaming sin consumir CPU del motor de BD.",
        "loki-server: Servidor dedicado exclusivamente al almacenamiento y compresión de logs.",
        "grafana-dashboard: Interfaz visual de telemetría en tiempo real (Puerto 3000).",
        "backup_storage: Volumen montado independiente para aislar dumps y segmentos WAL de contingencia."
    ], font_size=13)

    add_card(s3, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.0), "Principio de Aislamiento y Resiliencia")
    add_bullet_list(s3, Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.2), [
        "¿Por qué un servidor de logs separado?",
        "1. No saturar el I/O del disco transaccional: Las consultas de analítica de logs no frenan a los clientes del banco.",
        "2. Auditoría post-mortem: Si la base de datos se corrompe o se apaga, los logs permanecen a salvo en Loki para análisis forense.",
        "3. Costo $0 y 100% reproducible: Levanta en cualquier laptop con un solo comando: 'docker compose up -d'."
    ], font_size=13)

    # --------------------------------------------------------------------------
    # SLIDE 4: MÓDULO 1 - MÉTODOS DE BACKUP
    # --------------------------------------------------------------------------
    s4 = create_base_slide(prs, "3. MÓDULO DE RESILIENCIA (ESTUDIANTE 1)", "Estrategias de Backup: Totales, Incrementales y Diferenciales")

    add_card(s4, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.0), "Comparativa de Métodos")
    add_bullet_list(s4, Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.2), [
        "Backup Total (Full): Copia completa de esquema y datos (pg_dump comprimido). Es la base obligatoria de todo plan de recuperación.",
        "Backup Incremental: Respalda SOLO los cambios ocurridos desde el último backup (vía segmentos WAL de 16MB). Menor espacio, pero requiere toda la cadena para restaurar.",
        "Backup Diferencial: Respalda todos los cambios ocurridos desde el último Full. Restauración más rápida (Full + Último Diferencial).",
        "RPO (Recovery Point Objective): Cantidad máxima de datos que la empresa tolera perder.",
        "RTO (Recovery Time Objective): Tiempo máximo tolerado para volver a operar."
    ], font_size=12.5)

    # Insertar gráfico de backups
    s4.shapes.add_picture(img_backups, Inches(6.7), Inches(1.8), width=Inches(5.8))

    # --------------------------------------------------------------------------
    # SLIDE 5: MÓDULO 1 EN VIVO - DESASTRE Y PITR
    # --------------------------------------------------------------------------
    s5 = create_base_slide(prs, "3.1 DEMOSTRACIÓN EN VIVO (ESTUDIANTE 1)", "Simulación de Desastre y Restauración Point-in-Time")

    add_card(s5, Inches(0.8), Inches(1.7), Inches(5.7), Inches(5.0), "El Experimento en Vivo")
    add_bullet_list(s5, Inches(1.0), Inches(2.3), Inches(5.3), Inches(4.2), [
        "Paso 1: Se ejecuta backup_full.ps1 generando un dump comprimido de 13 MB en 5.2 segundos.",
        "Paso 2: Se inyecta una transacción de emergencia de alto valor.",
        "Paso 3: Se simula un error catastrófico ejecutando:",
        "    DROP TABLE transacciones CASCADE;",
        "    DROP TABLE cuentas CASCADE;",
        "Paso 4: Se demuestra que las tablas ya no existen.",
        "Paso 5: Se ejecuta disaster_and_restore.ps1 restaurando las 600,000 filas de forma íntegra en ~6 segundos."
    ], font_size=13)

    add_card(s5, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.0), "Concepto Clave: WAL y LSN", border_color=AMBER_ACCENT)
    add_bullet_list(s5, Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.2), [
        "¿Cómo funciona el Write-Ahead Logging (WAL)?",
        "1. Ningún dato se escribe en la tabla antes de haberse registrado en el log de transacciones (WAL).",
        "2. Cada transacción tiene un LSN (Log Sequence Number) correlativo y monotónico.",
        "3. Con WAL Archiving activo ('archive_mode=on'), cada bloque cerrado se envía al volumen seguro.",
        "4. En un desastre, se aplica el Full Backup y se 'reproducen' los WALs hasta el segundo exacto previo al fallo."
    ], font_size=13)

    # --------------------------------------------------------------------------
    # SLIDE 6: MÓDULO 2 - TELEMETRÍA Y SERVIDOR DE LOGS
    # --------------------------------------------------------------------------
    s6 = create_base_slide(prs, "4. MÓDULO DE OBSERVABILIDAD (ESTUDIANTE 2)", "Telemetría y Almacenamiento Desacoplado de Logs")

    add_card(s6, Inches(0.8), Inches(1.7), Inches(5.7), Inches(5.0), "¿Qué es la Telemetría de BD?")
    add_bullet_list(s6, Inches(1.0), Inches(2.3), Inches(5.3), Inches(4.2), [
        "No es solo monitorear CPU o RAM: es capturar la huella de cada sentencia SQL individual.",
        "Métricas capturadas en tiempo real:",
        "  • QPS (Queries per Second): Caudal transaccional.",
        "  • Desglose DML: Proporción de SELECT vs INSERT/UPDATE.",
        "  • Errores y Rollbacks: Detección proactiva de transacciones abortadas o violaciones de constraints.",
        "  • Latencia por sentencia: Detección inmediata de cuellos de botella."
    ], font_size=13)

    add_card(s6, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.0), "El Stack Loki + Grafana")
    add_bullet_list(s6, Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.2), [
        "Grafana Loki es 'Prometheus para Logs':",
        "1. No indexa el texto completo del log, solo indexa metadatos (labels), logrando que consuma 10 veces menos RAM que Elasticsearch.",
        "2. Promtail lee el archivo postgresql.log en streaming constante sin bloquear la tabla ni la sesión activa.",
        "3. Grafana muestra los paneles en vivo refrescándose cada 5 segundos frente a la clase."
    ], font_size=13)

    # --------------------------------------------------------------------------
    # SLIDE 7: MÓDULO 2 EN VIVO - LA PARADOJA DE LOS LOGS
    # --------------------------------------------------------------------------
    s7 = create_base_slide(prs, "4.1 DEMOSTRACIÓN EN VIVO (ESTUDIANTE 2)", "La Paradoja: Crecimiento de Logs vs Crecimiento de Tablas")

    add_card(s7, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.0), "Demostración de la Paradoja")
    add_bullet_list(s7, Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.2), [
        "Experimento: Se ejecutan 500 UPDATEs sobre una sola fila de saldo.",
        "Resultado en Disco:",
        "  • La tabla 'cuentas' mide lo mismo: 12.1 MB.",
        "  • Pero se emitieron 500 registros WAL y 500 eventos en Loki.",
        "Conclusión Arquitectónica:",
        "  Los logs crecen en función de la actividad transaccional, no del volumen de registros almacenados.",
        "  Si los logs se guardan en el servidor transaccional, el disco se llenará inevitablemente."
    ], font_size=13)

    s7.shapes.add_picture(img_paradoja, Inches(6.7), Inches(1.8), width=Inches(5.8))

    # --------------------------------------------------------------------------
    # SLIDE 8: MÓDULO 3 - OPTIMIZACIÓN DE CONSULTAS SQL
    # --------------------------------------------------------------------------
    s8 = create_base_slide(prs, "5. MÓDULO DE TUNING (ESTUDIANTE 3)", "Optimización de Consultas SQL y Análisis de Planes (EXPLAIN)")

    add_card(s8, Inches(0.8), Inches(1.7), Inches(5.7), Inches(5.0), "Anatomía de EXPLAIN ANALYZE")
    add_bullet_list(s8, Inches(1.0), Inches(2.3), Inches(5.3), Inches(4.2), [
        "EXPLAIN (ANALYZE, BUFFERS): La herramienta suprema del DBA.",
        "1. Execution Time: Tiempo real consumido por la CPU y el motor.",
        "2. Buffers read vs shared hit:",
        "    • Hit: Datos encontrados en caché RAM (rápido).",
        "    • Read: Datos que tuvieron que leerse físicamente del disco (lento, I/O bound).",
        "3. Sequential Scan (Seq Scan): Escaneo de la tabla completa línea por línea (O(N)). Inviable en grandes volúmenes.",
        "4. Index Scan / Bitmap Index Scan: Búsqueda mediante árbol B-Tree logarítmico (O(log N))."
    ], font_size=13)

    add_card(s8, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.0), "Estrategias de Indexación Demostradas")
    add_bullet_list(s8, Inches(7.0), Inches(2.3), Inches(5.3), Inches(4.2), [
        "1. B-Tree Unique Index: Búsqueda puntual por DNI sobre 100k registros.",
        "2. Índice Compuesto Multicolumna: Filtrado por cuenta y ordenamiento por fecha (evita el costo del algoritmo SORT).",
        "3. Índice Funcional / Basado en Expresiones: Superación del anti-patrón de funciones en el WHERE (ej. LOWER(email)).",
        "4. Monitoreo Global con pg_stat_statements: Identificar el 'Top 10' de consultas más costosas del sistema."
    ], font_size=13)

    # --------------------------------------------------------------------------
    # SLIDE 9: MÓDULO 3 EN VIVO - BENCHMARK DE RESULTADOS
    # --------------------------------------------------------------------------
    s9 = create_base_slide(prs, "5.1 DEMOSTRACIÓN EN VIVO (ESTUDIANTE 3)", "Resultados en Vivo: De Seq Scan a Index Scan")

    add_card(s9, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.0), "Casos Demostrados")
    add_bullet_list(s9, Inches(1.0), Inches(2.3), Inches(5.2), Inches(4.2), [
        "Caso 1 (DNI):",
        "  • Antes: 13.71 ms | 1,301 bloques leídos.",
        "  • Después: 0.12 ms | 4 bloques leídos (>110x más rápido).",
        "Caso 2 (Compuesto cuenta_id + fecha):",
        "  • Elimina la etapa de ordenamiento en memoria ('Sort Method: quicksort').",
        "Caso 3 (LOWER email):",
        "  • La función LOWER() anulaba el índice normal.",
        "  • El índice funcional idx_clientes_email_lower resolvió el cuello de botella."
    ], font_size=12.5)

    s9.shapes.add_picture(img_optimizacion, Inches(6.7), Inches(1.8), width=Inches(5.8))

    # --------------------------------------------------------------------------
    # SLIDE 10: GUION DE EXPOSICIÓN (CRONOGRAMA DE 18 MINUTOS)
    # --------------------------------------------------------------------------
    s10 = create_base_slide(prs, "6. METODOLOGÍA DE PRESENTACIÓN", "Cronograma de Exposición Colaborativa (18 Minutos)")

    add_card(s10, Inches(0.8), Inches(1.7), Inches(3.6), Inches(5.0), "Minuto 0 a 6: Estudiante 1", border_color=CYAN_ACCENT)
    add_bullet_list(s10, Inches(1.0), Inches(2.3), Inches(3.2), Inches(4.0), [
        "• Explica la arquitectura Docker.",
        "• Presenta el esquema relacional con 600,000 filas.",
        "• Corre backup_full.ps1 en vivo.",
        "• Simula el desastre (DROP TABLE).",
        "• Restaura los datos con disaster_and_restore.ps1 y muestra el éxito."
    ], font_size=12.5)

    add_card(s10, Inches(4.8), Inches(1.7), Inches(3.6), Inches(5.0), "Minuto 6 a 12: Estudiante 2", border_color=AMBER_ACCENT)
    add_bullet_list(s10, Inches(5.0), Inches(2.3), Inches(3.2), Inches(4.0), [
        "• Lanza el generador de tráfico:",
        "  traffic_generator.py.",
        "• Muestra el Dashboard de Grafana en tiempo real.",
        "• Explica el flujo Promtail -> Loki.",
        "• Demuestra la paradoja del crecimiento de logs vs tablas con el modo growth."
    ], font_size=12.5)

    add_card(s10, Inches(8.8), Inches(1.7), Inches(3.7), Inches(5.0), "Minuto 12 a 18: Estudiante 3", border_color=GREEN_ACCENT)
    add_bullet_list(s10, Inches(9.0), Inches(2.3), Inches(3.3), Inches(4.0), [
        "• Abre DBeaver/psql con optimization_demo.sql.",
        "• Ejecuta la consulta sin índice y analiza los Buffers y Seq Scan.",
        "• Crea el índice en vivo.",
        "• Muestra la caída de tiempo a 0.1ms.",
        "• Consulta pg_stat_statements.",
        "• Conclusiones finales."
    ], font_size=12.5)

    # --------------------------------------------------------------------------
    # SLIDE 11: CONCLUSIONES Y LECCIONES APRENDIDAS
    # --------------------------------------------------------------------------
    s11 = create_base_slide(prs, "7. CONCLUSIONES", "Lecciones Clave para la Gestión de Datos Empresariales")

    c_final = add_card(s11, Inches(0.8), Inches(1.7), Inches(11.7), Inches(5.0), "Conclusiones Principales del Proyecto")
    add_bullet_list(s11, Inches(1.1), Inches(2.4), Inches(11.1), Inches(4.0), [
        "1. Resiliencia Moderna: Los backups ya no son fotos estáticas; se sustentan en el archivado continuo de transacciones (WAL / LSN) para garantizar RPO cercanos a cero.",
        "2. Aislamiento de Observabilidad: Los logs de auditoría y telemetría crecen exponencialmente más rápido que las tablas de datos. Deben desacoplarse a servidores especializados (Loki) para proteger el I/O y el disco transaccional.",
        "3. El Ciclo Virtuoso de Optimización: La telemetría detecta cuándo y dónde sufre la base de datos; el plan de ejecución (EXPLAIN ANALYZE) revela la causa raíz; y la indexación adecuada multiplica el rendimiento por órdenes de magnitud.",
        "4. Eficiencia de Costos: Mediante contenedores Docker e Infraestructura como Código, es posible implementar arquitecturas de observabilidad y recuperación de nivel corporativo a costo $0."
    ], font_size=14)

    prs.save(OUTPUT_PPTX)
    print(f"\n[OK] Presentacion generada con exito en: {OUTPUT_PPTX}")

if __name__ == "__main__":
    generar_presentacion_completa()
