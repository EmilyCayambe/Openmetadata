#!/usr/bin/env python3
"""
slides_comunes.py
Módulo de diapositivas comunes de la presentación:
- Apertura: Portada, Problemática y Objetivos, Arquitectura Técnica.
- Cierre: Metodología Experimental del Laboratorio, Conclusiones Ejecutivas.
"""

from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from estilo_base import (
    BG_DARK, FONT_NAME, ACCENT_BLUE, ACCENT_SUBTLE, TEXT_TITLE,
    create_base_slide, add_card, add_structured_item
)

def agregar_slides_apertura(prs):
    """Genera las diapositivas 1, 2 y 3 (Portada, Problemática, Arquitectura)."""
    # --------------------------------------------------------------------------
    # SLIDE 1: PORTADA
    # --------------------------------------------------------------------------
    s1 = prs.slides.add_slide(prs.slide_layouts[6])
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = BG_DARK
    bg1.line.fill.background()

    cat_b = s1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(0.4))
    tf_c = cat_b.text_frame
    p_c = tf_c.paragraphs[0]
    p_c.text = "ALMACENAMIENTO Y MINERÍA DE DATOS"
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = ACCENT_BLUE
    p_c.font.name = FONT_NAME

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

def agregar_slides_cierre(prs):
    """Genera las diapositivas 10 y 11 (Metodología Experimental y Conclusiones)."""
    # --------------------------------------------------------------------------
    # SLIDE 10: METODOLOGÍA DEL LABORATORIO EXPERIMENTAL
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
