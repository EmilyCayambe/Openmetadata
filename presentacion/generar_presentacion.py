#!/usr/bin/env python3
"""
generar_presentacion.py
Generador automático de la presentación ejecutiva en PowerPoint (.pptx) para:
"Backup de Bases de Datos, Telemetría y Optimización de Consultas SQL"
Curso: Almacenamiento y Minería de Datos

Diseño:
- Sobrio, pulcro y corporativo (estilo ingeniería de software / arquitectura de datos).
- Paleta monocromática refinada Slate / Deep Navy con acento azul acero uniforme.
- Tipografía consistente (Segoe UI) con jerarquía clara: negrita únicamente en términos clave.
- Sin marcas de tiempo, sin menciones informales y con bordes neutros homogéneos.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
import matplotlib.pyplot as plt
import numpy as np

# Rutas del proyecto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
OUTPUT_PPTX = os.path.join(SCRIPT_DIR, "Presentacion_Telemetria_Optimizacion.pptx")
os.makedirs(ASSETS_DIR, exist_ok=True)

# ==============================================================================
# 1. PALETA CORPORATIVA SOBRIA ("SLATE NAVY")
# ==============================================================================
# Base sobria, fondo grafito oscuro, tarjetas neutras y un único acento azul profesional
FONT_NAME = "Segoe UI"

BG_DARK = RGBColor(15, 23, 42)         # #0F172A (Slate 900 - Fondo sobrio)
CARD_BG = RGBColor(30, 41, 59)         # #1E293B (Slate 800 - Superficie tarjetas)
CARD_BORDER = RGBColor(51, 65, 85)     # #334155 (Slate 700 - Borde uniforme y sutil)

ACCENT_BLUE = RGBColor(96, 165, 250)   # #60A5FA (Azul técnico para títulos destacados)
ACCENT_SUBTLE = RGBColor(148, 163, 184)# #94A3B8 (Gris azulado para subtítulos)

TEXT_TITLE = RGBColor(248, 250, 252)   # #F8FAFC (Blanco puro para títulos)
TEXT_BODY = RGBColor(226, 232, 240)    # #E2E8F0 (Texto claro para lectura cómoda)
TEXT_MUTED = RGBColor(148, 163, 184)   # #94A3B8 (Texto secundario para explicaciones)

# ==============================================================================
# 2. GENERADOR DE GRÁFICOS ANALÍTICOS (ESTILO SOBRIO Y REFINADO)
# ==============================================================================
def generar_grafico_paradoja_logs():
    """Genera gráfico comparativo: Crecimiento de Logs vs Crecimiento de Tabla"""
    path = os.path.join(ASSETS_DIR, "grafico_paradoja_logs.png")
    fig, ax = plt.subplots(figsize=(6.4, 4.0), facecolor='#1E293B')
    ax.set_facecolor('#1E293B')

    updates = np.array([0, 50, 100, 200, 350, 500, 750, 1000])
    tabla_mb = np.array([12.1, 12.12, 12.15, 12.18, 12.22, 12.25, 12.29, 12.33])
    logs_mb = np.array([0.1, 8.5, 18.2, 39.5, 71.0, 105.4, 162.8, 224.0])

    ax.plot(updates, logs_mb, color='#F87171', linewidth=2.5, marker='o', markersize=4.5,
            label='Logs de Transacciones y WALs (MB)', zorder=4)
    ax.plot(updates, tabla_mb, color='#38BDF8', linewidth=2.5, marker='s', markersize=4.5,
            label='Espacio de Datos en Disco (MB)', zorder=4)
    ax.fill_between(updates, logs_mb, color='#F87171', alpha=0.10)

    ax.set_title("Crecimiento de Logs vs Almacenamiento de Tabla", color='#F8FAFC',
                 fontsize=11.5, fontweight='bold', pad=14, fontfamily='sans-serif')
    ax.set_xlabel("Sentencias Transaccionales Ejecutadas (UPDATES)", color='#94A3B8', fontsize=9.5)
    ax.set_ylabel("Espacio de Almacenamiento (MB)", color='#94A3B8', fontsize=9.5)
    ax.tick_params(colors='#E2E8F0', labelsize=8.5)
    ax.grid(True, linestyle=':', alpha=0.25, color='#64748B')

    for spine in ax.spines.values():
        spine.set_color('#334155')

    legend = ax.legend(facecolor='#0F172A', edgecolor='#334155', fontsize=8.5)
    for text in legend.get_texts():
        text.set_color('#E2E8F0')

    plt.tight_layout()
    plt.savefig(path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    return path

def generar_grafico_optimizacion():
    """Genera gráfico de barras: Rendimiento Antes vs Después de Índices"""
    path = os.path.join(ASSETS_DIR, "grafico_optimizacion_benchmark.png")
    fig, ax = plt.subplots(figsize=(6.4, 4.0), facecolor='#1E293B')
    ax.set_facecolor('#1E293B')

    casos = ['Búsqueda Puntual\n(B-Tree)', 'Rango Compuesto\n(Filtro + Sort)', 'Expresión Funcional\n(LOWER)']
    sin_indice = [13.71, 28.50, 42.10]
    con_indice = [0.12, 0.45, 0.28]

    x = np.arange(len(casos))
    width = 0.32

    rects1 = ax.bar(x - width/2, sin_indice, width, label='Sin Índice (Sequential Scan)',
                    color='#F87171', edgecolor='#1E293B', zorder=3)
    rects2 = ax.bar(x + width/2, con_indice, width, label='Con Índice Optimizado (Index Scan)',
                    color='#38BDF8', edgecolor='#1E293B', zorder=3)

    ax.set_title("Impacto de Optimización: Latencia de Ejecución (ms)", color='#F8FAFC',
                 fontsize=11.5, fontweight='bold', pad=14, fontfamily='sans-serif')
    ax.set_ylabel("Tiempo de Ejecución (ms)", color='#94A3B8', fontsize=9.5)
    ax.set_xticks(x)
    ax.set_xticklabels(casos, color='#E2E8F0', fontsize=8.5)
    ax.tick_params(colors='#E2E8F0', labelsize=8.5)
    ax.grid(True, axis='y', linestyle=':', alpha=0.25, color='#64748B')

    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f'{h:.1f} ms', xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                    color='#FCA5A5', fontsize=8, fontweight='bold')

    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f'{h:.2f} ms', xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                    color='#7DD3FC', fontsize=8, fontweight='bold')

    for spine in ax.spines.values():
        spine.set_color('#334155')

    legend = ax.legend(facecolor='#0F172A', edgecolor='#334155', fontsize=8.5)
    for text in legend.get_texts():
        text.set_color('#E2E8F0')

    plt.tight_layout()
    plt.savefig(path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    return path

def generar_diagrama_backups():
    """Genera infografía conceptual de los tipos de backup y RTO"""
    path = os.path.join(ASSETS_DIR, "grafico_tipos_backups.png")
    fig, ax = plt.subplots(figsize=(6.4, 4.0), facecolor='#1E293B')
    ax.set_facecolor('#1E293B')

    dias = ['Día 1', 'Día 2', 'Día 3', 'Día 4', 'Día 5']
    full = [100, 0, 0, 0, 0]
    incr = [0, 15, 18, 22, 25]
    diff = [0, 15, 33, 55, 80]

    x = np.arange(len(dias))
    width = 0.28

    ax.bar(x - width, full, width, label='Full Backup (Base completa)', color='#60A5FA', zorder=3)
    ax.bar(x, incr, width, label='Incremental (Cambios del período)', color='#38BDF8', zorder=3)
    ax.bar(x + width, diff, width, label='Diferencial (Acumulado desde Full)', color='#94A3B8', zorder=3)

    ax.set_title("Estrategias de Respaldo: Volumen Transferido por Período", color='#F8FAFC',
                 fontsize=11.5, fontweight='bold', pad=14, fontfamily='sans-serif')
    ax.set_ylabel("Volumen Estimado (MB)", color='#94A3B8', fontsize=9.5)
    ax.set_xticks(x)
    ax.set_xticklabels(dias, color='#E2E8F0', fontsize=8.5)
    ax.tick_params(colors='#E2E8F0', labelsize=8.5)
    ax.grid(True, axis='y', linestyle=':', alpha=0.25, color='#64748B')

    for spine in ax.spines.values():
        spine.set_color('#334155')

    legend = ax.legend(facecolor='#0F172A', edgecolor='#334155', fontsize=8.5)
    for text in legend.get_texts():
        text.set_color('#E2E8F0')

    plt.tight_layout()
    plt.savefig(path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    return path

# ==============================================================================
# 3. HELPERS DE COMPOSICIÓN PPTX (TIPOGRAFÍA SEGOE UI Y JERARQUÍA PROFESIONAL)
# ==============================================================================
def create_base_slide(prs, category_tag="", title_text=""):
    """Crea una diapositiva con fondo uniforme Slate Navy y cabecera sobria."""
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)

    # Fondo neutro oscuro
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = BG_DARK
    bg.line.fill.background()

    # Tag de categoría superior (sin barras multicolores)
    if category_tag:
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(11.7), Inches(0.30))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_tag.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_BLUE
        p_cat.font.name = FONT_NAME

    # Título principal de la diapositiva
    if title_text:
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.70))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_TITLE
        p_title.font.name = FONT_NAME

    return slide

def add_card(slide, left, top, width, height, title=""):
    """Crea una tarjeta contenedora con borde neutro Slate."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = CARD_BORDER
    card.line.width = Pt(1.0)
    card.shadow.inherit = False

    if title:
        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.18), width - Inches(0.5), Inches(0.45))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = ACCENT_BLUE
        p.font.name = FONT_NAME
    return card

def add_structured_item(tf, bold_prefix, normal_text, font_size=12):
    """
    Añade un punto con formato tipográfico profesional:
    - Negrita únicamente en el concepto o término clave.
    - Texto regular desaturado para la explicación.
    """
    p = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
    p.space_after = Pt(7)
    p.space_before = Pt(2)

    # Viñeta discreta
    r_bullet = p.add_run()
    r_bullet.text = "•  "
    r_bullet.font.bold = False
    r_bullet.font.color.rgb = ACCENT_BLUE
    r_bullet.font.size = Pt(font_size)
    r_bullet.font.name = FONT_NAME

    # Concepto clave en negrita
    if bold_prefix:
        r_bold = p.add_run()
        r_bold.text = bold_prefix + (" " if not bold_prefix.endswith(":") else " ")
        r_bold.font.bold = True
        r_bold.font.color.rgb = TEXT_BODY
        r_bold.font.size = Pt(font_size)
        r_bold.font.name = FONT_NAME

    # Detalle en texto normal
    if normal_text:
        r_norm = p.add_run()
        r_norm.text = normal_text
        r_norm.font.bold = False
        r_norm.font.color.rgb = TEXT_MUTED
        r_norm.font.size = Pt(font_size)
        r_norm.font.name = FONT_NAME

# ==============================================================================
# 4. CONSTRUCCIÓN DE LAS DIAPOSITIVAS PROFESIONALES
# ==============================================================================
def generar_presentacion_completa():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    print(">>> Generando gráficos analíticos...")
    img_paradoja = generar_grafico_paradoja_logs()
    img_optimizacion = generar_grafico_optimizacion()
    img_backups = generar_diagrama_backups()

    print(">>> Construyendo diapositivas ejecutivas...")

    # --------------------------------------------------------------------------
    # SLIDE 1: PORTADA
    # --------------------------------------------------------------------------
    s1 = prs.slides.add_slide(prs.slide_layouts[6])
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = BG_DARK
    bg1.line.fill.background()

    # Cabecera institucional
    cat_b = s1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(0.4))
    tf_c = cat_b.text_frame
    p_c = tf_c.paragraphs[0]
    p_c.text = "ALMACENAMIENTO Y MINERÍA DE DATOS"
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = ACCENT_BLUE
    p_c.font.name = FONT_NAME

    # Título principal
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.9), Inches(11.7), Inches(2.2))
    tf = t_box.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "Backups, Telemetría y Optimización SQL"
    p1.font.size = Pt(34)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_TITLE
    p1.font.name = FONT_NAME

    p2 = tf.add_paragraph()
    p2.text = "Arquitectura Desacoplada, Resiliencia y Análisis de Rendimiento en Bases de Datos Relacionales"
    p2.font.size = Pt(16)
    p2.font.color.rgb = ACCENT_SUBTLE
    p2.font.name = FONT_NAME
    p2.space_before = Pt(8)

    # Tarjeta de contexto
    add_card(s1, Inches(0.8), Inches(4.5), Inches(5.6), Inches(2.1), "Marco del Proyecto")
    tb1 = s1.shapes.add_textbox(Inches(1.05), Inches(5.1), Inches(5.1), Inches(1.3))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    add_structured_item(tf1, "Nivel Académico:", "8vo Ciclo de Ingeniería de Sistemas", font_size=12)
    add_structured_item(tf1, "Paradigma:", "Infraestructura como Código (IaC) con Docker", font_size=12)
    add_structured_item(tf1, "Motor:", "PostgreSQL 16 Enterprise con Telemetría Desacoplada", font_size=12)

    # Tarjeta de equipo
    add_card(s1, Inches(6.8), Inches(4.5), Inches(5.7), Inches(2.1), "Equipo de Investigación")
    tb2 = s1.shapes.add_textbox(Inches(7.05), Inches(5.1), Inches(5.2), Inches(1.3))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    add_structured_item(tf2, "Integrantes:", "Zaid San Lucas y equipo de proyecto", font_size=12)
    add_structured_item(tf2, "Áreas de Demostración:", "Respaldo continuo, observabilidad y afinamiento SQL", font_size=12)
    add_structured_item(tf2, "Entorno de Pruebas:", "Contenedores aislados y reproducibles", font_size=12)

    # --------------------------------------------------------------------------
    # SLIDE 2: PROBLEMÁTICA Y OBJETIVOS
    # --------------------------------------------------------------------------
    s2 = create_base_slide(prs, "Contexto y Desafíos", "¿Por qué fallan las bases de datos en producción?")

    add_card(s2, Inches(0.8), Inches(1.65), Inches(3.6), Inches(5.1), "1. Pérdida Crítica de Datos")
    tb = s2.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Riesgo Operativo:", "Fallas físicas de disco, corrupción o sentencias destructivas accidentales.", 12)
    add_structured_item(tf, "Limitación Tradicional:", "Los backups lógicos diarios dejan ventanas de pérdida de varias horas.", 12)
    add_structured_item(tf, "Objetivo:", "Alcanzar un RPO cercano a cero mediante la captura continua de transacciones.", 12)

    add_card(s2, Inches(4.8), Inches(1.65), Inches(3.6), Inches(5.1), "2. Saturación por Logs")
    tb = s2.shapes.add_textbox(Inches(5.0), Inches(2.3), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "La Paradoja:", "Cada sentencia genera registros de auditoría y WAL; los logs crecen más rápido que las tablas.", 12)
    add_structured_item(tf, "Competencia de I/O:", "Almacenar logs en el mismo disco transaccional penaliza las consultas de clientes.", 12)
    add_structured_item(tf, "Objetivo:", "Desacoplar la ingesta hacia un servidor de observabilidad dedicado.", 12)

    add_card(s2, Inches(8.8), Inches(1.65), Inches(3.7), Inches(5.1), "3. Latencia en Consultas")
    tb = s2.shapes.add_textbox(Inches(9.0), Inches(2.3), Inches(3.3), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Degradación:", "Tablas con cientos de miles de filas colapsan en memoria ante escaneos secuenciales.", 12)
    add_structured_item(tf, "Anti-patrones:", "Uso inadecuado de funciones en cláusulas WHERE que invalidan índices estándar.", 12)
    add_structured_item(tf, "Objetivo:", "Reducir latencias de 15ms a 0.1ms mediante árboles B-Tree y tuning asistido.", 12)

    # --------------------------------------------------------------------------
    # SLIDE 3: ARQUITECTURA TÉCNICA
    # --------------------------------------------------------------------------
    s3 = create_base_slide(prs, "Infraestructura", "Arquitectura Desacoplada en Contenedores")

    add_card(s3, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.1), "Topología de Servicios Aislados")
    tb = s3.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "db-primary (PostgreSQL 16):", "Motor transaccional central con 600,000 registros sintéticos y logging activo.", 12)
    add_structured_item(tf, "promtail-agent:", "Agente de recolección en streaming que lee logs continuos sin impactar el motor.", 12)
    add_structured_item(tf, "loki-server:", "Servidor desacoplado especializado en la indexación comprimida de telemetría.", 12)
    add_structured_item(tf, "grafana-dashboard:", "Capa visual para monitoreo de QPS, errores y rendimiento en tiempo real.", 12)
    add_structured_item(tf, "backup_storage:", "Volumen de almacenamiento aislado para dumps completos y archivos WAL.", 12)

    add_card(s3, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.1), "Criterios de Diseño Arquitectónico")
    tb = s3.shapes.add_textbox(Inches(7.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Aislamiento de I/O:", "Las consultas de análisis de logs no consumen el ancho de banda del almacenamiento transaccional.", 12)
    add_structured_item(tf, "Análisis Post-Mortem:", "Si la base de datos se detiene o sufre corrupción, los registros de auditoría siguen accesibles en Loki.", 12)
    add_structured_item(tf, "Cero Presupuesto:", "Implementación 100% libre de costos de nube, totalmente reproducible en cualquier equipo con Docker.", 12)
    add_structured_item(tf, "Consistencia:", "Configuraciones predefinidas en código evitan inconsistencias entre entornos de desarrollo.", 12)

    # --------------------------------------------------------------------------
    # SLIDE 4: ESTRATEGIAS DE RESPALDO
    # --------------------------------------------------------------------------
    s4 = create_base_slide(prs, "Mecanismos de Recuperación", "Estrategias de Backup: Totales, Incrementales y Diferenciales")

    add_card(s4, Inches(0.8), Inches(1.65), Inches(5.5), Inches(5.1), "Fundamentos de Respaldo")
    tb = s4.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.0), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Backup Total (Full):", "Copia completa de estructuras y datos. Base indispensable para cualquier esquema de contingencia.", 12)
    add_structured_item(tf, "Backup Incremental:", "Almacena únicamente las modificaciones ocurridas desde el respaldo previo más reciente.", 12)
    add_structured_item(tf, "Backup Diferencial:", "Acumula todas las variaciones producidas desde el último Backup Total registrado.", 12)
    add_structured_item(tf, "Métrica RPO:", "Objetivo de Punto de Recuperación; define el volumen máximo de transacciones que la organización tolera perder.", 12)
    add_structured_item(tf, "Métrica RTO:", "Objetivo de Tiempo de Recuperación; plazo admisible para restablecer la operatividad normal.", 12)

    s4.shapes.add_picture(img_backups, Inches(6.6), Inches(1.8), width=Inches(5.9))

    # --------------------------------------------------------------------------
    # SLIDE 5: CASO PRÁCTICO: RECUPERACIÓN ANTE DESASTRES
    # --------------------------------------------------------------------------
    s5 = create_base_slide(prs, "Validación Práctica", "Simulación de Pérdida de Datos y Restauración de Contingencia")

    add_card(s5, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.1), "Procedimiento de la Prueba")
    tb = s5.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Fase 1 (Respaldo Base):", "Generación de dump binario comprimido de 13 MB mediante pg_dump en 5.2 segundos.", 12)
    add_structured_item(tf, "Fase 2 (Transacción Crítica):", "Registro de movimientos financieros de última hora posteriores al backup base.", 12)
    add_structured_item(tf, "Fase 3 (Desastre Simulado):", "Ejecución de sentencia destructiva accidental: DROP TABLE transacciones CASCADE.", 12)
    add_structured_item(tf, "Fase 4 (Verificación de Pérdida):", "Consulta de catálogo donde se constata la indisponibilidad total de la información.", 12)
    add_structured_item(tf, "Fase 5 (Restauración Exitosa):", "Ejecución de procedimiento de contingencia recuperando las 600,000 filas en 6 segundos.", 12)

    add_card(s5, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.1), "Mecanismo Interno: WAL y LSN")
    tb = s5.shapes.add_textbox(Inches(7.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Write-Ahead Logging:", "Ningún cambio se escribe en las páginas de datos sin haber sido persistido antes en el WAL.", 12)
    add_structured_item(tf, "Log Sequence Number (LSN):", "Identificador único y secuencial asignado a cada transacción en el sistema.", 12)
    add_structured_item(tf, "Archivado Activo:", "PostgreSQL segmenta el log en ficheros de 16 MB y los transfiere de forma segura a storage aislado.", 12)
    add_structured_item(tf, "Point-In-Time Recovery (PITR):", "Permite reproducir la secuencia de transacciones hasta el segundo exacto previo a la falla.", 12)

    # --------------------------------------------------------------------------
    # SLIDE 6: OBSERVABILIDAD Y TELEMETRÍA
    # --------------------------------------------------------------------------
    s6 = create_base_slide(prs, "Observabilidad", "Telemetría de Consultas y Almacenamiento Centralizado")

    add_card(s6, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.1), "Dimensiones de la Telemetría")
    tb = s6.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Más allá del Hardware:", "No se limita al uso de CPU o memoria; audita cada sentencia ejecutada por clientes y aplicaciones.", 12)
    add_structured_item(tf, "Throughput (QPS):", "Mide el volumen de operaciones por segundo y detecta picos de demanda inusuales.", 12)
    add_structured_item(tf, "Composición DML:", "Distribución entre consultas de lectura (SELECT) y operaciones de escritura (INSERT, UPDATE).", 12)
    add_structured_item(tf, "Alertas Tempranas:", "Identificación inmediata de bloqueos (locks), transacciones canceladas y rollbacks.", 12)

    add_card(s6, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.1), "Eficiencia de Grafana Loki")
    tb = s6.shapes.add_textbox(Inches(7.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Indexación por Metadatos:", "A diferencia de motores convencionales, Loki solo indexa etiquetas; reduce el consumo de RAM hasta un 90%.", 12)
    add_structured_item(tf, "Consumo No Invasivo:", "Promtail recopila logs en streaming sin abrir bloqueos de tabla ni interferir en sesiones activas.", 12)
    add_structured_item(tf, "Visibilidad Central:", "Dashboards dinámicos permiten correlacionar latencias de consultas con eventos del motor.", 12)
    add_structured_item(tf, "Retención Independiente:", "Políticas de archivado de logs sin comprometer el ciclo de vida de los datos transaccionales.", 12)

    # --------------------------------------------------------------------------
    # SLIDE 7: ANÁLISIS DE CRECIMIENTO: DATOS VS LOGS
    # --------------------------------------------------------------------------
    s7 = create_base_slide(prs, "Diagnóstico Experimental", "Comportamiento del Almacenamiento: Datos vs Logs Transaccionales")

    add_card(s7, Inches(0.8), Inches(1.65), Inches(5.5), Inches(5.1), "Hallazgos de la Simulación")
    tb = s7.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.0), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Condición de Prueba:", "Ejecución continua de 500 sentencias UPDATE consecutivas sobre una única fila de saldo.", 12)
    add_structured_item(tf, "Resultado en Tablas:", "El tamaño físico de la tabla en disco se mantiene invariable (~12.1 MB).", 12)
    add_structured_item(tf, "Resultado en Logs:", "Se emitieron 500 registros WAL de 16 MB y cientos de entradas de auditoría hacia Loki.", 12)
    add_structured_item(tf, "Conclusión Crítica:", "El almacenamiento de logs crece en función de la actividad operativa, no del número de filas.", 12)
    add_structured_item(tf, "Principio Rector:", "La separación de discos e instancias de log es indispensable para evitar incidentes por disco lleno.", 12)

    s7.shapes.add_picture(img_paradoja, Inches(6.6), Inches(1.8), width=Inches(5.9))

    # --------------------------------------------------------------------------
    # SLIDE 8: OPTIMIZACIÓN DE CONSULTAS SQL
    # --------------------------------------------------------------------------
    s8 = create_base_slide(prs, "Afinamiento de Rendimiento", "Análisis de Planes de Ejecución y Métricas de E/S")

    add_card(s8, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.1), "Fundamentos de EXPLAIN ANALYZE")
    tb = s8.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Tiempo de Ejecución:", "Medición cronométrica real del procesamiento interno en el motor de la base de datos.", 12)
    add_structured_item(tf, "Buffers (Hit vs Read):", "Hit indica lectura directa en memoria RAM; Read representa lectura física de disco (cuello de botella de E/S).", 12)
    add_structured_item(tf, "Sequential Scan (Seq Scan):", "Recorrido exhaustivo de cada página de la tabla. Ineficiente para búsquedas selectivas sobre grandes volúmenes.", 12)
    add_structured_item(tf, "Index Scan:", "Acceso selectivo mediante estructuras balanceadas B-Tree con complejidad logarítmica O(log N).", 12)

    add_card(s8, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.1), "Técnicas de Indexación Aplicadas")
    tb = s8.shapes.add_textbox(Inches(7.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Índice B-Tree Único:", "Búsqueda directa por documento de identidad; evita el escaneo de 100,000 filas.", 12)
    add_structured_item(tf, "Índice Compuesto Multicolumna:", "Indexación simultánea de cuenta y fecha; elimina la necesidad de ordenamiento en memoria (Sort).", 12)
    add_structured_item(tf, "Índice Basado en Expresiones:", "Creación sobre funciones de transformación (ej. LOWER); neutraliza anti-patrones en el WHERE.", 12)
    add_structured_item(tf, "Auditoría con pg_stat_statements:", "Inspección acumulada para identificar las 10 consultas más lentas del sistema global.", 12)

    # --------------------------------------------------------------------------
    # SLIDE 9: BENCHMARK DE RENDIMIENTO (EXPLAIN)
    # --------------------------------------------------------------------------
    s9 = create_base_slide(prs, "Resultados Comparativos", "Impacto de la Optimización: De Sequential Scan a Index Scan")

    add_card(s9, Inches(0.8), Inches(1.65), Inches(5.5), Inches(5.1), "Métricas de Desempeño")
    tb = s9.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.0), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Caso 1 (Búsqueda por DNI):", "La latencia se redujo de 13.71 ms a 0.12 ms; las lecturas pasaron de 1,301 bloques a 4 bloques (mejora >110x).", 12)
    add_structured_item(tf, "Caso 2 (Cuentas y Fechas):", "El índice compuesto evitó el algoritmo Quicksort en memoria, disminuyendo el tiempo de 28.5 ms a 0.45 ms.", 12)
    add_structured_item(tf, "Caso 3 (Uso de LOWER):", "La consulta no utilizaba el índice estándar por evaluación en fila; el índice funcional redujo la espera de 42.1 ms a 0.28 ms.", 12)
    add_structured_item(tf, "Eficiencia General:", "Menor contención de memoria compartida y liberación inmediata de conexiones en el pool.", 12)

    s9.shapes.add_picture(img_optimizacion, Inches(6.6), Inches(1.8), width=Inches(5.9))

    # --------------------------------------------------------------------------
    # SLIDE 10: METODOLOGÍA DEL LABORATORIO EXPERIMENTAL (SOBRIA, TÉCNICA)
    # --------------------------------------------------------------------------
    s10 = create_base_slide(prs, "Metodología Experimental", "Flujo Integrado de Demostración del Laboratorio")

    add_card(s10, Inches(0.8), Inches(1.65), Inches(3.6), Inches(5.1), "Fase 1: Línea Base y Respaldo")
    tb = s10.shapes.add_textbox(Inches(1.0), Inches(2.3), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Poblado Inicial:", "Generación masiva de 600,000 registros sintéticos en PostgreSQL mediante funciones de memoria.", 12)
    add_structured_item(tf, "Respaldo Completo:", "Ejecución de snapshot inicial en formato comprimido dentro del almacenamiento aislado.", 12)
    add_structured_item(tf, "Recuperación PITR:", "Simulación de incidente destructivo y validación de consistencia transaccional tras restaurar.", 12)

    add_card(s10, Inches(4.8), Inches(1.65), Inches(3.6), Inches(5.1), "Fase 2: Telemetría y Carga")
    tb = s10.shapes.add_textbox(Inches(5.0), Inches(2.3), Inches(3.2), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Inyección Concurrente:", "Simulación de tráfico transaccional continuo (lecturas, transferencias y rollbacks).", 12)
    add_structured_item(tf, "Transmisión en Streaming:", "Captura en tiempo real de eventos con Promtail hacia el repositorio de Loki.", 12)
    add_structured_item(tf, "Monitoreo en Vivo:", "Inspección de curvas de QPS, patrones de escritura y registro de errores en Grafana.", 12)

    add_card(s10, Inches(8.8), Inches(1.65), Inches(3.7), Inches(5.1), "Fase 3: Diagnóstico y Tuning")
    tb = s10.shapes.add_textbox(Inches(9.0), Inches(2.3), Inches(3.3), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Detección de Cuellos:", "Identificación de sentencias costosas reportadas por telemetría y pg_stat_statements.", 12)
    add_structured_item(tf, "Análisis de Planes:", "Evaluación de costos y lecturas de bloques de disco mediante EXPLAIN ANALYZE.", 12)
    add_structured_item(tf, "Verificación de Índices:", "Constatación inmediata de la caída drástica en la latencia tras crear las estructuras.", 12)

    # --------------------------------------------------------------------------
    # SLIDE 11: CONCLUSIONES
    # --------------------------------------------------------------------------
    s11 = create_base_slide(prs, "Síntesis Ejecutiva", "Conclusiones y Recomendaciones de Arquitectura")

    add_card(s11, Inches(0.8), Inches(1.65), Inches(11.7), Inches(5.1), "Principios Fundamentales para Entornos Empresariales")
    tb = s11.shapes.add_textbox(Inches(1.1), Inches(2.3), Inches(11.1), Inches(4.2))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "1. Continuidad Operativa:",
                        "Los respaldos estáticos son insuficientes para sistemas de alta disponibilidad; el archivado continuo de transacciones (WAL) es indispensable para minimizar el RPO ante contingencias críticas.", 13)
    add_structured_item(tf, "2. Aislamiento de Observabilidad:",
                        "La telemetría genera un volumen de datos superior al del propio negocio; su desacoplamiento a servidores dedicados (Loki) salvaguarda el rendimiento de disco y la CPU de producción.", 13)
    add_structured_item(tf, "3. Diagnóstico Científico:",
                        "La optimización de bases de datos requiere evidencia cuantitativa; la telemetría señala dónde ocurren las demoras, y el plan de ejecución revela las causas a nivel de bloques de almacenamiento.", 13)
    add_structured_item(tf, "4. Viabilidad con Código Abierto:",
                        "Mediante contenedores y herramientas open source (PostgreSQL, Loki, Grafana), es factible desplegar una plataforma de resiliencia y monitoreo de nivel corporativo con costo de infraestructura nulo.", 13)

    try:
        prs.save(OUTPUT_PPTX)
        print(f"\n[OK] Presentacion generada con exito en: {OUTPUT_PPTX}")
    except PermissionError:
        fallback = os.path.join(SCRIPT_DIR, "Presentacion_Telemetria_Optimizacion_Actualizada.pptx")
        prs.save(fallback)
        print(f"\n[OK] El archivo original esta abierto en PowerPoint. Se genero la version actualizada en: {fallback}")

if __name__ == "__main__":
    generar_presentacion_completa()