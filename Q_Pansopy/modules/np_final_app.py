# -*- coding: utf-8 -*-
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, 
    QgsCoordinateReferenceSystem, QgsCoordinateTransform,
    QgsPointXY, QgsWkbTypes, QgsField, QgsFields, QgsPoint,
    QgsLineString, QgsPolygon, QgsVectorFileWriter, QgsCircularString, QgsCompoundCurve, QgsCurvePolygon
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
from qgis.core import Qgis
from qgis.utils import iface
from ..utilities.units import QPANSOPYUnit,QPANSOPYUnitType
import math
import os
import datetime



navaid_parameters = {"NDB": {"area_tolerance_nm":1.25,"area_splay_deg":10.3,"tracking_tolerance_deg":6.9,"fix_tolerance_deg":6.2},
                     "VOR": {"area_tolerance_nm":1.0,"area_splay_deg":7.8,"tracking_tolerance_deg":5.2,"fix_tolerance_deg":4.5},
                     "DF": {"area_tolerance_nm":3.0,"area_splay_deg":10}}


# Function to convert from PointXY and add Z value
def pz(point, z):
    cPoint = QgsPoint(point)
    cPoint.addZValue()
    cPoint.setZ(z)
    return cPoint


def draw_vor_ndb(provider: QgsVectorLayer,azimuth:float,thr_geom,thr_elev:QPANSOPYUnit, navaid_geom,navaid_type:str,length:QPANSOPYUnit,log,con_tolerance:bool) -> QgsVectorLayer:
    if navaid_type.upper() == "NDB" or navaid_type.upper() == "VOR":
        area_tolerance = QPANSOPYUnit(navaid_parameters[navaid_type.upper()]["area_tolerance_nm"],QPANSOPYUnitType.NAUTICAL_MILE)
        area_splay = QPANSOPYUnit(navaid_parameters[navaid_type.upper()]["area_splay_deg"],QPANSOPYUnitType.DEGREES)
        tracking_tolerance = QPANSOPYUnit(navaid_parameters[navaid_type.upper()]["tracking_tolerance_deg"],QPANSOPYUnitType.DEGREES)
    else:
        raise TypeError("Invalid NAVAID Type")
    
    och = QPANSOPYUnit(250,QPANSOPYUnitType.FEET)
    moc = QPANSOPYUnit(75,QPANSOPYUnitType.METRE)
    end_geom = navaid_geom.project(length.metres,azimuth)
    secondary_width_start = area_tolerance.metres
    secondary_width_end = area_tolerance.metres + length.metres*math.tan(area_splay.radians)
    primary_width_start = area_tolerance.metres / 2
    primary_width_end = secondary_width_end / 2
    primary_area_altitude_m = thr_elev.metres + och.metres - moc.metres
    secondary_area_altitude_m = thr_elev.metres + och.metres

    # Calculate surface points
    #   Primary Area
    pnt_p1 = navaid_geom.project(primary_width_start, azimuth-90)
    pnt_p2 = navaid_geom.project(primary_width_start, azimuth+90)
    pnt_p3 = end_geom.project(primary_width_end, azimuth-90)
    pnt_p4 = end_geom.project(primary_width_end, azimuth+90)
    #   Secondary Area
    pnt_s1 = navaid_geom.project(secondary_width_start, azimuth-90)
    pnt_s2 = navaid_geom.project(secondary_width_start, azimuth+90)
    pnt_s3 = end_geom.project(secondary_width_end, azimuth-90)
    pnt_s4 = end_geom.project(secondary_width_end, azimuth+90)
    # Create and add features for each surface
    #   Primary Area
    exterior_ring = [pz(pnt_p1, primary_area_altitude_m), pz(pnt_p2, primary_area_altitude_m), pz(pnt_p4, primary_area_altitude_m), pz(pnt_p3, primary_area_altitude_m)]
    feature = QgsFeature()
    feature.setGeometry(QgsPolygon(QgsLineString(exterior_ring)))
    feature.setAttributes(['primary area'])
    provider.addFeatures([feature])
    #   Secondary Area 1
    exterior_ring = [pz(pnt_p1, primary_area_altitude_m), pz(pnt_p3, primary_area_altitude_m), pz(pnt_s3, secondary_area_altitude_m), pz(pnt_s1, secondary_area_altitude_m)]
    feature = QgsFeature()
    feature.setGeometry(QgsPolygon(QgsLineString(exterior_ring)))
    feature.setAttributes(['Secondary Area'])
    provider.addFeatures([feature])
    #   Secondary Area 2
    exterior_ring = [pz(pnt_p2, primary_area_altitude_m), pz(pnt_p4, primary_area_altitude_m), pz(pnt_s4, secondary_area_altitude_m), pz(pnt_s2, secondary_area_altitude_m)]
    feature = QgsFeature()
    feature.setGeometry(QgsPolygon(QgsLineString(exterior_ring)))
    feature.setAttributes(['Secondary Area'])
    provider.addFeatures([feature])

    #Nominal Track
    line = [pz(navaid_geom,thr_elev.metres),pz(end_geom,thr_elev.metres)]
    feature = QgsFeature()
    feature.setGeometry(QgsPolygon(QgsLineString(line)))
    feature.setAttributes(['Nominal Track'])
    provider.addFeatures([feature])


    if con_tolerance:
        draw_track_tolerance(provider,tracking_tolerance,navaid_geom,length,azimuth)


def draw_loc():
    pass

def draw_df(provider,log ,azimuth,length:QPANSOPYUnit,thr_elev:QPANSOPYUnit,navaid_geom,thr_geom):
    area_tolerance = QPANSOPYUnit(navaid_parameters["DF"]["area_tolerance_nm"],QPANSOPYUnitType.NAUTICAL_MILE)
    area_splay = QPANSOPYUnit(navaid_parameters["DF"]["area_splay_deg"],QPANSOPYUnitType.DEGREES)
    inverse_splay = QPANSOPYUnit(90 - area_splay.degrees,QPANSOPYUnitType.DEGREES)
    och = QPANSOPYUnit(250,QPANSOPYUnitType.FEET)
    moc = QPANSOPYUnit(90,QPANSOPYUnitType.METRE)
    primary_alt = och.metres - moc.metres + thr_elev.metres
    splay_line_length = (area_tolerance.metres / 2) * math.cos(inverse_splay.radians) + math.sqrt(length.metres**2 - (area_tolerance.metres / 2)**2 * math.sin(inverse_splay.radians)**2)
    pnt_p1 = navaid_geom.project(area_tolerance.metres / 2,azimuth +90)
    pnt_p2 = navaid_geom.project(area_tolerance.metres / 2,azimuth -90)
    pnt_p3 = pnt_p1.project(splay_line_length,azimuth +10)
    pnt_p4 = pnt_p2.project(splay_line_length,azimuth -10)
    pnt_p5 = navaid_geom.project(length.metres,azimuth)
    circular_string = QgsCircularString()
    circular_string.setPoints([pz(pnt_p3,primary_alt),pz(pnt_p5,primary_alt),pz(pnt_p4,primary_alt)])
    line = QgsLineString([pz(pnt_p4,thr_elev.metres),pz(pnt_p2,thr_elev.metres),pz(pnt_p1,thr_elev.metres),pz(pnt_p3,thr_elev.metres)])
    #   Primary Area
    compound = QgsCompoundCurve()
    compound.addCurve(circular_string)
    compound.addCurve(line)
    poly = QgsCurvePolygon()
    poly.setExteriorRing(compound)
    feature = QgsFeature()
    geometry = QgsGeometry(poly)
    feature.setGeometry(geometry)
    feature.setAttributes(['primary area'])
    provider.addFeatures([feature])


def draw_sre():
    pass

def draw_track_tolerance(provider:QgsVectorLayer,tolerance_angle:QPANSOPYUnit,navaid_geom,length:QPANSOPYUnit,azimuth:float):

    pnt_1 = navaid_geom.project(length.metres * 1.2, azimuth+tolerance_angle.degrees)
    pnt_2 = navaid_geom.project(length.metres * 1.2, azimuth-tolerance_angle.degrees)

    line_1 = [pz(navaid_geom, 0), pz(pnt_1,0)]
    line_2 = [pz(navaid_geom, 0), pz(pnt_2,0)]
    feature = QgsFeature()
    feature.setGeometry(QgsPolygon(QgsLineString(line_1)))
    feature.setAttributes(['Tracking Tolerance'])
    provider.addFeatures([feature])
    feature = QgsFeature()
    feature.setGeometry(QgsPolygon(QgsLineString(line_2)))
    feature.setAttributes(['Tracking Tolerance'])
    provider.addFeatures([feature])


def calculate_np_final_approach(iface, threshold_layer,naviad_layer, runway_layer, params,log) -> dict:
    """
    Create a non-precision Final Approach Surface for the selected NAVAID
    
    :param iface: QGIS interface
    :param threshold_layer: Point layer with the threshold point (WGS84)
    :param navaid_layer: Point layer with the navaid point (WGS84)
    :param runway_layer: Runway layer (projected CRS)
    :param params: Dictionary with calculation parameters
    :return: Dictionary with results
    """

    # Extract parameters
    construct_trk_tol:bool = params.get('construct_trk_tol',False)
    thr_elev:QPANSOPYUnit = params.get('threshold_elevation')
    navaid_type:str = params.get('navaid_type')
    length:QPANSOPYUnit = params.get('segment_len')
    offset_angle:QPANSOPYUnit = params.get("track_offset")
    export_kml:bool = params.get('export_kml', True)
    output_dir = params.get('output_dir', os.path.expanduser('~'))
    FAT_direction:str = params.get("FAT_direction","TO NAVAID")

    
    # Check if layers exist
    if not threshold_layer or not runway_layer or not naviad_layer:
        iface.messageBar().pushMessage("Error", "Threshold, navaid or runway layer not provided", level=Qgis.Critical)
        return None
    
    # Check if layers have features
    if threshold_layer.featureCount() == 0:
        iface.messageBar().pushMessage("Error", "Threshold layer has no features", level=Qgis.Critical)
        return None
    
    if runway_layer.featureCount() == 0:
        iface.messageBar().pushMessage("Error", "Runway layer has no features", level=Qgis.Critical)
        return None
    
    if naviad_layer.featureCount() == 0:
        iface.messageBar().pushMessage("Error", "Navaid layer has no features", level=Qgis.Critical)
        return None
    
    # Get the threshold point
    thr_feature = next(threshold_layer.getFeatures())
    thr_geom = thr_feature.geometry().asPoint()

    # Get the navaid point
    naviad_feature= next(naviad_layer.getFeatures())
    navaid_geom = naviad_feature.geometry().asPoint()
    
    # Get the runway line
    runway_feature = next(runway_layer.getFeatures())
    runway_geom = runway_feature.geometry().asPolyline()
    
    # Get map CRS
    map_srid = iface.mapCanvas().mapSettings().destinationCrs().authid()
    
    # Calculate azimuth
    start_point = QgsPoint(runway_geom[0])
    end_point = QgsPoint(runway_geom[1])
    angle0 = start_point.azimuth(end_point) % 360
    
    # Use end of runway for calculation
    s = -1
    if s == -1:
        s2 = 0
    else:
        s2 = 180
    
    runway_azimuth = angle0 + s2
    runway_back_azimuth = (runway_azimuth + 180) % 360
    point_of_intersect = thr_geom.project(1400,runway_back_azimuth)
    largest_offset = navaid_geom.azimuth(point_of_intersect) % 360
    
    max_offset = largest_offset - runway_back_azimuth
    if max_offset < 0:
        direction = "Right of centreline"
    else:
        direction = "Left of centreline"
    log(f"Maximum offset angle for this approach is: {abs(math.floor(max_offset*10000)/10000)}° {direction}")
    
    ##Calculate the direction to draw the final approach track
    if FAT_direction.startswith("TO") or navaid_type == "DF":
        track_azimuth = (runway_back_azimuth + offset_angle.degrees) % 360
    elif FAT_direction.startswith("FROM"):
        track_azimuth = (runway_back_azimuth + offset_angle.degrees - 180) % 360
    else:
        raise TypeError("Direction is not valid string")
    if abs(offset_angle.degrees) > abs(max_offset):
        log("Warning: FAT intersects runway centreline too close to the Threshold")


    # Create memory layer
    if navaid_type == "DF":
        v_layer = QgsVectorLayer("CurvePolygon?crs=" + map_srid, "{}_Final_Approach_Surfaces".format(navaid_type), "memory")
    else:
        v_layer = QgsVectorLayer("PolygonZ?crs=" + map_srid, "{}_Final_Approach_Surfaces".format(navaid_type), "memory")
    
    provider = v_layer.dataProvider()
    


    'Curved Features'
    # Add fields
    provider.addAttributes([
        QgsField('{}_Final_Approach_Surface'.format(navaid_type), QVariant.String)
    ])
    v_layer.updateFields()

    if navaid_type == "LOC":
        draw_loc()
    elif navaid_type == "DF":
        draw_df(provider,log ,track_azimuth,length,thr_elev,navaid_geom,thr_geom)
    elif navaid_type == "PSR":
        draw_sre()
    elif navaid_type == "NDB" or navaid_type == "VOR":
        draw_vor_ndb(provider,track_azimuth,thr_geom,thr_elev, navaid_geom,navaid_type,length,log,construct_trk_tol)
    else:
        iface.messageBar().pushMessage("Error", "Navaid Type selection is invalid", level=Qgis.Critical)


    # Update layer extents
    v_layer.updateExtents()
    
    # Style the layer - green with 50% opacity as requested by client
    v_layer.renderer().symbol().setColor(QColor(0, 255, 0, 127))  # Green with 50% opacity
    v_layer.renderer().symbol().symbolLayer(0).setStrokeColor(QColor(0, 255, 0))
    v_layer.renderer().symbol().symbolLayer(0).setStrokeWidth(0.7)
    
    # Add layer to the project
    QgsProject.instance().addMapLayer(v_layer)
    
    # Zoom to layer
    v_layer.selectAll()
    canvas = iface.mapCanvas()
    canvas.zoomToSelected(v_layer)
    v_layer.removeSelection()
    
    # Export to KML if requested

    result = {
        '{}_layer'.format(navaid_type): v_layer
    }
    
    if export_kml:
        # Get current timestamp for unique filenames
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Define KML export path
        kml_export_path = os.path.join(output_dir, f'Final_Approach_{navaid_type}_Surfaces_{timestamp}.kml')
        
        # Export to KML
        crs = QgsCoordinateReferenceSystem("EPSG:4326")
        
        kml_error = QgsVectorFileWriter.writeAsVectorFormat(
            v_layer,
            kml_export_path,
            'utf-8',
            crs,
            'KML',
            layerOptions=['MODE=2']
        )
        
        # Correct KML structure for better visualization
        def correct_kml_structure(kml_file_path):
            with open(kml_file_path, 'r') as file:
                kml_content = file.read()
            
            # Add altitude mode
            kml_content = kml_content.replace('<Polygon>', '<Polygon>\n  <altitudeMode>absolute</altitudeMode>')
            
            # Add style - green with 50% opacity
            style_kml = '''
            <Style id="style1">
                <LineStyle>
                    <color>ff00ff00</color>
                    <width>2</width>
                </LineStyle>
                <PolyStyle>
                    <fill>1</fill>
                    <color>ff00ff7F</color>
                </PolyStyle>
            </Style>
            '''
            
            kml_content = kml_content.replace('<Document>', f'<Document>{style_kml}')
            kml_content = kml_content.replace('<styleUrl>#</styleUrl>', '<styleUrl>#style1</styleUrl>')
            
            with open(kml_file_path, 'w') as file:
                file.write(kml_content)
        
        # Apply corrections to KML file
        if kml_error[0] == QgsVectorFileWriter.NoError:
            correct_kml_structure(kml_export_path)
            result['kml_path'] = kml_export_path
    
    # Zoom to appropriate scale
    sc = canvas.scale()
    if sc < 20000:
        sc = 20000
    canvas.zoomScale(sc)
    
    # Show success message
    iface.messageBar().pushMessage("QPANSOPY:", f"Final Appraoch {navaid_type} Surfaces created successfully", level=Qgis.Success)
    
    return result
        

def calculate_offset(naviad,threshold,runway,direction:str) -> float:
    if naviad is None or threshold is None or runway is None:
        return None
    else:
        # Get the threshold point
        thr_feature = next(threshold.getFeatures())
        thr_geom = thr_feature.geometry().asPoint()

        # Get the navaid point
        naviad_feature= next(naviad.getFeatures())
        navaid_geom = naviad_feature.geometry().asPoint()
        
        # Get the runway line
        runway_feature = next(runway.getFeatures())
        runway_geom = runway_feature.geometry().asPolyline()

        start_point = QgsPoint(runway_geom[0])
        end_point = QgsPoint(runway_geom[1])
        runway_azimuth = start_point.azimuth(end_point) % 360
        runway_back_azimuth = (runway_azimuth + 180) % 360
        point_of_intersect = thr_geom.project(1400,runway_back_azimuth)
        
        if direction.startswith("TO"):
            largest_offset = navaid_geom.azimuth(point_of_intersect) % 360
            
        elif direction.startswith("FROM"):
            largest_offset = (navaid_geom.azimuth(point_of_intersect)+180) % 360
        else:
            raise TypeError("Direction is not valid string")
        
        return largest_offset - runway_back_azimuth


    