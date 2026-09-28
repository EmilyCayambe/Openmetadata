#!/usr/bin/env python3
"""
generar_presentacion.py
=============================================================================
COMPILADOR MAESTRO DE LA PRESENTACIÓN (POWERPOINT)
Curso: Almacenamiento y Minería de Datos
=============================================================================
Este script orquesta e integra los módulos desarrollados de forma independiente
por cada integrante del equipo, garantizando que nadie modifique el código de
otro compañero:

- estilo_base.py        -> Sistema de diseño, paleta Slate Navy y helpers comunes.
- slides_comunes.py     -> Slides 1, 2, 3 (Apertura) y Slides 10, 11 (Cierre).
- slides_backup.py      -> Slides 4 y 5 (Módulo Backups & PITR) - Zaid San Lucas.
- slides_telemetria.py  -> Slides 6 y 7 (Módulo Telemetría & Loki) - Estudiante 2.
- slides_optimizacion.py-> Slides 8 y 9 (Módulo Tuning & EXPLAIN) - Estudiante 3.

Uso:
    python presentacion/generar_presentacion.py
"""

import os
import sys

# Asegurar que el directorio de presentación esté en el path de Python
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from estilo_base import create_empty_deck, save_deck_safe
from slides_comunes import agregar_slides_apertura, agregar_slides_cierre
from slides_backup import agregar_slides_backup
from slides_telemetria import agregar_slides_telemetria
from slides_optimizacion import agregar_slides_optimizacion

OUTPUT_MASTER = os.path.join(SCRIPT_DIR, "Presentacion_Telemetria_Optimizacion.pptx")

def compilar_presentacion_completa():
    print("=================================================================")
    print(" [ORQUESTADOR] COMPILANDO PRESENTACIÓN COMPLETA DESDE MÓDULOS")
    print("=================================================================")

    # 1. Crear lienzo base en blanco 16:9
    prs = create_empty_deck()

    # 2. Agregar diapositivas de apertura (Portada, Problemática, Arquitectura)
    print("-> Integrando Apertura (Slides 1 a 3)...")
    agregar_slides_apertura(prs)

    # 3. Agregar Módulo 1: Backups y Recuperación (Zaid)
    print("-> Integrando Módulo 1: Backups & PITR (Slides 4 y 5)...")
    agregar_slides_backup(prs)

    # 4. Agregar Módulo 2: Telemetría y Servidor de Logs (Compañero 2)
    print("-> Integrando Módulo 2: Telemetría & Loki (Slides 6 y 7)...")
    agregar_slides_telemetria(prs)

    # 5. Agregar Módulo 3: Optimización SQL y Benchmarks (Compañero 3)
    print("-> Integrando Módulo 3: Optimización SQL (Slides 8 y 9)...")
    agregar_slides_optimizacion(prs)

    # 6. Agregar diapositivas de cierre (Metodología del Laboratorio, Conclusiones)
    print("-> Integrando Cierre y Metodología (Slides 10 y 11)...")
    agregar_slides_cierre(prs)

    # 7. Guardar presentación maestra unificada
    destino = save_deck_safe(prs, OUTPUT_MASTER)
    print(f"\n[ÉXITO] Presentación maestra compilada con éxito en:\n{destino}")
    print("=================================================================\n")
    return destino

if __name__ == "__main__":
    compilar_presentacion_completa()