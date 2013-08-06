# -*- coding: utf-8 -*-
# Copyright (c) 2013, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" Definition of shader classes.

This code is inspired by similar classes from Pygly.

"""

from __future__ import print_function, division, absolute_import

import sys

import numpy as np

from vispy import gl
from . import GLObject, push_enable, pop_enable, ext_available

if sys.version_info > (3,):
    basestring = str



class BaseShader(GLObject):
    """ Abstract shader class.
    """
    
    def __init__(self, type, source=None):
        
        # Check and store type
        if type not in [gl.GL_VERTEX_SHADER, gl.GL_FRAGMENT_SHADER]:
            raise ValueError('Type must be vertex or fragment shader.')
        self._type = type
        
        self._handle = 0
        self._compiled = 0  # 0: not compiled, 1: compile tried, 2: compile success 
        self._description = None
        self.set_source(source)
    
    
    def _delete(self):
        gl.glDeleteShader(self._handle)
    
    
    def set_source(self, source):
        """ Set the source of the shader.
        """
        self._source = source
        self._compiled = 0  # force recompile 
        # Try to get description from first line
        # EXPERIMENTAL
        if source is None:
            self._description = None
        else:
            self._description = self._source.split('\n',1)[0].strip(' \t/*')
            
    
    
    def add_source(self, source):
        """ Templating, for later.
        """
        raise NotImplemented()
    
    
    def _enable(self):
        
        if self._handle <= 0:
            self._handle = gl.glCreateShader(self._type)
        
        # todo: what should happen if no source is given?
        if not self._source:
            self._compiled = 2
            return
        
        # If shader is compiled, we're done now
        if self._compiled:
            return 
        
        # Set compiled flag. It means that we tried to compile
        self._compiled = 1
        
        # Set source
        gl.glShaderSource(self._handle, self._source)
        
        # Compile the shader
        try:
            gl.glCompileShader(self._handle)
        except Exception as e:
            print( "Error compiling shader %r" % self )
            parse_shader_errors(e.description, self._source)
            raise

        # retrieve the compile status
        if not gl.glGetShaderiv(self._handle, gl.GL_COMPILE_STATUS):
            print( "Error compiling shader %r" % self )
            errors = gl.glGetShaderInfoLog(self._handle)
            parse_shader_errors(errors, self._source)
            raise RuntimeError(errors)
        
        # If we get here, compile is succesful
        self._compiled = 2
    
    
    def _disable(self):
        pass

    def __repr__(self):
        if self._description:
            return "<%s '%s'>" % (self.__class__.__name__, self._description)
        else:
            return "<%s at %s>" % (self.__class__.__name__, hex(id(self)))


class VertexShader(BaseShader):
    """ Representation of a vertex shader object. Inherits BaseShader.
    """
    def __init__(self, source=None):
        BaseShader.__init__(self, gl.GL_VERTEX_SHADER, source)



class FragmentShader(BaseShader):
    """ Representation of a fragment shader object. Inherits BaseShader.
    """
    def __init__(self, source=None):
        BaseShader.__init__(self, gl.GL_FRAGMENT_SHADER, source)



def parse_shader_error(error):
    """Parses a single GLSL error and extracts the line number
    and error description.

    Line number and description are returned as a tuple.

    GLSL errors are not defined by the standard, as such,
    each driver provider prints their own error format.

    Nvidia print using the following format::

        0(7): error C1008: undefined variable "MV"

    Nouveau Linux driver using the following format::

        0:28(16): error: syntax error, unexpected ')', expecting '('

    ATi and Intel print using the following format::

        ERROR: 0:131: '{' : syntax error parse error
    """
    import re

    # Nvidia
    # 0(7): error C1008: undefined variable "MV"
    match = re.match( r'(\d+)\((\d+)\)\s*:\s(.*)', error )
    if match:
        return (
            int(match.group( 2 )),   # line number
            match.group( 3 )    # description
            )

    # ATI
    # Intel
    # ERROR: 0:131: '{' : syntax error parse error
    match = re.match( r'ERROR:\s(\d+):(\d+):\s(.*)', error )
    if match:
        return (
            int(match.group( 2 )),   # line number
            match.group( 3 )    # description
            )

    # Nouveau
    # 0:28(16): error: syntax error, unexpected ')', expecting '('
    match = re.match( r'(\d+):(\d+)\((\d+)\):\s(.*)', error )
    if match:
        return (
            int(match.group( 2 )),   # line number
            match.group( 4 )    # description
            )
    
    return None, error


def parse_shader_errors(errors, source=None):
    """Parses a GLSL error buffer and prints a list of
    errors, trying to show the line of code where the error 
    ocrrured.
    """
    # Init
    if not isinstance(errors, basestring):
        errors = errors.decode('utf-8', 'replace')
    results = []
    lines = None
    if source is not None:
        lines = [line.strip() for line in source.split('\n')]
    
    for error in errors.split('\n'):
        # Strip; skip empy lines
        error = error.strip()
        if not error:
            continue
        # Separate line number from description (if we can)
        linenr, error = parse_shader_error(error)
        if None in (linenr, lines):
            print('    %s' % error)
        else:
            print('    on line %i: %s' % (linenr, error))
            if linenr>0 and linenr < len(lines):
                print('        %s' % lines[linenr-1])

