#!/usr/bin/env python3
"""
slides_telemetria.py
=============================================================================
MÓDULO 2: OBSERVABILIDAD Y TELEMETRÍA EN SERVIDOR DESACOPLADO
Responsable: Estudiante 2
=============================================================================
Contenido:
- Slide 6: Telemetría de Consultas y Almacenamiento Centralizado (Loki + Promtail + Grafana)
- Slide 7: Diagnóstico Experimental: Datos vs Logs (La Paradoja de los Logs)
- Generación de gráfico analítico de crecimiento de logs vs tablas.

Este archivo se puede ejecutar de forma INDEPENDIENTE para generar una vista
previa exclusiva de este módulo:
    python presentacion/slides_telemetria.py
"""

import os
from pptx.util import Inches
import matplotlib.pyplot as plt
import numpy as np

from estilo_base import (
    ASSETS_DIR, SCRIPT_DIR, create_empty_deck, create_base_slide,
    add_card, add_structured_item, save_deck_safe
)

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

def agregar_slides_telemetria(prs):
    """Inserta las diapositivas de Telemetría en la presentación."""
    img_paradoja = generar_grafico_paradoja_logs()

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

if __name__ == "__main__":
    print(">>> Generando vista previa independiente del MÓDULO TELEMETRÍA...")
    preview_prs = create_empty_deck()
    agregar_slides_telemetria(preview_prs)
    preview_path = os.path.join(SCRIPT_DIR, "preview_modulo_telemetria.pptx")
    save_deck_safe(preview_prs, preview_path)
