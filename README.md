# RiverCorridorPolygons

 Purpose: Create evenly spaced polygons perpendicular to the centerline of a single polygon with ~4 sides

 Created by: Cara Walter (carawalter0@gmail.com)

Required Script Files: AnalysisInterface, CartographyInterface, ManagementInterface, Polygon2CenterlineModule, MessagingModule, RiverCorridorPolygons, ShapefileProperties, SplitLineModule

***To run via command line outside of ArcGIS, change AsArcGISTool in RiverCorridorPolygons line 77 to equal 0

 Input: 
	1) TheInPolyFile - the name of a polygon feature class with 1 polygon with ~4 sides (2 sides, 2 ends)
        2) TheInPointFile - the name of a point feature class with the 4 corner points to split the polygon at
             *****Point shapefile must have "Id" field with 0 for DS left, 1 for DS right, 10 for US left, 11 for US right
        
	3) MaxWidth - numeric value for the largest distance between side boundaries segmented will be created perpendicular to
        4) SplitLength - number specifying interval at which to split polygon 

 Output: (name same as input shapefile with suffix): 
   Intermediate (in IntermediateFiles): 
     Polygon2CenterlineModule:
        1) _rawpolyline.shp (RawPolyline): output of conversion from input polygon to polyline
        2) _boundarypolyline.shp  (BoundaryRawPolyline): raw polyline split into individual lines at the input corner points (plus raw polyline end)
        3) _mergedpolyline.shp (MergedBoundaries): if the polyline was split at more than the 4 corners, this polyline is created which contains polylines only split at the four corners
        4) _finalsidepolylines.shp (FinalBoundaries): the two side polylines
        5) _centerlinepolyline.shp (CenterlinePolyline): the centerline polyline between the two side polylines

     6) _simplecenterline.shp (SimpleCenterline): created if the user selects, the centerline minus bends within a tolerance of 0.1 * Maximum width

     SplitLineModule:
        7) _single.shp (PolylineSingle): shapefile with polylines merged if input had more than one polyline
        8) _random_points.shp (PointName): points along input polyline at specified spacing
        9) _copy_points.shp (PointNameCopy): two sets of points along input polyline at specified spacing
        10) _segmented_line.shp (LineSegmented): the output split polylines

   Final: 
        11) _segmented.shp (BufferShp): raw polygons created from buffering to either side of the segmented centerline to a distance of max width * 0.6


 Process:
         1) Check input files and setup outputs
         2) Polygon2CenterlineModule
               a) Convert boundary polygon to polylines 
               b) Split polylines using points
               c) Ensure polylines are only split at points
               d) Select and create new layer only with 2 boundary (longest) polylines
               e) Convert boundary polylines to centerline
               f) Check to see if any part of the centerline is still on top of side lines
         3) Simplify centerline if selected
         4) SplitLineModule
               a) Check to see if polyline contains single, continous feature - try to fix if not
               b) Create evenly spaced points along the centerline
               c) Duplicate the points and append original points to duplicate points shapefile to create 
                    start and end points for each line segment
               d) Use points to line tool to create segmented line (use CID field as unique line identifier)
               e) Add distance from start to attribute table in "Station" field
         5) Use Buffer to create polygons from centerline

         arcpy.management.SplitLineAtPoint supposedly does part of this, but it is unreliable


 Modified: 3/19/2013
