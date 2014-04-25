# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import numpy as np


###############################################################################
# Adapted from Python's unittest2 (which is wrapped by nose)
# http://docs.python.org/2/license.html

def _safe_rep(obj, short=False):
    """Helper for assert_* ports"""
    try:
        result = repr(obj)
    except Exception:
        result = object.__repr__(obj)
    if not short or len(result) < 80:
        return result
    return result[:80] + ' [truncated]...'


def _safe_str(obj):
    """Helper for assert_* ports"""
    try:
        return str(obj)
    except Exception:
        return object.__str__(obj)


def _format_msg(msg, std_msg):
    """Helper for assert_* ports"""
    if msg is None:
        msg = std_msg
    else:
        try:
            msg = '%s : %s' % (std_msg, msg)
        except UnicodeDecodeError:
            msg = '%s : %s' % (_safe_str(std_msg), _safe_str(msg))
    return msg


def assert_in(member, container, msg=None):
    """Backport for old nose.tools"""
    if member in container:
        return
    std_msg = '%s not found in %s' % (_safe_rep(member), _safe_rep(container))
    msg = _format_msg(msg, std_msg)
    raise AssertionError(msg)


def assert_not_in(member, container, msg=None):
    """Backport for old nose.tools"""
    if member not in container:
        return
    std_msg = '%s found in %s' % (_safe_rep(member), _safe_rep(container))
    msg = _format_msg(msg, std_msg)
    raise AssertionError(msg)


def assert_is(expr1, expr2, msg=None):
    """Backport for old nose.tools"""
    if expr1 is not expr2:
        std_msg = '%s is not %s' % (_safe_rep(expr1), _safe_rep(expr2))
        raise AssertionError(_format_msg(msg, std_msg))


###############################################################################
# GL stuff

def _has_pyopengl():
    try:
        from OpenGL import GL  # noqa, analysis:ignore
    except Exception:
        return False
    else:
        return True


def requires_pyopengl():
    return np.testing.dec.skipif(not _has_pyopengl(), 'Requires PyOpenGL')


###############################################################################
# App stuff

def has_backend(backend, require=(), out=()):
    mod = __import__('app.backends._%s' % backend, globals(), level=2)
    mod = getattr(mod.backends, '_%s' % backend)
    has = mod.available
    for req in require:
        has = (has and getattr(mod, 'has_%s' % req))
    ret = (has,) if len(out) > 0 else has
    for o in out:
        ret += (getattr(mod, o),)
    return ret


def requires_application(backend=None, require=()):
    if backend is None:
        has = False
        backends = ['qt', 'pyglet', 'glfw', 'glut']  # should pull from app!
        for backend in backends:
            if has_backend(backend, require=require):
                has = True
                break
        return np.testing.dec.skipif(not has, 'Requires application backend')
    else:
        has, why = has_backend(backend, require=require, out=['why_not'])
        return np.testing.dec.skipif(not has, 'Requires %s: %s'
                                     % (backend, why))
