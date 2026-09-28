#!/usr/bin/env python3
"""
slides_backup.py
=============================================================================
MÓDULO 1: ESTRATEGIAS DE BACKUP Y RECUPERACIÓN ANTE DESASTRES
Responsable: Zaid San Lucas
=============================================================================
Contenido Exhaustivo y Didáctico (5 Diapositivas):
- Slide 1 (B1): Taxonomía y Métricas de Respaldo (Full, Incremental, Diferencial, RPO/RTO)
- Slide 2 (B2): Criterios de Selección: ¿Cuándo utilizar cada método? (Escenarios y Ventanas)
- Slide 3 (B3): Anatomía Interna del WAL: Convención Hexadecimal (TLI, LogID, LSN) y pg_waldump
- Slide 4 (B4): Comandos Nativos de Producción y Parámetros Críticos (pg_dump, pg_restore, flags)
- Slide 5 (B5): Validación Práctica: Simulación de Desastre y Restauración PITR

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
    """Inserta las 5 diapositivas didácticas de Backups en la presentación."""
    img_backups = generar_grafico_backups()

    # --------------------------------------------------------------------------
    # SLIDE 1 (B1): TAXONOMÍA Y MÉTRICAS DE RESPALDO
    # --------------------------------------------------------------------------
    s1 = create_base_slide(prs, "Mecanismos de Recuperación", "Taxonomía de Backups: Totales, Incrementales y Diferenciales")

    add_card(s1, Inches(0.8), Inches(1.65), Inches(5.5), Inches(5.1), "Fundamentos de Respaldo")
    tb = s1.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.0), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Backup Total (Full):", "Copia íntegra de estructuras y datos. Base obligatoria para cualquier plan de continuidad.", 12)
    add_structured_item(tf, "Backup Incremental:", "Almacena únicamente las modificaciones ocurridas desde el respaldo previo más reciente.", 12)
    add_structured_item(tf, "Backup Diferencial:", "Acumula todas las variaciones producidas desde el último Backup Total registrado.", 12)
    add_structured_item(tf, "Métrica RPO:", "Recovery Point Objective; volumen máximo de transacciones que la organización tolera perder.", 12)
    add_structured_item(tf, "Métrica RTO:", "Recovery Time Objective; plazo máximo admisible para restablecer la operatividad normal.", 12)

    s1.shapes.add_picture(img_backups, Inches(6.6), Inches(1.8), width=Inches(5.9))

    # --------------------------------------------------------------------------
    # SLIDE 2 (B2): CRITERIOS DE DECISIÓN: ¿CUÁNDO USAR CADA TIPO?
    # --------------------------------------------------------------------------
    s2 = create_base_slide(prs, "Mecanismos de Recuperación", "Criterios de Selección: ¿Cuándo Utilizar Cada Método?")

    add_card(s2, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.1), "Escenarios Recomendados por Tipo")
    tb = s2.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Cuándo usar Backup Total:", "Ventanas semanales o mensuales de bajo tráfico (ej. domingos en la noche); indispensable antes de migraciones de esquema mayores.", 12)
    add_structured_item(tf, "Cuándo usar Backup Diferencial:", "Ejecución diaria nocturna entre semana; recomendado cuando se exige un RTO muy rápido, ya que solo se restaura el Full + último diferencial.", 12)
    add_structured_item(tf, "Cuándo usar Backup Incremental:", "Ejecución horaria o continua mediante WAL archiving; ideal para sistemas transaccionales críticos donde el RPO debe ser menor a 5 minutos.", 12)
    add_structured_item(tf, "Enfoque Híbrido Estándar:", "Full semanal + Diferencial diario + Archivado continuo de WALs en tiempo real.", 12)

    add_card(s2, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.1), "Impacto en Recursos y Recuperación")
    tb = s2.shapes.add_textbox(Inches(7.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Sobrecarga de I/O en Producción:", "El Backup Total satura lecturas en disco; el Incremental lee únicamente bloques modificados o registros WAL.", 12)
    add_structured_item(tf, "Espacio de Almacenamiento:", "El Total requiere terabytes de destino; el Incremental minimiza el uso de disco al capturar solo deltas.", 12)
    add_structured_item(tf, "Riesgo en la Restauración:", "Si un segmento incremental de la cadena se corrompe, los incrementales posteriores se vuelven inválidos.", 12)
    add_structured_item(tf, "Velocidad de Restauración (RTO):", "Diferencial restaura en 2 pasos; Incremental exige aplicar Full + Inc1 + Inc2 + ... + IncN.", 12)

    # --------------------------------------------------------------------------
    # SLIDE 3 (B3): ANATOMÍA INTERNA DEL WAL (WRITE-AHEAD LOGGING)
    # --------------------------------------------------------------------------
    s3 = create_base_slide(prs, "Arquitectura Interna", "Anatomía del WAL: Convención Hexadecimal e Inspección Interna")

    add_card(s3, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.1), "Convención Hexadecimal de 24 Caracteres")
    tb = s3.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Estructura Física:", "Cada fichero WAL tiene un tamaño inmutable de exactamente 16.0 MB (ej. 00000001000000000000001D).", 12)
    add_structured_item(tf, "Timeline ID (Primeros 8 dígitos):", "00000001 identifica la línea temporal del motor; se incrementa si una réplica es promovida a nodo maestro.", 12)
    add_structured_item(tf, "Log ID (Dígitos 9 al 16):", "00000000 indica el número de serie del ciclo lógico de registros de transacciones.", 12)
    add_structured_item(tf, "Segmento LSN (Últimos 8 dígitos):", "0000001D representa el número correlativo del segmento dentro del ciclo activo.", 12)
    add_structured_item(tf, "Principio WAL Inviolable:", "Ningún registro se persiste en las tablas de datos sin antes haberse volcado en el WAL.", 12)

    add_card(s3, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.1), "Decodificación con pg_waldump")
    tb = s3.shapes.add_textbox(Inches(7.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Utilidad Oficial:", "pg_waldump permite leer e inspeccionar los binarios WAL sin necesidad de iniciar PostgreSQL.", 12)
    add_structured_item(tf, "Resource Manager (rmgr):", "Identifica el componente del motor afectado (Heap = datos de tabla, Btree = índices, Transaction = commits).", 12)
    add_structured_item(tf, "Log Sequence Number (LSN):", "Puntero exacto en bytes (ej. 0/01000028) que marca la posición secuencial de la operación.", 12)
    add_structured_item(tf, "Transaction ID (tx):", "Número de transacción único asociado para rastrear commits, aborts y rollbacks.", 12)
    add_structured_item(tf, "Comando en Laboratorio:", "docker exec db-primary pg_waldump -n 8 /backup_storage/wal_archive/<archivo_wal>", 12)

    # --------------------------------------------------------------------------
    # SLIDE 4 (B4): COMANDOS NATIVOS DE PRODUCCIÓN Y FLAGS
    # --------------------------------------------------------------------------
    s4 = create_base_slide(prs, "Operaciones y Herramientas", "Comandos Nativos de Producción: Parámetros y Banderas Críticas")

    add_card(s4, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.1), "Generación de Respaldo (pg_dump y WAL)")
    tb = s4.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Comando Base:", "pg_dump -U admin_db -d banco_telemetria -F c -b -v -f <destino.dump>", 12)
    add_structured_item(tf, "Bandera -F c (Custom Format):", "Comprime con zlib (13 MB para 600k filas) y genera metadatos que permiten restauraciones selectivas o multi-hilo (-j).", 12)
    add_structured_item(tf, "Bandera -b (Blobs):", "Garantiza la inclusión de objetos binarios grandes sin pérdidas estructurales.", 12)
    add_structured_item(tf, "Rotación Manual de WAL:", "SELECT pg_switch_wal(); fuerza el cierre del segmento actual para su archivado inmediato.", 12)
    add_structured_item(tf, "archive_command:", "Parámetro en postgresql.conf que copia automáticamente cada segmento WAL cerrado al almacenamiento aislado.", 12)

    add_card(s4, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.1), "Procedimiento de Restauración (pg_restore)")
    tb = s4.shapes.add_textbox(Inches(7.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Comando de Restauración:", "pg_restore -U admin_db -d banco_telemetria --clean --if-exists -v <archivo.dump>", 12)
    add_structured_item(tf, "Bandera --clean:", "Emite sentencias DROP sobre tablas existentes antes de recrear las estructuras, evitando conflictos.", 12)
    add_structured_item(tf, "Bandera --if-exists:", "Evita que el proceso aborte con error si un objeto a borrar no existía previamente.", 12)
    add_structured_item(tf, "Bandera --no-owner:", "Omite comandos de asignación de propiedad original para permitir restaurar entre diferentes usuarios o entornos.", 12)
    add_structured_item(tf, "Consistencia Transaccional:", "Utiliza transacciones snapshot con nivel REPEATABLE READ para asegurar coherencia sin bloquear operaciones.", 12)

    # --------------------------------------------------------------------------
    # SLIDE 5 (B5): VALIDACIÓN PRÁCTICA: SIMULACIÓN DE DESASTRE Y PITR
    # --------------------------------------------------------------------------
    s5 = create_base_slide(prs, "Validación Práctica", "Simulación de Pérdida de Datos y Restauración de Contingencia")

    add_card(s5, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.1), "Procedimiento de la Prueba")
    tb = s5.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Fase 1 (Respaldo Base):", "Generación de dump binario comprimido de 13 MB mediante pg_dump en 3.9 segundos.", 12)
    add_structured_item(tf, "Fase 2 (Transacción Crítica):", "Registro de movimientos financieros de última hora posteriores al backup base.", 12)
    add_structured_item(tf, "Fase 3 (Desastre Simulado):", "Ejecución de sentencia destructiva accidental: DROP TABLE transacciones, cuentas, clientes CASCADE.", 12)
    add_structured_item(tf, "Fase 4 (Verificación de Pérdida):", "Consulta de catálogo donde se constata la indisponibilidad total de la información.", 12)
    add_structured_item(tf, "Fase 5 (Restauración Exitosa):", "Ejecución de procedimiento de contingencia recuperando las 600,000 filas en 5 segundos.", 12)

    add_card(s5, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.1), "Mecanismo Point-In-Time Recovery (PITR)")
    tb = s5.shapes.add_textbox(Inches(7.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Recuperación a Punto Específico:", "Combina el último Backup Total con el 'replay' secuencial de los segmentos WAL archivados.", 12)
    add_structured_item(tf, "recovery_target_time:", "Parámetro que permite detener la reproducción de logs en la hora exacta previa al error humano.", 12)
    add_structured_item(tf, "recovery_target_lsn:", "Detención en una posición de bytes exacta de LSN para máxima precisión forense.", 12)
    add_structured_item(tf, "Resiliencia Total:", "Garantiza que la empresa no pierda las transacciones del día entre el último backup y el desastre.", 12)

if __name__ == "__main__":
    print(">>> Generando vista previa independiente del MÓDULO BACKUP (5 diapositivas)...")
    preview_prs = create_empty_deck()
    agregar_slides_backup(preview_prs)
    preview_path = os.path.join(SCRIPT_DIR, "preview_modulo_backup.pptx")
    save_deck_safe(preview_prs, preview_path)
