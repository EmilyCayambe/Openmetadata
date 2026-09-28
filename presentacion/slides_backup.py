#!/usr/bin/env python3
"""
slides_backup.py
=============================================================================
MÓDULO 1: ESTRATEGIAS DE BACKUP Y RECUPERACIÓN ANTE DESASTRES
Responsable: Zaid San Lucas
=============================================================================
Contenido:
- Slide 4: Estrategias de Backup (Totales, Incrementales, Diferenciales, RPO/RTO)
- Slide 5: Caso Práctico (Simulación de Pérdida DROP TABLE, WAL, LSN y PITR)
- Generación de gráfico analítico de volúmenes de respaldo.

Este archivo se puede ejecutar de forma INDEPENDIENTE para generar una vista
previa exclusiva de este módulo:
    python presentacion/slides_backup.py
"""

import os
from pptx.util import Inches
import matplotlib.pyplot as plt
import numpy as np

from estilo_base import (
    ASSETS_DIR, SCRIPT_DIR, create_empty_deck, create_base_slide,
    add_card, add_structured_item, save_deck_safe
)

def generar_grafico_backups():
    """Genera infografía conceptual de los tipos de backup y volumen transferido."""
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

def agregar_slides_backup(prs):
    """Inserta las diapositivas de Estrategias de Backup en la presentación."""
    img_backups = generar_grafico_backups()

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

if __name__ == "__main__":
    print(">>> Generando vista previa independiente del MÓDULO BACKUP...")
    preview_prs = create_empty_deck()
    agregar_slides_backup(preview_prs)
    preview_path = os.path.join(SCRIPT_DIR, "preview_modulo_backup.pptx")
    save_deck_safe(preview_prs, preview_path)
