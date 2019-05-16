# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# Copyright (C) 2017 OPENGIS.ch
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from qgis.PyQt.QtCore import Qt
from .KontrollblattDialog import KontrollblattDialog
from PyQt5.QtWidgets import QAction, QMessageBox

def classFactory(iface):
    return Kontrollblatt(iface)


class Kontrollblatt(object):

    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction(u'Kontrollblatt SH', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        layer = self.iface.activeLayer()

        if( layer.name() == 'kontrollblatt'):
            self.dlg = KontrollblattDialog( self.iface)
            self.dlg.exec()
        else:
            QMessageBox.information(None, u'Kontrollblatt SH', u'Plugin only available layer "kontrollblatt" with the following fields:\n  - erledigt_datum (date)\n  - kontrolleur (string)')

