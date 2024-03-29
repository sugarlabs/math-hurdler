import math_hurdler
import sugargame.canvas
from sugar3.activity.widgets import StopButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics.toolbarbox import ToolbarBox
import sugar3.activity.activity
import pygame

from gettext import gettext as _

import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class MathHurdlerActivity(sugar3.activity.activity.Activity):
    def __init__(self, handle):
        super(MathHurdlerActivity, self).__init__(handle)

        self.paused = False
        self.muted = False
        # Create the game instance.
        self.game = math_hurdler.MathHurdler()

        # Build the activity toolbar.
        self.build_toolbar()

        # Build the Pygame canvas.
        self._pygamecanvas = sugargame.canvas.PygameCanvas(
            self, main=self.game.run)

        # Note that set_canvas implicitly calls read_file when
        # resuming from the Journal.
        self.set_canvas(self._pygamecanvas)

        # Start the game running (self.game.run is called when the
        # activity constructor returns).
        # Deprecated:Not required in sugargame v0.12
        # self._pygamecanvas.run_pygame(self.game.run)

    def build_toolbar(self):
        toolbar_box = ToolbarBox()
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, -1)
        activity_button.show()

        # Pause/Play button:

        stop_play = ToolButton('media-playback-stop')
        stop_play.set_tooltip(_("Stop"))
        stop_play.set_accelerator(_('<ctrl>space'))
        stop_play.connect('clicked', self._stop_play_cb)
        stop_play.show()

        toolbar_box.toolbar.insert(stop_play, -1)

        mute_button = ToolButton('speaker-muted-100')
        mute_button.set_tooltip(_('Sound'))
        mute_button.connect('clicked', self.sound_control)
        mute_button.show()

        toolbar_box.toolbar.insert(mute_button, -1)

        # Blank space (separator) and Stop button at the end:

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

    def _stop_play_cb(self, button):
        # Pause or unpause the game.
        self.paused = not self.paused
        self.game.set_paused(self.paused)

        # Update the button to show the next action.
        if self.paused:
            button.set_icon_name('media-playback-start')
            button.set_tooltip(_("Start"))
        else:
            button.set_icon_name('media-playback-stop')
            button.set_tooltip(_("Stop"))

    def sound_control(self, button):
        self.muted = not self.muted
        if self.muted:
            button.set_icon_name('speaker-muted-000')
            button.set_tooltip(_('Unmute'))
        else:
            button.set_icon_name('speaker-muted-100')
            button.set_tooltip(_('Mute'))
        self.game.toggle_mute()

    def read_file(self, file_path):
        with open(file_path, 'r') as f:
            restore_data = f.read()
            restore_data = str(restore_data).split()
            score, hscore, play_state, hurdle_number = [
                restore_data[i] for i in range(4)]
            self.game.restore_game(score, hscore, play_state, hurdle_number)

    def write_file(self, file_path):
        score, hscore, play_state, hurdle_number = self.game.write_file()
        with open(file_path, 'w') as f:
            f.write(f'{score}\n{hscore}\n{play_state}\n{hurdle_number}')
