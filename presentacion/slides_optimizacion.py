#!/usr/bin/env python3
"""
slides_optimizacion.py
=============================================================================
MÓDULO 3: OPTIMIZACIÓN DE CONSULTAS SQL – TÉCNICAS DE INDEXACIÓN
Responsable: Estudiante 3
=============================================================================
Contenido (4 Diapositivas):
- Slide 8:  Fundamentos de EXPLAIN ANALYZE
- Slide 9:  Técnicas de Indexación – Qué hacen y cuándo usarlas
- Slide 10: Índice B-Tree e Índice Compuesto – Aplicación sobre la BD
- Slide 11: Índice Hash y Bitmap Index Scan – Aplicación sobre la BD

Las demos en vivo se ejecutan desde: optimizacion/guia_indices.sql

Este archivo se puede ejecutar de forma INDEPENDIENTE para generar una vista
previa exclusiva de este módulo:
    python presentacion/slides_optimizacion.py
"""

import os
from pptx.util import Inches

from estilo_base import (
    SCRIPT_DIR, create_empty_deck, create_base_slide,
    add_card, add_structured_item, save_deck_safe
)

def agregar_slides_optimizacion(prs):
    """Inserta las diapositivas de Optimización SQL en la presentación."""

    # --------------------------------------------------------------------------
    # SLIDE 8: FUNDAMENTOS DE EXPLAIN ANALYZE
    # --------------------------------------------------------------------------
    s8 = create_base_slide(prs, "Afinamiento de Rendimiento", "Fundamentos de EXPLAIN ANALYZE")

    add_card(s8, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.1), "¿Qué es EXPLAIN ANALYZE?")
    tb = s8.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Propósito:", "Es el comando que le pide a PostgreSQL que ejecute la consulta y revele exactamente cómo la procesó internamente paso a paso.", 12)
    add_structured_item(tf, "Tiempo de Ejecución:", "Muestra el tiempo real (en milisegundos) que el motor tardó en procesar la consulta completa.", 12)
    add_structured_item(tf, "Buffers (Hit vs Read):", "Hit = la información se leyó directamente desde la RAM (rápido). Read = se tuvo que ir al disco físico a buscarla (lento, cuello de botella).", 12)
    add_structured_item(tf, "Sintaxis Utilizada:", "EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) seguido de la consulta SQL que se desea inspeccionar.", 12)

    add_card(s8, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.1), "Tipos de Escaneo que Revela")
    tb = s8.shapes.add_textbox(Inches(7.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Sequential Scan (Seq Scan):", "Recorre TODAS las filas de la tabla una por una hasta encontrar las que coinciden. Es lento en tablas grandes con búsquedas selectivas.", 12)
    add_structured_item(tf, "Index Scan:", "Usa un índice para ir directamente a las filas que necesita sin leer toda la tabla. Complejidad logarítmica O(log N).", 12)
    add_structured_item(tf, "Bitmap Heap Scan:", "Estrategia intermedia: primero construye un mapa de páginas válidas usando índices y luego lee solo esas páginas del disco.", 12)
    add_structured_item(tf, "Nodo Sort:", "Aparece cuando PostgreSQL necesita ordenar datos en memoria. Un buen índice compuesto puede eliminarlo por completo.", 12)

    # --------------------------------------------------------------------------
    # SLIDE 9: TÉCNICAS DE INDEXACIÓN – QUÉ HACEN Y CUÁNDO USARLAS
    # --------------------------------------------------------------------------
    s9 = create_base_slide(prs, "Técnicas de Indexación", "¿Qué hace cada índice y cuándo conviene usarlo?")

    add_card(s9, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.1), "Índice B-Tree e Índice Compuesto")
    tb = s9.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "B-Tree (Árbol Balanceado):", "Organiza los valores en una estructura de árbol ordenada. Cada búsqueda descarta la mitad de los datos en cada paso, por eso es logarítmico.", 12)
    add_structured_item(tf, "¿Cuándo usarlo?:", "Cuando se buscan valores exactos (=), rangos (BETWEEN, <, >) o se necesita ordenar resultados (ORDER BY). Es el más versátil y el índice por defecto.", 12)
    add_structured_item(tf, "Índice Compuesto:", "Un B-Tree que indexa dos o más columnas juntas. El orden de las columnas importa: la primera filtra y la segunda ordena.", 12)
    add_structured_item(tf, "¿Cuándo usarlo?:", "Cuando las consultas siempre filtran por una columna y ordenan por otra, como obtener las últimas transacciones de una cuenta específica.", 12)

    add_card(s9, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.1), "Índice Hash y Bitmap Index Scan")
    tb = s9.shapes.add_textbox(Inches(7.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Hash:", "Aplica una función de dispersión que convierte el valor en una posición fija. La búsqueda es directa sin recorrer una estructura de árbol.", 12)
    add_structured_item(tf, "¿Cuándo usarlo?:", "Exclusivamente para igualdad exacta (=). No funciona con rangos ni con ORDER BY. Ideal para columnas de tipo categórico (estados, tipos).", 12)
    add_structured_item(tf, "Bitmap Index Scan:", "No es un índice que se crea, sino una estrategia del planificador. Combina varios índices individuales mediante operaciones AND/OR sobre mapas de bits.", 12)
    add_structured_item(tf, "¿Cuándo aparece?:", "Cuando la consulta tiene múltiples condiciones en el WHERE (ej. dni = X OR estado = Y). PostgreSQL fusiona los mapas de bits de cada índice.", 12)

    # --------------------------------------------------------------------------
    # SLIDE 10: APLICACIÓN B-TREE Y COMPUESTO SOBRE LA BD
    # --------------------------------------------------------------------------
    s10 = create_base_slide(prs, "Aplicación Práctica", "Índice B-Tree e Índice Compuesto sobre la Base de Datos")

    add_card(s10, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.1), "Caso 1: B-Tree sobre DNI (Tabla Clientes)")
    tb = s10.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Problema:", "Buscar un cliente por su DNI obliga al motor a recorrer las 100,000 filas de la tabla completa (Sequential Scan).", 12)
    add_structured_item(tf, "Solución Aplicada:", "CREATE INDEX idx_clientes_dni_btree ON clientes USING btree (dni);", 12)
    add_structured_item(tf, "Qué Observar en EXPLAIN:", "El plan de ejecución cambia de Seq Scan a Index Scan. El número de buffers leídos baja drásticamente.", 12)
    add_structured_item(tf, "Demostración:", "Ejecutar en vivo el Caso 1 de optimizacion/guia_indices.sql y comparar los resultados antes y después.", 12)

    add_card(s10, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.1), "Caso 2: Compuesto sobre Transacciones")
    tb = s10.shapes.add_textbox(Inches(7.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Problema:", "Consultar las últimas transacciones de una cuenta genera un Seq Scan sobre toda la tabla más un Sort en memoria para ordenar por fecha.", 12)
    add_structured_item(tf, "Solución Aplicada:", "CREATE INDEX idx_transacciones_cuenta_fecha ON transacciones USING btree (cuenta_id, fecha_hora DESC);", 12)
    add_structured_item(tf, "Qué Observar en EXPLAIN:", "El nodo Sort desaparece completamente porque el índice ya entrega los datos en el orden solicitado.", 12)
    add_structured_item(tf, "Demostración:", "Ejecutar en vivo el Caso 2 de optimizacion/guia_indices.sql y verificar la eliminación del Sort.", 12)

    # --------------------------------------------------------------------------
    # SLIDE 11: APLICACIÓN HASH Y BITMAP SOBRE LA BD
    # --------------------------------------------------------------------------
    s11 = create_base_slide(prs, "Aplicación Práctica", "Índice Hash y Bitmap Index Scan sobre la Base de Datos")

    add_card(s11, Inches(0.8), Inches(1.65), Inches(5.7), Inches(5.1), "Caso 3: Hash sobre Tipo de Cuenta")
    tb = s11.shapes.add_textbox(Inches(1.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Problema:", "Filtrar cuentas por tipo (AHORROS, CORRIENTE) recorre toda la tabla porque no existe un índice sobre esa columna.", 12)
    add_structured_item(tf, "Solución Aplicada:", "CREATE INDEX idx_cuentas_tipo_hash ON cuentas USING hash (tipo_cuenta);", 12)
    add_structured_item(tf, "Qué Observar en EXPLAIN:", "Con igualdad (=) el motor usa el índice Hash. Con rango (>) lo ignora y vuelve a Seq Scan, demostrando su limitación.", 12)
    add_structured_item(tf, "Demostración:", "Ejecutar en vivo el Caso 3 de optimizacion/guia_indices.sql con igualdad y luego con rango.", 12)

    add_card(s11, Inches(6.8), Inches(1.65), Inches(5.7), Inches(5.1), "Caso 4: Bitmap Index Scan Automático")
    tb = s11.shapes.add_textbox(Inches(7.05), Inches(2.25), Inches(5.2), Inches(4.3))
    tf = tb.text_frame
    tf.word_wrap = True
    add_structured_item(tf, "Problema:", "Consultas con múltiples condiciones (WHERE dni = X OR estado = Y) no pueden resolverse con un solo índice.", 12)
    add_structured_item(tf, "Solución Observada:", "PostgreSQL combina automáticamente los índices idx_clientes_dni_btree e idx_clientes_estado mediante BitmapOr o BitmapAnd.", 12)
    add_structured_item(tf, "Qué Observar en EXPLAIN:", "Aparecen nodos BitmapOr/BitmapAnd que fusionan mapas de bits de cada índice y luego un Bitmap Heap Scan lee solo las páginas necesarias.", 12)
    add_structured_item(tf, "Demostración:", "Ejecutar en vivo el Caso 4 de optimizacion/guia_indices.sql con condiciones OR y AND.", 12)


if __name__ == "__main__":
    print(">>> Generando vista previa independiente del MÓDULO OPTIMIZACIÓN...")
    preview_prs = create_empty_deck()
    agregar_slides_optimizacion(preview_prs)
    preview_path = os.path.join(SCRIPT_DIR, "preview_modulo_optimizacion.pptx")
    save_deck_safe(preview_prs, preview_path)
