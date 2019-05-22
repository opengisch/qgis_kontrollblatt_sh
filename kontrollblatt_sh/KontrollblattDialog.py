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
    QgsDateTimeEdit,
    QgsMapCanvas
)

from qgis.core import (
    QgsMapLayer,
    QgsFeature,
    QgsMapLayerProxyModel,
    QgsProject,
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
    QVariant,
    QDateTime
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
        self.layer = QgsProject.instance().mapLayersByName('stammdaten')[0]
        self.iface.setActiveLayer(self.layer)
        self.layer.removeSelection()

        # gui stuff:
        self.setWindowTitle("Bauminventar Kontrollblatt")
        self.layout = QVBoxLayout()
        self.title = QLabel("Bauminventar Kontrollblatt")
        font = self.title.font()
        font.setPointSize(24);
        font.setBold(True);
        self.title.setFont(font);
        self.layout.addWidget(self.title)

        self.selectButton = QPushButton("Baumobjekte selektieren")
        self.selectButton.clicked.connect(self.select)
        self.selectedFeatureIdsLabel = QLabel()
        self.layout.addWidget(self.selectButton)
        self.layout.addWidget(self.selectedFeatureIdsLabel)
        #todo make signal or remove this selected feature list

        self.frame = QFrame()
        self.frame.setLayout( QGridLayout() )
        self.datumLabel = QLabel("Erledigt_Datum") 
        self.datumEdit = QgsDateTimeEdit()
        self.datumEdit.setDisplayFormat('dd.MM.yyyy')
        self.datumEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.datumEdit.valueChanged.connect(self.setStateOfSaveButton)
        self.kontrolleurLabel = QLabel("Kontrolleur") 
        self.kontrolleurEdit = QLineEdit()
        self.kontrolleurEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.kontrolleurEdit.textChanged.connect(self.setStateOfSaveButton)
        self.frame.layout().addWidget(self.datumLabel, 0, 0 )
        self.frame.layout().addWidget(self.datumEdit, 0, 1 )
        self.frame.layout().addWidget(self.kontrolleurLabel, 1, 0 )
        self.frame.layout().addWidget(self.kontrolleurEdit, 1, 1 )
        self.layout.addWidget(self.frame)
         
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close|QDialogButtonBox.Save)
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)
        self.buttonBox.accepted.connect(self.save)
        self.buttonBox.rejected.connect(self.close)
          
        # todo: deactivate save
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
    
    def select(self):
        self.iface.actionSelectPolygon().trigger()
        self.layer.selectionChanged.connect(self.selectionMade)
        self.setVisible(False)

    def selectionMade(self):
        self.layer.selectionChanged.disconnect(self.selectionMade)
        self.setVisible(True)
        if len(self.layer.selectedFeatureIds()):
            self.selectedFeatureIdsLabel.setText( str(self.layer.selectedFeatureIds()) )
        else: 
            self.selectedFeatureIdsLabel.setText('')
        self.setStateOfSaveButton()

    def setStateOfSaveButton(self):
        print("papapapap"+str(self.datumEdit.dateTime())+"   "+self.datumEdit.text()+" "+str(QDateTime()))
        if len(self.layer.selectedFeatureIds()) and len(self.kontrolleurEdit.text()) and self.datumEdit.dateTime()!=QDateTime():
          self.buttonBox.button(QDialogButtonBox.Save).setEnabled(True)
        else:
          self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)  

    def close(self):
        self.layer.removeSelection()
        self.done(0)

    def save(self):
        selectedFeatureIds = self.layer.selectedFeatureIds()
        kontrollblattLayer = QgsProject.instance().mapLayersByName('kontrollblatt')[0]
        kontrollblattLayer.startEditing()
        for stammdatenId in selectedFeatureIds:
            feature = QgsFeature( kontrollblattLayer.fields() )
            feature.setAttribute('erledigt_datum', self.datumEdit.date())
            feature.setAttribute('kontrolleur', self.kontrolleurEdit.text())
            feature.setAttribute('stammdaten', stammdatenId)
            kontrollblattLayer.addFeature(feature)
        if kontrollblattLayer.commitChanges():
            self.iface.messageBar().pushMessage( '{number_of_features} Features hinzugefügt (Erledigt_Datum: {date} und Kontrolleur: {kontrolleur}) mit den stammdaten ids {ids}.'
                .format( number_of_features=len(selectedFeatureIds), ids=str(selectedFeatureIds), date=self.datumEdit.date().toString('dd.MM.yyyy'), kontrolleur=self.kontrolleurEdit.text() ) )
        
        self.layer.removeSelection()
        self.done(0)
