# -*- coding: utf-8 -*-
# -----------------------------------------------------------
# Copyright (C) 2017 OPENGIS.ch
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------

from qgis.gui import (
    QgsDockWidget,
    QgsAttributeForm,
    QgsMapLayerComboBox,
    QgsAttributeEditorContext,
    QgsDateTimeEdit
)
from qgis.core import (
    QgsExpression,
    QgsMapLayer,
    QgsFeature,
    QgsMapLayerProxyModel,
    QgsProject,
    QgsDefaultValue,
    NULL
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QGridLayout,
    QFrame,
    QDialogButtonBox,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QDateEdit,
    QSizePolicy
)
from qgis.PyQt.QtCore import(
    pyqtSignal,
    QCoreApplication,
    QVariant
)
from qgis.PyQt.QtGui import (
    QFont,
    QColor
)


class KontrollblattDialog(QDialog):

    def __init__(self, iface):
        QDialog.__init__(self)

        # layer stuff
        self.iface = iface
        self.layer = self.iface.activeLayer()

        # gui stuff:
        self.layout = QVBoxLayout()
        self.title = QLabel("Bauminventar Kontrollblatt")
        self.layout.addWidget(self.title)

        self.selectButton = QPushButton("Baumobjekte selektieren")
        self.selectButton.clicked.connect(self.select)
        self.layout.addWidget(self.selectButton)

        self.frame = QFrame()
        self.frame.setLayout( QGridLayout() )
        self.datumLabel = QLabel("Erledigt_Datum") 
        self.datumEdit = QgsDateTimeEdit()
        self.datumEdit.setDisplayFormat('dd.MM.yyyy')
        self.datumEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.kontrolleurLabel = QLabel("Kontrolleur") 
        self.kontrolleurEdit = QLineEdit()
        self.kontrolleurEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.frame.layout().addWidget(self.datumLabel, 0, 0 )
        self.frame.layout().addWidget(self.datumEdit, 0, 1 )
        self.frame.layout().addWidget(self.kontrolleurLabel, 1, 0 )
        self.frame.layout().addWidget(self.kontrolleurEdit, 1, 1 )
        self.layout.addWidget(self.frame)
         
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
        self.buttonBox.accepted.connect(self.save)
        self.buttonBox.rejected.connect(self.close)
        # todo: deactivate save

        self.layout.addWidget(self.buttonBox)
        
        self.setLayout(self.layout)
    
    def select(self):
        # self.layer = self.iface.activeLayer()
        self.iface.mapCanvas().setSelectionColor( QColor("blue") )
        self.iface.mapCanvas().setMapTool( QgsMapToolSelect(self.iface.mapCanvas()) )
        # mMapTools.mSelectPolygon = new QgsMapToolSelect( mMapCanvas );
        # mMapTools.mSelectPolygon->setAction( mActionSelectPolygon );
        # mMapTools.mSelectPolygon->setSelectionMode( QgsMapToolSelectionHandler::SelectPolygon );

        pass

    def close(self):
        self.done(0)

    def save(self):
        self.layer.startEditing()
        selectedFeatures = self.layer.selectedFeatures()
        for feature in selectedFeatures:
            feature.setAttribute('erledigt_datum', self.datumEdit.date())
            feature.setAttribute('kontrolleur', self.kontrolleurEdit.text())
            self.layer.updateFeature(feature)
        self.layer.removeSelection()
        self.layer.commitChanges()
        # todo: successmessage
