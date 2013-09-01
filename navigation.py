# -*- coding: utf-8 -*-
# Copyright (C) 2006-2008 Osmo Salomaa
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

"""Additional methods of moving in the text."""

import gedit
import gtk
import os


class NavigationPlugin(gedit.Plugin):

    """Additional methods of moving in the text."""

    def activate(self, window):
        """Activate plugin."""
        action_group = gtk.ActionGroup(self.__class__.__name__)
        action_group.add_actions((
            ("BeginningOfLine", None, "_Beginning Of Line", None,
             "Go to the beginning of the current line",
             self.on_beginning_of_line_activate),
            ("EndOfLine", None, "_End Of Line", None,
             "Go to the end of the current line",
             self.on_end_of_line_activate),), window)
        uim = window.get_ui_manager()
        uim.insert_action_group(action_group, -1)
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, "navigation.xml")
        ui_id = uim.add_ui_from_file(path)
        data = {"action_group": action_group, "ui_id": ui_id}
        window.set_data(self.__class__.__name__, data)

    def deactivate(self, window):
        """Deactivate plugin."""
        uim = window.get_ui_manager()
        data = window.get_data(self.__class__.__name__)
        uim.remove_ui(data["ui_id"])
        uim.remove_action_group(data["action_group"])
        uim.ensure_update()
        window.set_data(self.__class__.__name__, None)

    def on_beginning_of_line_activate(self, action, window):
        """Go to the beginning of the current line."""
        doc = window.get_active_document()
        itr = doc.get_iter_at_mark(doc.get_insert())
        indent = itr.starts_line()
        itr.set_line_offset(0)
        while indent and (itr.get_char() in (" ", "\t")):
            itr.forward_char()
        doc.place_cursor(itr)

    def on_end_of_line_activate(self, action, window):
        """Go to the end of the current line."""
        doc = window.get_active_document()
        itr = doc.get_iter_at_mark(doc.get_insert())
        if not itr.ends_line():
            itr.forward_to_line_end()
        doc.place_cursor(itr)

    def update_ui(self, window):
        """Update the sensitivities of actions."""
        view = window.get_active_view()
        sensitive = bool(view and view.get_editable())
        data = window.get_data(self.__class__.__name__)
        data["action_group"].set_sensitive(sensitive)
