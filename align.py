# -*- coding: utf-8 -*-
# Copyright (C) 2006 Osmo Salomaa
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

"""Align blocks of text into columns."""

import gedit
import gtk
import gtk.glade
import os


class AlignDialog(object):

    """Dialog for specifying an alignment separator."""

    def __init__(self, parent):
        path = os.path.join(os.path.dirname(__file__), "align.glade")
        glade_xml = gtk.glade.XML(path)
        self.dialog = glade_xml.get_widget("dialog")
        self.entry = glade_xml.get_widget("entry")
        self.dialog.set_transient_for(parent)
        self.dialog.set_default_response(gtk.RESPONSE_OK)

    def destroy(self):
        """Destroy the dialog."""
        return self.dialog.destroy()

    def get_separator(self):
        """Get separator."""
        return self.entry.get_text()

    def run(self):
        """Show and run the dialog."""
        self.dialog.show()
        return self.dialog.run()


class AlignPlugin(gedit.Plugin):

    """Align blocks of text into columns."""

    def __init__(self):
        gedit.Plugin.__init__(self)
        self.window = None

    def activate(self, window):
        """Activate plugin."""
        self.window = window
        action_group = gtk.ActionGroup(self.__class__.__name__)
        action_group.add_actions((
            ("Align", None, "Ali_gn...", None,
             "Align the selected text to columns",
             self.on_align_activate),), window)
        uim = window.get_ui_manager()
        uim.insert_action_group(action_group, -1)
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, "align.xml")
        ui_id = uim.add_ui_from_file(path)
        data = {"action_group": action_group, "ui_id": ui_id}
        window.set_data(self.__class__.__name__, data)

    def align(self, doc, bounds, separator):
        """Align the selected text into columns."""
        splitter = separator.strip() or " "
        lines = range(bounds[0].get_line(), bounds[1].get_line() + 1)
        # Split text to rows and columns.
        # Ignore lines that don't match splitter.
        matrix = []
        for i in reversed(range(len(lines))):
            line_start = doc.get_iter_at_line(lines[i])
            line_end = line_start.copy()
            line_end.forward_to_line_end()
            text = doc.get_text(line_start, line_end)
            if text.find(splitter) == -1:
                lines.pop(i)
                continue
            matrix.insert(0, text.split(splitter))
        for i in range(len(matrix)):
            matrix[i][0] = matrix[i][0].rstrip()
            for j in range(1, len(matrix[i])):
                matrix[i][j] = matrix[i][j].strip()
        # Find out column count and widths.
        col_count = max(list(len(x) for x in matrix))
        widths = [0] * col_count
        for row in matrix:
            for i, element in enumerate(row):
                widths[i] = max(widths[i], len(element))
        doc.begin_user_action()
        # Remove text and insert column elements.
        for i, line in enumerate(lines):
            line_start = doc.get_iter_at_line(line)
            line_end = line_start.copy()
            line_end.forward_to_line_end()
            doc.delete(line_start, line_end)
            for j, element in enumerate(matrix[i]):
                offset = sum(widths[:j])
                itr = doc.get_iter_at_line(line)
                itr.set_line_offset(offset)
                doc.insert(itr, element)
                if j < col_count - 1:
                    itr.set_line_offset(offset + len(element))
                    space = " " * (widths[j] - len(element))
                    doc.insert(itr, space)
        # Insert separators.
        for i, line in enumerate(lines):
            for j in reversed(range(len(matrix[i]) - 1)):
                offset = sum(widths[:j + 1])
                itr = doc.get_iter_at_line(line)
                itr.set_line_offset(offset)
                doc.insert(itr, separator)
        doc.end_user_action()

    def deactivate(self, window):
        """Deactivate plugin."""
        uim = window.get_ui_manager()
        data = window.get_data(self.__class__.__name__)
        uim.remove_ui(data["ui_id"])
        uim.remove_action_group(data["action_group"])
        uim.ensure_update()
        window.set_data(self.__class__.__name__, None)
        self.window = None

    def on_align_activate(self, *args):
        """Align the selected text into columns."""
        doc = self.window.get_active_document()
        bounds = doc.get_selection_bounds()
        if not bounds: return
        dialog = AlignDialog(self.window)
        response = dialog.run()
        separator = dialog.get_separator()
        dialog.destroy()
        if response == gtk.RESPONSE_OK and separator:
            self.align(doc, bounds, separator)

    def update_ui(self, window):
        """Update sensitivity of plugin's actions."""
        doc = self.window.get_active_document()
        self.action_group.set_sensitive(doc is not None)
