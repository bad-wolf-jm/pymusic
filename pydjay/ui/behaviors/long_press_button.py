import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.clock import Clock

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.button import ButtonBehavior

from functools import partial

from time import time


class LongPressButtonBehaviour(object):
    def __init__(self, **args):
        super(LongPressButtonBehaviour, self).__init__(**args)
        self._click = False
        self._long_press_threshold = .75
        self._long_press_trigger = None
        self._last_press_event = None
        self._last_release_event = None
        self.register_event_type('on_long_press')
        self.register_event_type('on_click')

        self.bind(on_touch_down=self._do_press,
                  on_touch_up=self._do_release)

    def _long_press(self, x, y, *args):
        self.dispatch('on_long_press', x, y)
        self._click = False

    def _do_press(self, window, event):
        self._click = True
        if not self.collide_point(*event.pos):
            return False
        if event != self._last_press_event:
            self._long_press_trigger = partial(self._long_press, event.pos[0], event.pos[1])
            Clock.schedule_once(self._long_press_trigger, self._long_press_threshold)
            self._last_press_event = event

    def _do_release(self, window, event):
        if not self.collide_point(*event.pos):
            return False

        if event != self._last_release_event:
            if self._long_press_trigger is not None:
                Clock.unschedule(self._long_press_trigger)
                self._long_press_trigger = None
            self._last_release_event = event
            if self._click:
                self.dispatch('on_click')
                self._click = False

    def on_long_press(self, *a):
        pass

    def on_click(self, *a):
        pass
