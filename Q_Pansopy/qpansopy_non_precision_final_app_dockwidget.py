import os
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QFileInfo, Qt
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes, QgsMapLayerProxyModel
from qgis.utils import iface
from qgis.core import Qgis
from .utilities.units import QPANSOPYUnit, QPANSOPYUnitType


# Use __file__ to get the current script path
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'Non-precision_Final_Appraoch.ui'))



class QPANSOPYNpFinAppDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self,iface):

        """Constructor."""
        super(QPANSOPYNpFinAppDockWidget, self).__init__(iface.mainWindow())
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.iface = iface
        
        # Configure the dock widget to be resizable
        self.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable |
                         QtWidgets.QDockWidget.DockWidgetFloatable |
                         QtWidgets.QDockWidget.DockWidgetClosable)

        # Set minimum and maximum sizes
        self.setMinimumHeight(300)
        self.setMaximumHeight(800)

        # Connect signals
        self.calculateInterceptpushButton.clicked.connect(self.populate_track_offset)
        self.calculateButton.clicked.connect(self.calculate)
        self.browseButton.clicked.connect(self.browse_output_folder)
        
        # Set default output folder
        self.outputFolderLineEdit.setText(self.get_desktop_path())
        
        # Filter layers in comboboxes
        self.navaidLayerComboBox.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.thresholdLayerComboBox.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.runwayLayerComboBox.setFilters(QgsMapLayerProxyModel.LineLayer)
        
        #Add units to comboBoxes

        self.thresholdElevationUnitsComboBox.addItems([QPANSOPYUnit._abbreviation[QPANSOPYUnitType.METRE],QPANSOPYUnit._abbreviation[QPANSOPYUnitType.FEET]])
        self.trackOffsetUnitsComboBox.addItems([QPANSOPYUnit._abbreviation[QPANSOPYUnitType.DEGREES],QPANSOPYUnit._abbreviation[QPANSOPYUnitType.RADIANS],QPANSOPYUnit._abbreviation[QPANSOPYUnitType.PERCENT]])
        self.distanceUnitsComboBox.addItems([QPANSOPYUnit._abbreviation[QPANSOPYUnitType.NAUTICAL_MILE],QPANSOPYUnit._abbreviation[QPANSOPYUnitType.METRE]])

        self.segmentLengthSpinBox.setValue(5.0)

        # Log message
        self.log("QPANSOPY Non-precision Final Approach plugin loaded. Select layers and parameters, then click Calculate.")

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
    
    def get_desktop_path(self):
        """Get the path to the desktop"""
        if os.name == 'nt':  # Windows
            return os.path.join(os.environ['USERPROFILE'], 'Desktop')
        elif os.name == 'posix':  # macOS or Linux
            return os.path.join(os.path.expanduser('~'), 'Desktop')
        else:
            return os.path.expanduser('~')
    
    def browse_output_folder(self):
        """Open a folder browser dialog"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.outputFolderLineEdit.text()
        )
        if folder:
            self.outputFolderLineEdit.setText(folder)
    

    def log(self, message):
        """Add a message to the log"""
        self.logTextEdit.append(message)
        # Ensure the latest message is visible
        self.logTextEdit.ensureCursorVisible()


    def validate_inputs(self):
        """Validate user inputs"""

        # Check if layers are selected
        if not self.navaidLayerComboBox.currentLayer():
            self.log("Error: Please select a point layer for navigation aid")
            return False
        
        if not self.thresholdLayerComboBox.currentLayer():
            self.log("Error: Please select a point layer for the Threshold")
            return False

        if not self.runwayLayerComboBox.currentLayer():
            self.log("Error: Please select a runway layer")
            return False
        
        # Check if navaid layer is in WGS84
        navaid_layer = self.navaidLayerComboBox.currentLayer()
        if not navaid_layer.crs().authid() == 'EPSG:4326':
            self.log("Warning: NAVAID layer should be in WGS84 (EPSG:4326)")
            # Continue anyway, but warn the user

        # Check if threshold layer is in WGS84
        navaid_layer = self.thresholdLayerComboBox.currentLayer()
        if not navaid_layer.crs().authid() == 'EPSG:4326':
            self.log("Warning: Threshold layer should be in WGS84 (EPSG:4326)")
            # Continue anyway, but warn the user
        
        # Check if runway layer is in a projected CRS
        runway_layer = self.runwayLayerComboBox.currentLayer()
        if runway_layer.crs().isGeographic():
            self.log("Warning: Runway layer should be in a projected coordinate system")
            # Continue anyway, but warn the user
        
        # Check if output folder exists
        output_folder = self.outputFolderLineEdit.text()
        if not os.path.exists(output_folder):
            try:
                os.makedirs(output_folder)
                self.log(f"Created output folder: {output_folder}")
            except Exception as e:
                self.log(f"Error creating output folder: {str(e)}")
                return False
        
        return True

    def populate_track_offset(self):
        if not self.validate_inputs():
            return
        navaid_layer = self.navaidLayerComboBox.currentLayer()
        thr_layer = self.thresholdLayerComboBox.currentLayer()
        runway_layer = self.runwayLayerComboBox.currentLayer()
        from .modules.np_final_app import calculate_offset
        fat_direction = self.directionFATComboBox.currentText()
        offset_value = calculate_offset(navaid_layer,thr_layer,runway_layer,fat_direction)
        self.trackOffsetSpinBox.setValue(offset_value)
        self.trackOffsetUnitsComboBox.setCurrentText(QPANSOPYUnit._abbreviation[QPANSOPYUnitType.DEGREES])


    def calculate(self):
        """Run the calculation"""

        self.log("Starting calculation...")
        
        # Validate inputs
        if not self.validate_inputs():
            return
        
        # Get parameters
        ##TODO: this step can be skipped, and parameters dict can be populated directly
        navaid_layer = self.navaidLayerComboBox.currentLayer()
        thr_layer = self.thresholdLayerComboBox.currentLayer()
        runway_layer = self.runwayLayerComboBox.currentLayer()
        input_theshold_elevation = self.thresholdElevationSpinBox.value()
        theshold_elevation_units = self.thresholdElevationUnitsComboBox.currentText()
        construct_trk_tol:bool = self.drawTrackToleranceCheckBox.isChecked()
        segment_len_units:str = self.distanceUnitsComboBox.currentText()
        navaid_type:str = self.navaidTypeComboBox.currentText()
        input_segment_length:float = self.segmentLengthSpinBox.value()
        fat_direction:str = self.directionFATComboBox.currentText()
        input_track_offset:float = self.trackOffsetSpinBox.value()
        track_offset_units:float = self.trackOffsetUnitsComboBox.currentText()
        export_kml = self.exportKmlCheckBox.isChecked()
        output_dir = self.outputFolderLineEdit.text()

        
        #Setup the segment length units
        if segment_len_units == QPANSOPYUnit._abbreviation[QPANSOPYUnitType.METRE]:
            segment_len = QPANSOPYUnit(input_segment_length,QPANSOPYUnitType.METRE)
        elif segment_len_units == QPANSOPYUnit._abbreviation[QPANSOPYUnitType.NAUTICAL_MILES]:
            segment_len = QPANSOPYUnit(input_segment_length,QPANSOPYUnitType.NAUTICAL_MILES)
        else:
            raise NotImplementedError("Units '{}' are not currently supported".format(segment_len_units))


        #setup the track offset units
        if track_offset_units == QPANSOPYUnit._abbreviation[QPANSOPYUnitType.DEGREES]:
            track_offset = QPANSOPYUnit(input_track_offset,QPANSOPYUnitType.DEGREES)
        elif track_offset_units == QPANSOPYUnit._abbreviation[QPANSOPYUnitType.RADIANS]:
            track_offset = QPANSOPYUnit(input_track_offset,QPANSOPYUnitType.RADIANS)
        elif track_offset_units == QPANSOPYUnit._abbreviation[QPANSOPYUnitType.PERCENT]:
            track_offset = QPANSOPYUnit(input_track_offset,QPANSOPYUnitType.PERCENT)
        else:
            raise NotImplementedError("Units '{}' are not currently supported".format(segment_len_units)) 

        #Setup the threshold elevation units
        if theshold_elevation_units == QPANSOPYUnit._abbreviation[QPANSOPYUnitType.FEET]:
            theshold_elevation = QPANSOPYUnit(input_theshold_elevation,QPANSOPYUnitType.FEET)
        elif theshold_elevation_units == QPANSOPYUnit._abbreviation[QPANSOPYUnitType.METRE]:
            theshold_elevation = QPANSOPYUnit(input_theshold_elevation,QPANSOPYUnitType.METRE)
        else:
            raise NotImplementedError("Units '{}' are not currently supported".format(segment_len_units))         


        
        # Prepare parameters
        params = {
            'navaid_layer': navaid_layer,
            'thr_layer': thr_layer,
            'runway_layer': runway_layer,
            'construct_trk_tol': construct_trk_tol,
            'navaid_type': navaid_type,
            'segment_len': segment_len,
            'FAT_direction': fat_direction,
            'track_offset': track_offset,
            'threshold_elevation': theshold_elevation,
            'export_kml': export_kml,
            'output_dir': output_dir,
        }
        
        try:
            # Run calculation based on Navaid type
            if navaid_type == "NDB" or navaid_type == "VOR":
                self.log("Running {} splay calculation...".format(navaid_type))
                # Import here to avoid circular imports
                from .modules.np_final_app import calculate_np_final_approach
                result = calculate_np_final_approach(self.iface, thr_layer,navaid_layer, runway_layer, params,self.log)
            elif navaid_type == "LOC":
                iface.messageBar().pushMessage("Error", "LOC not yet implimented", level=Qgis.Critical)
            elif navaid_type == "DF":
                iface.messageBar().pushMessage("Error", "DF not yet implimented", level=Qgis.Critical)
            elif navaid_type == "PSR":
                iface.messageBar().pushMessage("Error", "PSR not yet implimented", level=Qgis.Critical)
            else:
                raise TypeError("Invalid Navaid Type Selection: ",navaid_type)
            
            
            #Log results
            if result:
                if export_kml:
                    self.log(f"{navaid_type} KML exported to: {result.get('kml_path', 'N/A')}")
                self.log(f"{navaid_type} calculation completed successfully!")
            else:
                self.log("Calculation completed but no results were returned.")
                
        except Exception as e:
            self.log(f"Error during calculation: {str(e)}")
            import traceback
            self.log(traceback.format_exc())