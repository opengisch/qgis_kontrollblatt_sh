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
    QgsVectorLayerUtils,
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
        self.stammdatenLayer = QgsProject.instance().mapLayersByName('baumstammdaten')[0]

        # gui stuff:
        self.setWindowTitle("Bauminventar Kontrollblatt")
        layout = QVBoxLayout()
        title = QLabel("Bauminventar Kontrollblatt")
        font = title.font()
        font.setPointSize(24)
        font.setBold(True);
        title.setFont(font);
        layout.addWidget(title)

        selectButton = QPushButton("Baumobjekte selektieren")
        selectButton.clicked.connect(self.select)
        self.selectedStammdatenTidsLabel = QLabel()
        self.selectedStammdatenTidsLabel.setText('Es wurden noch keine Objekte selektiert.')
        font = self.selectedStammdatenTidsLabel.font()
        font.setBold(True)
        self.selectedStammdatenTidsLabel.setFont(font)
        self.selectedFelledTidsLabel = QLabel()
        self.selectedFelledTidsLabel.setVisible(False)
        font = self.selectedFelledTidsLabel.font()
        font.setItalic(True)
        self.selectedFelledTidsLabel.setFont(font)

        layout.addWidget(selectButton)
        layout.addWidget(self.selectedStammdatenTidsLabel)
        layout.addWidget(self.selectedFelledTidsLabel)

        self.datumLabel = QLabel("Erledigt_Datum") 
        self.datumEdit = QgsDateTimeEdit()
        self.datumEdit.setDisplayFormat('dd.MM.yyyy')
        self.datumEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.datumEdit.clear()
        self.datumEdit.valueChanged.connect(self.setStateOfSaveButton)
        self.kontrolleurLabel = QLabel("Kontrolleur") 
        self.kontrolleurEdit = QLineEdit()
        self.kontrolleurEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.kontrolleurEdit.textChanged.connect(self.setStateOfSaveButton)

        frame = QFrame()
        frame.setLayout( QGridLayout() )
        frame.layout().addWidget(self.datumLabel, 0, 0 )
        frame.layout().addWidget(self.datumEdit, 0, 1 )
        frame.layout().addWidget(self.kontrolleurLabel, 1, 0 )
        frame.layout().addWidget(self.kontrolleurEdit, 1, 1 )
         
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close|QDialogButtonBox.Save)
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)
        self.buttonBox.accepted.connect(self.save)
        self.buttonBox.rejected.connect(self.close)

        layout.addWidget(frame)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        self.stammdatenTids=[]
        self.felledTids=[]
    
    def select(self):
        self.iface.setActiveLayer(self.stammdatenLayer)
        self.stammdatenLayer.removeSelection()
        self.iface.actionSelectPolygon().trigger()
        self.stammdatenLayer.selectionChanged.connect(self.selectionMade)
        self.iface.mapCanvas().mapToolSet.connect(self.noSelectionMade)
        self.setVisible(False)
        self.iface.messageBar().pushMessage( 'Selektieren Sie jetzt die Baumobjekte.')

    def selectionMade(self):
        self.stammdatenLayer.selectionChanged.disconnect(self.selectionMade)
        self.iface.mapCanvas().mapToolSet.disconnect(self.noSelectionMade)
        self.setVisible(True)

        self.stammdatenTids.clear()
        self.felledTids.clear()
        selectedFeatures = self.stammdatenLayer.selectedFeatures()
        for selectedFeature in selectedFeatures:
            if selectedFeature["faelljahr"] == NULL:
                self.stammdatenTids.append(selectedFeature["T_id"])
            else:
                self.felledTids.append(selectedFeature["T_id"])

        self.setSelectionInfo()
        self.setStateOfSaveButton()

    def noSelectionMade(self):
        self.stammdatenLayer.selectionChanged.disconnect(self.selectionMade)
        self.iface.mapCanvas().mapToolSet.disconnect(self.noSelectionMade)
        self.setVisible(True)
        self.setSelectionInfo()
        self.setStateOfSaveButton()

    def setStateOfSaveButton(self):
        if len(self.stammdatenTids) and len(self.kontrolleurEdit.text()) and self.datumEdit.dateTime()!=QDateTime():
          self.buttonBox.button(QDialogButtonBox.Save).setEnabled(True)
        else:
          self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)  

    def setSelectionInfo(self):
        if len(self.stammdatenTids):
            if len(self.stammdatenTids)>1:
                self.selectedStammdatenTidsLabel.setText('{} Objekte sind selektiert.'.format(len(self.stammdatenTids)))
            else:
                self.selectedStammdatenTidsLabel.setText('Ein Objekt ist selektiert.')
            self.selectedStammdatenTidsLabel.setToolTip(str(self.stammdatenTids))
        else:
            self.selectedStammdatenTidsLabel.setText('Es wurden noch keine Objekte selektiert.')
        if len(self.felledTids):
            if len(self.felledTids)>1:
                self.selectedFelledTidsLabel.setText('{} gefällte Objekte sind selektiert (und werden ignoriert).'.format(len(self.felledTids)))
            else:
                self.selectedFelledTidsLabel.setText('Ein gefälltes Objekt ist selektiert (und wird ignoriert).')
            self.selectedFelledTidsLabel.setToolTip(str(self.felledTids))
            self.selectedFelledTidsLabel.setVisible(True)
        else:
            self.selectedFelledTidsLabel.setVisible(False)

    def close(self):
        self.done(0)

    def save(self):
        kontrollblattLayer = QgsProject.instance().mapLayersByName('kontrollblatt')[0]
        kontrollblattLayer.startEditing()

        features = []
        for stammdatenId in self.stammdatenTids:
            feature = QgsVectorLayerUtils.createFeature( kontrollblattLayer )
            feature.setAttribute('erledigt_datum', self.datumEdit.date())
            feature.setAttribute('kontrolleur', self.kontrolleurEdit.text())
            feature.setAttribute('baumstammdaten', stammdatenId)
            features.append(feature)

        kontrollblattLayer.addFeatures(features)

        if kontrollblattLayer.commitChanges():
            self.iface.messageBar().pushMessage( '{number_of_features} Features hinzugefügt (Erledigt_Datum: {date} und Kontrolleur: {kontrolleur}) mit den stammdaten ids {ids}.'
                .format( number_of_features=len(self.stammdatenTids), ids=str(self.stammdatenTids), date=self.datumEdit.date().toString('dd.MM.yyyy'), kontrolleur=self.kontrolleurEdit.text() ) )
        
        self.stammdatenLayer.removeSelection()
        self.done(0)
