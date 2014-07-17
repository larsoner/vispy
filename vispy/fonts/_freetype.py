# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

# Use freetype to get glyph bitmaps

import sys
import numpy as np

from ..ext.freetype import (FT_LOAD_RENDER, FT_LOAD_NO_HINTING,
                            FT_LOAD_NO_AUTOHINT, Face)


# Convert face to filename
if sys.platform.startswith('linux'):
    from ..ext.fontconfig import find_font
elif sys.platform.startswith('win'):
    from ._win32 import find_font  # noqa, analysis:ignore
else:
    raise NotImplementedError

_font_dict = {}


def _load_font(face, size, bold, italic):
    key = '%s-%s-%s-%s' % (face, size, bold, italic)
    if key in _font_dict:
        return _font_dict[key]
    fname = find_font(face, size, bold, italic)
    font = Face(fname)
    _font_dict[key] = font
    return font


def _load_glyph(f, char, glyphs_dict):
    """Load glyph from font into dict"""
    freetype_flags = FT_LOAD_RENDER | FT_LOAD_NO_HINTING | FT_LOAD_NO_AUTOHINT
    face = _load_font(f['face'], f['size'], f['bold'], f['italic'])
    face.set_char_size(f['size'] * 64)
    # get the character of interest
    face.load_char(char, freetype_flags)
    bitmap = face.glyph.bitmap
    width = face.glyph.bitmap.width
    height = face.glyph.bitmap.rows
    bitmap = np.array(bitmap.buffer)
    w0 = bitmap.size // height if bitmap.size > 0 else 0
    bitmap.shape = (height, w0)
    bitmap = bitmap[:, :width].astype(np.ubyte)

    left = face.glyph.bitmap_left
    top = face.glyph.bitmap_top
    advance = face.glyph.advance.x / 64.
    glyph = dict(char=char, offset=(left, top), bitmap=bitmap,
                 advance=advance, kerning={})
    glyphs_dict[char] = glyph
    # Generate kerning
    face.set_char_size(f['size'] * 64)
    for other_char, other_glyph in glyphs_dict.items():
        kerning = face.get_kerning(other_char, char)
        glyph['kerning'][other_char] = kerning.x / 64.0
        kerning = face.get_kerning(char, other_char)
        other_glyph['kerning'][char] = kerning.x / 64.0
