#######################################################################
# RiverCorridorPolygons
#
# Purpose: Create evenly spaced polygons perpendicular to the centerline of a single polygon with ~4 sides
#
# Created by: Cara Walter
#
# Input: TheInPolyFile - the name of a polygon feature class with 1 polygon with ~4 sides (2 sides, 2 ends)
#        TheInPointFile - the name of a point feature class with the 4 corner points to split the polygon at
#             ***Must have "Id" field with 0 for DS left, 1 for DS right, 10 for US left, 11 for US right
#        MaxWidth - numeric value for the largest distance between side boundaries segmented will be created perpendicular to
#        SplitLength - number specifying interval at which to split polygon 
#
# Required Script Files: AnalysisInterface, CartographyInterface, ManagementInterface, Polygon2CenterlineModule,
#                       MessagingModule, ShapefileProperties, SplitLineModule
#
# Output: (name same as input shapefile with suffix): 
#   Intermediate (in IntermediateFiles): 
#     Polygon2CenterlineModule:
#        _rawpolyline.shp (RawPolyline): output of conversion from input polygon to polyline
#        _boundarypolyline.shp  (BoundaryRawPolyline): raw polyline split into individual lines at the input corner points (plus raw polyline end)
#        _mergedpolyline.shp (MergedBoundaries): if the polyline was split at more than the 4 corners, this polyline is created which contains polylines only split at the four corners
#        _finalsidepolylines.shp (FinalBoundaries): the two side polylines
#        _centerlinepolyline.shp (CenterlinePolyline): the centerline polyline between the two side polylines
#
#     _simplecenterline.shp (SimpleCenterline): created if the user selects, the centerline minus bends within a tolerance of 0.1 * Maximum width
#     _smoothcenterline.shp (SmoothCenterline): created if the user selects, the simple centerline smoothed
#
#     SplitLineModule:
#        _single.shp (PolylineSingle): shapefile with polylines merged if input had more than one polyline
#        _random_points.shp (PointName): points along input polyline at specified spacing
#        _copy_points.shp (PointNameCopy): two sets of points along input polyline at specified spacing
#        _segmented_line.shp (LineSegmented): the output split polylines
#
#   Final: 
#        _segmented.shp (BufferShp): raw polygons created from buffering to either side of the segmented centerline to a distance of max width * 0.6
#
# Process:
#         1) Check input files and setup outputs
#         2) Polygon2CenterlineModule
#               a) Convert boundary polygon to polylines 
#               b) Split polylines using points
#               c) Ensure polylines are only split at points
#               d) Select and create new layer only with 2 boundary (longest) polylines
#               e) Convert boundary polylines to centerline
#               f) Check to see if any part of the centerline is still on top of side lines
#         3) Simplify and smooth centerline if selected
#         4) SplitLineModule
#               a) Check to see if polyline contains single, continous feature - try to fix if not
#               b) Create evenly spaced points along the centerline
#               c) Duplicate the points and append original points to duplicate points shapefile to create 
#                    start and end points for each line segment
#               d) Use points to line tool to create segmented line (use CID field as unique line identifier)
#               e) Add distance from start to attribute table in "Station" field
#         5) Use Buffer to create polygons from centerline
#
#         arcpy.management.SplitLineAtPoint supposedly does part of this, but it is unreliable
#
# Modified: 3/18/2013
#######################################################################
try:
	import os
	import AnalysisInterface as AnalysisGIS
	import CartographyInterface as CartGIS
	import ManagementInterface as MgmtGIS
	import ShapefileProperties as ShpProp
	from Polygon2CenterlineModule import Polygon2Centerline
	from SplitLineModule import SplitLine
	from MessagingModule import MessageSwitch

	### Setup classes, etc.
	'''Variable to set running as ArcGIS tool (1=True) or not (0=False)'''
	AsArcGISTool=1

	# Create instances of classes
	AInterface=AnalysisGIS.AnalysisInterface()
	MgmtInterface=MgmtGIS.ManagementInterface()
	CartInterface=CartGIS.CartographyInterface()
	
	### Input file and paths if running as ArcGIS tool
	####### simplify not working in GIS
	if AsArcGISTool==1:
		# Get parameters from ArcGIS
		import arcpy
		StartAnswer=arcpy.GetParameterAsText(0)
		if StartAnswer=="false":
			StartAnswer=False
			CenterlinePolyline=arcpy.GetParameterAsText(2)
		else:
			StartAnswer=True
		TheInPolyFile=arcpy.GetParameterAsText(1)
		if TheInPolyFile=='':
			SkipBoundary=1
		else:
			SkipBoundary=0	
		TheInPointFile=arcpy.GetParameterAsText(3)
		TheOutFilePath=arcpy.GetParameterAsText(4)
		MaxWidth=float(arcpy.GetParameterAsText(5))
		SplitLength=float(arcpy.GetParameterAsText(6))
		SimplifyAnswer=arcpy.GetParameterAsText(7)
		if SimplifyAnswer=="true":
			SimplifyAnswer=True
		# Extract just the polygon file name
		TheFileName=os.path.basename(TheInPolyFile)
	
	### Input file and paths if running outside of ArcGIS
	else:
		# import library for file dialog gui
		from tkFileDialog import askopenfilename,askdirectory
		from tkMessageBox import askyesno
		#import dialog for numeric and string inputs
		from tkSimpleDialog import askfloat

		# prevent root window from opening
		from Tkinter import Tk
		Tk().withdraw()
				
		# ask for input polygon shapefile (returns name and path)
		TheInPolyFile=askopenfilename(filetypes=[("Shapefiles","*.shp")],
	                                      title="Select input boundary shapefile")

		# ask for starting point: boundary or centerline
		StartAnswer=askyesno("Start Layer","Starting with boundary (yes) or centerline (no)?")                    		

		SkipBoundary=0
		# abort if no file selected
		if TheInPolyFile=='':
			if StartAnswer:
				raise RuntimeError("No input file selected.  Script will abort.")
			# Warn if no file selected and starting with centerline
			else:
				SkipBoundary=1
				print("No input boundary selected.  Script will stop after buffering.")

		# check to make sure the input shapefile is a polygon
		InType=ShpProp.ShapefileType(TheInPolyFile)
		# Abort if not a polygon
		if InType!="Polygon":
			raise RuntimeError("Input file is not a polygon.  Script will abort.")

		if StartAnswer:
			# ask for input corner points shapefile
			TheInPointFile=askopenfilename(filetypes=[("Shapefiles","*.shp")],
				                       title="Select input corner points shapefile")
			# abort if no file selected
			if TheInPointFile=='':
				raise RuntimeError("No input file selected. Script will abort.")
	
			# check to make sure the input shapefile is points
			InType=ShpProp.ShapefileType(TheInPointFile)
			# Abort if not point type
			if InType!="Point":
				raise RuntimeError("Input file is not points. Script will abort.")
			
			# Extract just the polygon file name
			TheFileName=os.path.basename(TheInPolyFile)
			TheFileName=TheFileName[0:-4]			
			
		else:
			# ask for input centerline polyline shapefile (returns name and path)
			CenterlinePolyline=askopenfilename(filetypes=[("Shapefiles","*.shp")],
		                                      title="Select input centerline shapefile")
			# abort if no file selected
			if CenterlinePolyline=='':
				raise RuntimeError("No input file selected.  Script will abort.")

			# check to make sure the input shapefile is a polyline
			InType=ShpProp.ShapefileType(CenterlinePolyline)
			# Abort if not a polygon
			if InType!="Polyline":
				raise RuntimeError("Input file is not a polyline.  Script will abort.")
			
			# Extract just the polyline file name
			TheFileName=os.path.basename(CenterlinePolyline)
			TheFileName=TheFileName[0:-4]
		
		# Ask for length of lines to split derived centerline into
		SplitLength=askfloat("Length of segments to split polygon into",
	                             "Input length of segments along centerline")
		# Abort if no value
		if SplitLength==None:
			raise RuntimeError("No value provided for split length. Script will abort.")
		
		# Ask if simplifying centerline before segmenting
		SimplifyAnswer=askyesno("Centerline","Simplify and smooth centerline?")		

		# Ask for maximum width between boundary lines
		MaxWidth=askfloat("Maximum Width","Maximum distance between side boundary lines")
		# Abort if no value
		if MaxWidth==None:
			raise RuntimeError("No value provided for maximum width.  Script will abort.")
					
		# ask for output folder (does not have to exist)
		TheOutFilePath=askdirectory(title="Specify output directory")	
		
	### Perform setup and checks
	# Make sure output folder has ending slash
	if TheOutFilePath[-1]!= u"/" or TheOutFilePath[-2:-1]!= u"\\":
		TheOutFilePath=TheOutFilePath+"/"	
	# Check to see if out folder exists, if not create it
	if os.path.isdir(TheOutFilePath)!= True:        
		os.mkdir(TheOutFilePath)

	# Create intermediate file folder if it does not exist
	IntermedOutputFolder=TheOutFilePath+"IntermediateFiles/"
	if os.path.isdir(IntermedOutputFolder)!= True:
		os.mkdir(IntermedOutputFolder)
	
	if StartAnswer:
		# Convert polygon to centerline
		Centerline_Flip=Polygon2Centerline(TheInPolyFile,TheInPointFile,TheOutFilePath,MaxWidth,AsArcGISTool)
		if Centerline_Flip==[]:
			message="Polygon2Centerline failed. Script will abort"
			MessageSwitch(AsArcGISTool,message)
			x=1/0
	
		# Extract centerline polyline name and path
		CenterlinePolyline=Centerline_Flip[0]
		# Extract centerline orientation indicator
		FlipCenterline=Centerline_Flip[1]
	else:
		FlipCenterline=0
		
	### Simplify and smooth centerline if user answered yes
	if SimplifyAnswer:
		# Update user on process
		message="Simplifying and smoothing centerline..."
		MessageSwitch(AsArcGISTool,message)
		
		SimpleCenterline=IntermedOutputFolder+TheFileName+"_simplecenterline.shp"
		CartInterface.SimpleLine(CenterlinePolyline,SimpleCenterline,"BEND_SIMPLIFY",format(MaxWidth*.2))
		SmoothCenterline=IntermedOutputFolder+TheFileName+"_smoothcenterline.shp"
		CartInterface.SmoothLine(SimpleCenterline,SmoothCenterline,"PAEK",format(MaxWidth*.2),"#","NO_CHECK")
	else:
		SmoothCenterline=CenterlinePolyline

	### Split centerline into specified lengths
	# Update user on process
	message="Splitting centerline into segments..."
	MessageSwitch(AsArcGISTool,message)
	
	SegmentedCenterline=SplitLine(SmoothCenterline,IntermedOutputFolder,SplitLength,AsArcGISTool,FlipCenterline)

	### Start process of converting centerline to segmented polygons
	# Update user on process
	message="Buffering polylines to create polygons..."
	MessageSwitch(AsArcGISTool,message)
	
	# Create polygons from polylines
	# Name of buffered shapefile
	BufferShp=TheOutFilePath+TheFileName+"_segmented.shp"
	# Buffer to 0.6 max width every other polyline
	AInterface.Buffer(SegmentedCenterline,BufferShp,format(MaxWidth*.6),"FULL","FLAT","NONE","#")
	
	# Clean up attribute table
	MgmtInterface.DeleteField(BufferShp,"BUFF_DIST")
	
	# Update user on process
	message="Segmented polygons created."
	MessageSwitch(AsArcGISTool,message)
	
	if SkipBoundary:
		message="Processing complete after buffering."
		MessageSwitch(AsArcGISTool,message)
	# keep going to fill gaps		
	else:
		# Update user on process
		message="Filling gaps between polygons"
		MessageSwitch(AsArcGISTool,message)		
		
		# Clip buffered polygon to boundary, create polygons in gaps
		IDPolygons=IntermedOutputFolder+TheFileName+"_segmented_ID.shp"
		AInterface.Identity(TheInPolyFile,BufferShp,IDPolygons,"ALL","#","#")
		
		# Select areas which are not same as original (FID>max FID from orig) or FID = 0
		# Get max FID from orig
		TheFID=ShpProp.ListFromField(BufferShp,"FID")
		maxFID=max(TheFID)
		# Create feature layer for selection
		MgmtInterface.CreateLayer(IDPolygons,"ID_Layer")
		Statement="\"FID\" = 0 OR \"FID\" > " + str(maxFID)
		MgmtInterface.SelectUsingAttributes("ID_Layer","NEW_SELECTION",Statement)

		# Multipart to single to create shapefile with just gap fillers
		GapsShp=IntermedOutputFolder+TheFileName+"_segmented_gaps.shp"
		MgmtInterface.Multipart2Single("ID_Layer",GapsShp)		
		
		# Create new shapefile with just clipped original polygons
		MgmtInterface.SelectUsingLocation("ID_Layer","#","#","#","SWITCH_SELECTION")
		ClippedShp=IntermedOutputFolder+TheFileName+"_segmented_clipped.shp"
		MgmtInterface.CopyFeatures("ID_Layer",ClippedShp)
		
		# Run Near to associate gaps with normal polygons
		AInterface.Near(GapsShp,ClippedShp,"#","#","#")
		
		# Put Near_FID in original shapefile
		MgmtInterface.AddField(ClippedShp,"Near_FID","LONG","#","#","#")
		MgmtInterface.WriteField(ClippedShp,"Near_FID","!FID!","PYTHON")
		
		# Merge original and gaps shapefiles
		#MergedShp=IntermedOutputFolder+TheFileName+"_segmented_merged.shp"
		#MgmtInterface.MergeShapefiles([ClippedShp,GapsShp],MergedShp)
		
		# Union original and gaps shapefiles
		UnionShp=IntermedOutputFolder+TheFileName+"_segmented_union.shp"
		AInterface.Union([ClippedShp,GapsShp],UnionShp,"#","#","#")

		# if using union, transfer NEAR_FID_1 to NEAR_FID (after selecting NEAR_FID==0)
		MgmtInterface.CreateLayer(UnionShp,"Union_Layer")
		MgmtInterface.SelectUsingAttributes("Union_Layer","NEW_SELECTION","\"NEAR_FID\"=0")
		MgmtInterface.WriteField("Union_Layer","NEAR_FID","!NEAR_FID_1!","PYTHON")
		
		# Dissolve by Near_FID field
		DissShp=TheOutFilePath+TheFileName+"_segmented_diss.shp"
		MgmtInterface.Dissolve(UnionShp,DissShp,"NEAR_FID","#","SINGLE_PART","#")
		
		# Calculate station
		MgmtInterface.AddField(DissShp,"Station","DOUBLE",10,1,"#")
		MgmtInterface.WriteField(DissShp,"Station","!Near_FID! * " + str(SplitLength),"PYTHON")
		
		# Add select by area then eliminate for random remaining small pieces?
		
		message="Processing complete."
		MessageSwitch(AsArcGISTool,message)		

#Print out error from Python
except Exception as TheError:
	message="An error has occurred: "+format(TheError)
	MessageSwitch(AsArcGISTool,message)