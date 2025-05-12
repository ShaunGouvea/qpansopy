# -*- coding: utf-8 -*-
"""
QPANSOPY Plugin for QGIS
"""
import os
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolBar, QMessageBox
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform

# Import the dock widgets
from .qpansopy_vss_dockwidget import QPANSOPYVSSDockWidget
from .qpansopy_ils_dockwidget import QPANSOPYILSDockWidget
from .qpansopy_non_precision_final_app_dockwidget import QPANSOPYNpFinAppDockWidget

class Qpansopy:
    """QPANSOPY Plugin Implementation"""

    def __init__(self, iface):
        """Constructor.
        
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        
        # Create actions
        self.actions = []
        self.menu = "QPANSOPY"


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        
        # Crear el menú QPANSOPY antes del menú de Ayuda
        menuBar = self.iface.mainWindow().menuBar()
        helpMenu = None
        
        # Buscar el menú de Ayuda
        for action in menuBar.actions():
            if action.text() == "Help" or action.text() == "Ayuda":
                helpMenu = action
                break
        
        # Crear nuestro menú
        self.menu = QMenu("QPANSOPY", self.iface.mainWindow())
        
        # Insertar antes del menú de Ayuda si se encuentra, de lo contrario añadir al final
        if helpMenu:
            menuBar.insertMenu(helpMenu, self.menu)
        else:
            menuBar.addMenu(self.menu)

        #Configure Modules NAME:PROPERTIES (STR:DICT)
        self.modules:dict = {"VSS": {"TITLE":"QPANSOPY VSS Tool","ICON":"vss_icon.png","DOCK_WIDGET": QPANSOPYVSSDockWidget,"GUI_INSTANCE":None},
                             "ILS": {"TITLE":"QPANSOPY ILS Tool","ICON":"ils_icon.png","DOCK_WIDGET": QPANSOPYILSDockWidget,"GUI_INSTANCE":None},
                             "NPFA": {"TITLE":"QPANSOPY Non-precision Final App Tool","ICON":"NP_FinalApp_icon.png","DOCK_WIDGET": QPANSOPYNpFinAppDockWidget,"GUI_INSTANCE":None}}

        #Create Actions
        for name,properties in self.modules.items():
            new_action = QAction(
            QIcon(os.path.join(self.plugin_dir, 'icons', properties["ICON"])),
            properties["TITLE"], 
            self.iface.mainWindow())
            ##Use lambda so the toggle_dock function is not called oin init and _,n=name prevents late binding bug
            new_action.triggered.connect(lambda _,n=name: self.toggle_dock(n))
            self.menu.addAction(new_action)
            self.iface.addToolBarIcon(new_action)
            self.actions.append(new_action)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Eliminar el menú
        if self.menu:
            menuBar = self.iface.mainWindow().menuBar()
            menuBar.removeAction(self.menu.menuAction())
        
        # Eliminar iconos de la barra de herramientas
        for action in self.actions:
            self.iface.removeToolBarIcon(action)
        
        for name,properties in self.modules.items():
            if properties["GUI_INSTANCE"] is not None:
                self.iface.removeDockWidget(properties["GUI_INSTANCE"])
                self.modules[name]["GUI_INSTANCE"] = None

    def toggle_dock(self,name:str):
        """Toggle the requested dock widget
        :param str name: key name from self.module for the module to toggle 
        """
        if self.modules[name]["GUI_INSTANCE"] is None:
            dock_widget = self.modules[name]["DOCK_WIDGET"]
             # Create the dock widget
            module_dock = self.modules[name]["GUI_INSTANCE"] = dock_widget(self.iface)
            # Connect the closing signal
            module_dock.closingPlugin.connect(lambda _,n=name: self.on_dock_closed(n))
            # Add the dock widget to the interface
            self.iface.addDockWidget(Qt.RightDockWidgetArea, module_dock)

            #Close all other module dock if open
            for other_name,other_properties in self.modules.items():
                if other_properties["GUI_INSTANCE"] and other_name != name:
                    self.iface.removeDockWidget(other_properties["GUI_INSTANCE"])
                    self.modules[other_name]["GUI_INSTANCE"] = None
        else:
            module_dock = self.modules[name]["GUI_INSTANCE"]
            self.iface.removeDockWidget(module_dock)
            self.modules[name]["GUI_INSTANCE"] = None


    def on_dock_closed(self,name):
        """Handle module dock widget closing
        :param str name: key name from self.module for the module to close 
        """
        self.modules[name]["GUI_INSTANCE"] = None