# -*- coding: utf-8 -*-
# Copyright (C) 2008 Osmo Salomaa
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

"""Increase or decrease space between lines."""

import gconf
import gedit
import gtk

GCONF_KEY = "/apps/gedit-2/plugins/line-spacing/line-spacing"


class PreferencesDialog(gtk.Dialog):

    """Dialog for setting the value of the line-spacing."""

    def __init__(self, window):
        gtk.Dialog.__init__(self, parent=window)
        self.view = window.get_active_view()
        self.init_dialog(window)
        self.init_widgets()

    def init_dialog(self, window):
        """Initialize the dialog properties."""
        self.set_title("Line-Spacing Preferences")
        self.add_button(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE)
        self.set_default_response(gtk.RESPONSE_CLOSE)
        self.set_has_separator(False)
        self.set_transient_for(window)
        self.set_resizable(False)
        self.set_border_width(6)
        self.set_modal(True)
        on_response = lambda self, response: self.destroy()
        self.connect("response", on_response)

    def init_widgets(self):
        """Initialize the widgets in the dialog."""
        spin_button = gtk.SpinButton()
        spin_button.set_increments(1, 2)
        spin_button.set_range(-99, 99)
        spin_button.set_value(self.view.get_pixels_above_lines())
        spin_button.set_activates_default(True)
        callback = self.on_spin_button_value_changed
        spin_button.connect("value-changed", callback)
        label = gtk.Label("_Additional space between lines:")
        label.set_use_underline(True)
        label.set_mnemonic_widget(spin_button)
        main_hbox = gtk.HBox(False, 12)
        main_hbox.set_border_width(6)
        main_hbox.pack_start(label)
        value_hbox = gtk.HBox(False, 6)
        value_hbox.pack_start(spin_button)
        value_hbox.pack_start(gtk.Label("pixels"))
        main_hbox.pack_start(value_hbox)
        vbox = self.get_child()
        vbox.add(main_hbox)
        vbox.show_all()

    def on_spin_button_value_changed(self, spin_button):
        """Save and apply the new line-spacing."""
        value = spin_button.get_value_as_int()
        self.view.set_pixels_above_lines(value)
        client = gconf.client_get_default()
        client.set_int(GCONF_KEY, value)


class LineSpacingPlugin(gedit.Plugin):

    """Increase or decrease space between lines."""

    def __init__(self):
        gedit.Plugin.__init__(self)
        self.gconf_id = None
        client = gconf.client_get_default()
        self.pixels_above = client.get_int(GCONF_KEY)

    def activate(self, window):
        """Activate plugin."""
        for view in window.get_views():
            view.set_pixels_above_lines(self.pixels_above)
        callback = self.on_window_tab_added
        handler_id = window.connect("tab-added", callback)
        window.set_data(self.__class__.__name__, handler_id)
        client = gconf.client_get_default()
        callback = self.on_gconf_client_notify
        self.gconf_id = client.notify_add(GCONF_KEY, callback)

    def create_configure_dialog(self):
        """Return the preferences dialog."""
        window = gedit.app_get_default().get_active_window()
        return PreferencesDialog(window)

    def deactivate(self, window):
        """Deactivate plugin."""
        for view in window.get_views():
            view.set_pixels_above_lines(0)
        handler_id = window.get_data(self.__class__.__name__)
        window.disconnect(handler_id)
        window.set_data(self.__class__.__name__, None)
        client = gconf.client_get_default()
        client.notify_remove(self.gconf_id)

    def on_gconf_client_notify(self, client, gconf_id, entry, data):
        """Update line-spacing for all views."""
        self.pixels_above = client.get_int(GCONF_KEY)
        window = gedit.app_get_default().get_active_window()
        for view in window.get_views():
            view.set_pixels_above_lines(self.pixels_above)

    def on_window_tab_added(self, window, tab):
        """Set line-spacing for the view in tab."""
        view = tab.get_view()
        view.set_pixels_above_lines(self.pixels_above)
