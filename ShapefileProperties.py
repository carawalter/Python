# Purpose: Extract shapefile shape parameters
# Contains code modified from https://www.e-education.psu.edu/geog485/book/export/html/59, ArcGIS 10 help
#                          OSU GEO 599: https://dl.dropbox.com/u/37858409/Geo599_GIS_Programming/07_3_AccessingAttributes.html
# Created by: Cara Walter
# Modified: 2/27/2013

import arcpy 

################################################
# Purpose: Extract feature polygon areas
# Input: PolygonShapefile - Polygon shapefile
# Output: PolyAreas - List of polygon areas
def Area(PolygonShapefile):
    try:
        # Create search cursor
        rows = arcpy.SearchCursor(PolygonShapefile) 
        
        # extract the name of the Shape (geometry) field name for the shapefile
        ShapeName = arcpy.Describe(PolygonShapefile).shapeFieldName
        
        #Create empty list
        PolygonAreas=[]
        
        # For each row, extract the area of the feature
        for row in rows:
            feat = row.getValue(ShapeName)
            PolygonAreas = PolygonAreas + [feat.area]
    
        return(PolygonAreas)
    #Print out error from Python
    except Exception as TheError:
        raise RuntimeError("An error has occurred in ShapeProperties LineArea: "+format(TheError))

################################################
# Purpose: Extract feature coordinates: X, Y, Z
# Input: Shapefile - shapefile
# Output: XYZCoords: [Feature[Point[(X,Y,Z)]]]
# code modified from: http://help.arcgis.com/en/arcgisdesktop/10.0/help/index.html#//002z0000001t000000

def Coordinates(Shapefile):
    try:
        # Create search cursor
        rows = arcpy.SearchCursor(Shapefile) 
        
        # extract the name of the Shape (geometry) field name for the shapefile
        ShapeName = arcpy.Describe(Shapefile).shapeFieldName
        
        # Create empty list for all features
        XYZAllFeatures=[]
        
        # Enter loop for each row
        for row in rows:
            # Create the geometry object
            feat = row.getValue(ShapeName)
            # Create counter for each part of each feature
            partnum=0
            # Create empty list for the coordinates of each feature
            XYZIndivFeature=[]
            # Step through each part of the feature - make each feature part of a list
            for part in feat:  
                # Step through each vertex in the feature - make each point a tuple (list within list)
                for pnt in feat.getPart(partnum):
                    XYZIndivFeature=XYZIndivFeature+[(pnt.X,pnt.Y,pnt.Z)]
                             
                partnum += 1
                
            XYZAllFeatures=XYZAllFeatures+[XYZIndivFeature]
        return(XYZAllFeatures)
    #Print out error from Python
    except Exception as TheError:
        raise RuntimeError("An error has occurred in ShapeProperties Coordinates: "+format(TheError))

############################################
# Purpose: Extract feature line lengths
# Input: PolyShapefile - Polyline or polygon shapefile
# Output: PolyLengths - List of polyline lengths
def Length(PolyShapefile):
    try:
        # Create search cursor
        rows = arcpy.SearchCursor(PolyShapefile)
        
        # extract the name of the Shape (geometry) field name for the shapefile
        ShapeName = arcpy.Describe(PolyShapefile).shapeFieldName
        
        #Create empty list
        PolyLengths=[]
        
        # For each row, extract the length of the feature
        for row in rows:
            feat = row.getValue(ShapeName)
            PolyLengths= PolyLengths + [feat.length]
    
        return(PolyLengths)
    #Print out error from Python
    except Exception as TheError:
        raise RuntimeError("An error has occurredin ShapeProperties LineLength: "+format(TheError))

############################################
# Purpose: Extract list from a field
# Input: TheShapefile
#        TheField - string for field name
# Output: TheList - List of field entries
def ListFromField(TheShapefile,TheField):
    try:
        # Create search cursor
        rows = arcpy.SearchCursor(TheShapefile,"","",TheField)
        
        #Create empty list
        TheList=[]
        
        # Loop through each row in the attribute field and add to list
        for row in rows:
            TheList= TheList + [row.getValue(TheField)]
    
        return(TheList)
    #Print out error from Python
    except Exception as TheError:
        raise RuntimeError("An error has occurred in ShapeProperties ListFromField: "+format(TheError))

############################################
# Purpose: Determine which type of shapefile
# Input: Shapefile - point, polyline or polygon shapefile
# Output: ShpType - string of shapefile type
def ShapefileType(Shapefile):
    try:
      
        # extract the type of the Shape (geometry) field name for the shapefile
        ShpType = arcpy.Describe(Shapefile).shapeType
        
        return(ShpType)
    #Print out error from Python
    except Exception as TheError:
        raise RuntimeError("An error has occurred in ShapeType: "+format(TheError))


############################################
# Purpose: Extract spatial reference
# Input: TheFile - shapefile or raster name and path
# Output: OutParameter - name of the spatial reference as a string
def SpatialReference(TheFile):
    try:
        TheSpatialReference = arcpy.Describe(TheFile).SpatialReference
        
        return(TheSpatialReference)

    #Print out error from Python
    except Exception as TheError:
        raise RuntimeError("An error has occurred in ShapeProperties SpatialReference: "+format(TheError))




        
