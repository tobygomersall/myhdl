#  This file is part of the myhdl library, a Python package for using
#  Python as a Hardware Description Language.
#
#  Copyright (C) 2003-2008 Jan Decaluwe
#
#  The myhdl library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public License as
#  published by the Free Software Foundation; either version 2.1 of the
#  License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.

#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

""" Simulator internals and the now function

This module provides the following objects:
now -- function that returns the current simulation time

"""

from contextlib import contextmanager
import weakref
import sys
import types

try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading

class _SimContextManager(types.ModuleType):

    def __init__(self):

        import copy
        self.copy = copy.copy

        self._data = _threading.local()
        self._data._default_context = {'signals': [],
                                       'siglist': [],
                                       'futureEvents': [],
                                       'time': 0,
                                       'cosim': 0,
                                       'tracing': 0,
                                       'tf': None,
                                       'signal_state': {}}

        self._data.context_dict = weakref.WeakKeyDictionary()

        self._data.current_context = None

    def _set_context_id(self, context_id=None):
        
        self._data.current_context = context_id

        if (self._data.current_context not in self._data.context_dict and
            self._data.current_context is not None):

            new_context = {}

            # Copy the default context
            for each in self._data._default_context:
                new_context[each] = self.copy(
                    self._data._default_context[each])

            self._data.context_dict[self._data.current_context] = new_context

    def _get_context(self):
        
        if self._data.current_context is None:
            context = self._data._default_context

        else:
            context = self._data.context_dict[self._data.current_context]

        return context

    @property
    def _signals(self):
        return self._get_context()['signals']

    @_signals.setter
    def _signals(self, val):
        self._get_context()['signals'] = val

    @property
    def _signal_state(self):
        return self._get_context()['signal_state']

    @_signal_state.setter
    def _signal_state(self, val):
        self._get_context()['signal_state'] = val

    @property
    def _siglist(self):
        return self._get_context()['siglist']

    @_siglist.setter
    def _siglist(self, val):
        self._get_context()['siglist'] = val
    
    @property
    def _futureEvents(self):
        return self._get_context()['futureEvents']

    @_futureEvents.setter
    def _futureEvents(self, val):
        self._get_context()['futureEvents'] = val

    @property
    def _time(self):
        return self._get_context()['time']

    @_time.setter
    def _time(self, val):
        self._get_context()['time'] = val

    @property
    def _cosim(self):
        return self._get_context()['cosim']

    @_cosim.setter
    def _cosim(self, val):
        self._get_context()['cosim'] = val

    @property
    def _tracing(self):
        return self._get_context()['tracing']

    @_tracing.setter
    def _tracing(self, val):
        self._get_context()['tracing'] = val

    @property
    def _tf(self):
        return self._get_context()['tf']

    @_tf.setter
    def _tf(self, val):
        self._get_context()['tf'] = val

    def now(self):
        """ Return the current simulation time """
        return self._time

    @contextmanager
    def simulation_context(self, context_id=None):

        if context_id is not None and self._data.current_context is not None:
            raise ValueError(
                'A new context can currently only be entered from the '
                'default context.')

        try:
            for signal in self._signals:
                signal._stash_state()
            
            self._set_context_id(context_id)

            for signal in self._signals:
                signal._recall_state()

            yield
        finally:
            for signal in self._signals:
                signal._stash_state()
            
            self._set_context_id(None)

            for signal in self._signals:
                signal._recall_state()

sys.modules[__name__] = _SimContextManager()

