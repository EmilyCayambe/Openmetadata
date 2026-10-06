#!/usr/bin/env python3
"""Genera la presentación de Diagnóstico IA, OpenMetadata y MSP."""

import os

from estilo_base import create_empty_deck, save_deck_safe
from slides_diagnostico_ia import agregar_slides_diagnostico_ia


def main():
    presentation = create_empty_deck()
    agregar_slides_diagnostico_ia(presentation)
    destination = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Presentacion_Diagnostico_IA_OpenMetadata_MSP_Final.pptx",
    )
    return save_deck_safe(presentation, destination)


if __name__ == "__main__":
    main()