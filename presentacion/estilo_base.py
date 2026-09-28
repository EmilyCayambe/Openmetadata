#!/usr/bin/env python3
"""
estilo_base.py
=============================================================================
SISTEMA DE DISEÑO Y GUÍA DE ESTILOS PARA LA PRESENTACIÓN (POWERPOINT)
Curso: Almacenamiento y Minería de Datos
=============================================================================

REGLAS DE DISEÑO PARA CUALQUIER INTEGRANTE O AGENTE IA:
1. Tipografía Única: "Segoe UI".
2. Jerarquía de Negritas:
   - Títulos en negrita (22-34 pt).
   - En viñetas/listas: SOLO el concepto inicial va en negrita (ej: "•  Concepto Clave:").
   - La explicación va SIEMPRE en texto regular y color desaturado (TEXT_MUTED).
3. Paleta Sobria ("Slate Navy"):
   - Prohibido usar bordes multicolores (rojos, verdes, amarillos, rosas).
   - Todos los bordes de tarjeta deben usar CARD_BORDER (#334155) con grosor fino (1.0 pt).
   - Fondos: BG_DARK (#0F172A) para lienzo general, CARD_BG (#1E293B) para tarjetas.
   - Acentos: ACCENT_BLUE (#60A5FA) para títulos destacados y viñetas.
4. Títulos Limpios:
   - Prohibido incluir nombres de estudiantes o tiempos de exposición en títulos de slides.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Directorios globales
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Tipografía estándar
FONT_NAME = "Segoe UI"

# Paleta Slate Navy (Sobria y Corporativa)
BG_DARK = RGBColor(15, 23, 42)          # #0F172A (Fondo general Slate 900)
CARD_BG = RGBColor(30, 41, 59)          # #1E293B (Superficie tarjetas Slate 800)
CARD_BORDER = RGBColor(51, 65, 85)      # #334155 (Borde neutro Slate 700)

ACCENT_BLUE = RGBColor(96, 165, 250)    # #60A5FA (Azul técnico para títulos y viñetas)
ACCENT_SUBTLE = RGBColor(148, 163, 184) # #94A3B8 (Gris azulado para subtítulos)

TEXT_TITLE = RGBColor(248, 250, 252)    # #F8FAFC (Blanco puro para títulos)
TEXT_BODY = RGBColor(226, 232, 240)     # #E2E8F0 (Texto claro para términos clave)
TEXT_MUTED = RGBColor(148, 163, 184)    # #94A3B8 (Texto regular desaturado para lectura)

def create_empty_deck():
    """Inicializa una presentación en blanco configurada en formato panorámico 16:9."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs

def create_base_slide(prs, category_tag="", title_text=""):
    """
    Crea una diapositiva con fondo uniforme Slate Navy y cabecera sobria.
    """
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

def save_deck_safe(prs, target_path):
    """
    Guarda la presentación. Si está abierta en PowerPoint (PermissionError),
    guarda automáticamente una copia con sufijo '_preview.pptx' o '_actualizada.pptx'.
    """
    try:
        prs.save(target_path)
        print(f"[OK] Presentacion guardada: {target_path}")
        return target_path
    except PermissionError:
        base, ext = os.path.splitext(target_path)
        fallback = f"{base}_preview{ext}"
        prs.save(fallback)
        print(f"[AVISO] El archivo original esta bloqueado por PowerPoint.")
        print(f"[OK] Se guardo copia alternativa en: {fallback}")
        return fallback
