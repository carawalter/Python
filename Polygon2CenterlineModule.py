#######################################################################
# Polygon2CenterlineModule
#
# Purpose: Convert a 4-sided polygon to a polyline centerline between the two specified sides
#
# Created by: Cara Walter
#
# Input: TheInPolyFile - the name of a polygon feature class with 1 polygon
#        TheInPointFile - the name of a point feature class with the 4 corner points to split the polygon at
#                ***Must have "Id" field with 0 for DS left, 1 for DS right, 10 for US left, 11 for US right
#        TheOutFilePath: the path of the folder to put the output shapefiles in
#        MaxWidth - numeric value for the largest distance between boundaries
#        AsArcGISTool: binary specifying if running as a GIS tool (1) or not (0) to control messaging
#
# Output: _centerlinepolyline.shp:(CenterlinePolyline) - a polyline centered between the two specified boundary sides
#
# Returns: [CenterlinePolyline, FlipCenterline] as a list
#
# Process:
#         1) Convert boundary polygon to polylines 
#         2) Split polylines using points
#         3) Ensure polylines are only split at points
#         4) Select and create new layer only with boundary (longest) polylines
#         5) Convert boundary polylines to centerline
#
# Modified: 3/17/2013
#######################################################################
def Polygon2Centerline(TheInPolyFile,TheInPointFile,TheOutFilePath,MaxWidth,AsArcGISTool):
	try:
		import os
		from math import sqrt
		import AnalysisInterface as AnalysisGIS
		import CartographyInterface as CartGIS
		import ManagementInterface as MgmtGIS
		import ShapefileProperties as ShpProp
		from SplitLineModule import SplitLine
		from MessagingModule import MessageSwitch

		### Setup classes, etc.
		# Create instances of classes
		AInterface=AnalysisGIS.AnalysisInterface()
		MgmtInterface=MgmtGIS.ManagementInterface()
		CartInterface=CartGIS.CartographyInterface()  

		# Extract just the polygon file name
		TheFileName=os.path.basename(TheInPolyFile)
		if AsArcGISTool==0:
			TheFileName=TheFileName[0:-4]

		#Determine how many input polygon features there are
		NumFeatures=MgmtInterface.CountRows(TheInPolyFile)

		# Check to see if there is other than 1 features and abort if so
		message="Input polygon file has more or less than 1 feature.  Script will abort."
		if NumFeatures!=1:
			MessageSwitch(AsArcGISTool,message)
			x=1/0

		#Determine how many input point features there are
		NumPoints=MgmtInterface.CountRows(TheInPointFile)

		# Check to see if there is other than 4 features and abort if so
		message="Input point file has more or less than 4 points.  Script will abort."
		if NumPoints!=4:
			MessageSwitch(message,AsArcGISTool)
			x=1/0			

		# Check to make sure points shapefile has Id field with more than just 0s
		# Get Id field entries
		IdFieldList=ShpProp.ListFromField(TheInPointFile,"Id")
		# Loop through Id field checking entries
		for Id in IdFieldList:
			if ((Id == 0) or (Id == 1) or (Id == 10) or (Id == 11)):
				""
			else:
				message=("Input point file Id field does not contain the "+ 
				"correct identifying numbers \n"+
				"(0: DS Left, 1: DS Right, 10: US Left, 11: US Right)." +
				"Check Read Me for details.  Script will abort.\n")		
				MessageSwitch(message,AsArcGISTool)		
				x=1/0
		
		# Make sure output folder has ending slash
		if TheOutFilePath[-1] != u"/" or TheOutFilePath[-2:-1] != u"\\":
			TheOutFilePath=TheOutFilePath+"/"	
		# Check to see if out folder exists, if not create it
		if os.path.isdir(TheOutFilePath)!= True:        
			os.mkdir(TheOutFilePath)
	
		# Create intermediate file folder if it does not exist
		IntermedOutputFolder=TheOutFilePath+"IntermediateFiles/"
		if os.path.isdir(IntermedOutputFolder)!= True:
			os.mkdir(IntermedOutputFolder)

		### Convert polygon to polyline
		# Update user on process
		message="Converting " + TheFileName+ " to polyline..."
		MessageSwitch(AsArcGISTool,message)
		RawPolyline=IntermedOutputFolder+TheFileName+"_rawpolyline.shp"		
		MgmtInterface.Polygon2Polyline(TheInPolyFile,RawPolyline,"","ATTRIBUTES")
	
		### Split the resulting polyline at the corner points
		# Update user on process
		message="Splitting polyline at points..."
		MessageSwitch(AsArcGISTool,message)
		BoundaryRawPolyline=IntermedOutputFolder+TheFileName+"_boundarypolyline.shp"
		MgmtInterface.SplitLineAtPoints(RawPolyline,TheInPointFile,BoundaryRawPolyline,1)
	
		### Reconnect lines if separated at more than just corners (more than 4 lines): e.g. end of line fell in middle of boundary
		# Determine how many polyline features there are
		NumLines=MgmtInterface.CountRows(BoundaryRawPolyline)
		# Convert to feature layers
		MgmtInterface.CreateLayer(TheInPointFile,"Point_Layer")
		
		if NumLines>4:
			# Convert to feature layers
			MgmtInterface.CreateLayer(BoundaryRawPolyline,"Polyline_Layer")
			# Create new field in polyline to specify which lines to dissolve
			MgmtInterface.AddField("Polyline_Layer","Dissolve","SHORT","#","#","#")
			# Write fid to new field
			MgmtInterface.WriteField("Polyline_Layer","Dissolve", "[FID]","VB")
			
			# Select line on left side using points
			# Select left side points
			MgmtInterface.SelectUsingAttributes("Point_Layer","NEW_SELECTION","\"Id\" = 0 OR \"Id\" = 10")
			# Select lines which intersects left points
			MgmtInterface.SelectUsingLocation("Polyline_Layer","INTERSECT","Point_Layer",0,"NEW_SELECTION")
			# Select right side points
			MgmtInterface.SelectUsingAttributes("Point_Layer","NEW_SELECTION","\"Id\" = 1 OR \"Id\" = 11")
			# Deselect lines which intersect right side points
			MgmtInterface.SelectUsingLocation("Polyline_Layer","INTERSECT","Point_Layer",0,"REMOVE_FROM_SELECTION")
			
			# Check to see if more than 1 line - if so write to field for dissolve field calculation
			NumSelected=MgmtInterface.CountRows("Polyline_Layer")
			if NumSelected>1:
				# write consistent ID to Dissolve field
				MgmtInterface.WriteField("Polyline_Layer","Dissolve",5,"VB")		
			
			# Select lines which are on right side using points
			# Select right side points
			MgmtInterface.SelectUsingAttributes("Point_Layer","NEW_SELECTION","\"Id\" = 1 OR \"Id\" = 11")
			# Select lines which intersects right points		
			MgmtInterface.SelectUsingLocation("Polyline_Layer","INTERSECT","Point_Layer",0,"NEW_SELECTION")
			# Select left side points
			MgmtInterface.SelectUsingAttributes("Point_Layer","NEW_SELECTION","\"Id\" = 0 OR \"Id\" = 10")
			# Deselect lines which intersect left side points
			MgmtInterface.SelectUsingLocation("Polyline_Layer","INTERSECT","Point_Layer",0,"REMOVE_FROM_SELECTION")
			# check to see if more than 1 line - if so dissolve field calculation
			NumSelected=MgmtInterface.CountRows("Polyline_Layer")
			if NumSelected>1:
				# write consistent ID to Dissolve field
				MgmtInterface.WriteField("Polyline_Layer","Dissolve",6,"VB")
				
			# Unselect all
			MgmtInterface.SelectUsingAttributes("Polyline_Layer","CLEAR_SELECTION","#")
			# Name for merged boundary lines
			MergedBoundaries=IntermedOutputFolder+TheFileName+"_mergedpolyline.shp"
			# Run dissolve to combine any side lines (don't care if multipart)
			MgmtInterface.Dissolve("Polyline_Layer",MergedBoundaries,"Dissolve","#",
				               "MULTI_PART","DISSOLVE_Lines")
		else:
			MergedBoundaries=BoundaryRawPolyline
			
		### Identify side lines from merged shapefile
		# Convert to feature layer
		MgmtInterface.CreateLayer(MergedBoundaries,"Boundary_Layer")
	
		# Select line on left side using points
		# Select left side points
		MgmtInterface.SelectUsingAttributes("Point_Layer","NEW_SELECTION","\"Id\" = 0 OR \"Id\" = 10")
		# Select lines which intersects left points
		MgmtInterface.SelectUsingLocation("Boundary_Layer","INTERSECT","Point_Layer",0,"NEW_SELECTION")
		# Select right side points
		MgmtInterface.SelectUsingAttributes("Point_Layer","NEW_SELECTION","\"Id\" = 1 OR \"Id\" = 11")
		# Deselect lines which intersect right side points
		MgmtInterface.SelectUsingLocation("Boundary_Layer","INTERSECT","Point_Layer",0,"REMOVE_FROM_SELECTION")	
		# Get the FID of the left side line
		LeftLineFID=ShpProp.ListFromField("Boundary_Layer","FID")	
		
		# Select lines which are on right side using points
		# Select right side points
		MgmtInterface.SelectUsingAttributes("Point_Layer","NEW_SELECTION","\"Id\" = 1 OR \"Id\" = 11")
		# Select lines which intersects right points		
		MgmtInterface.SelectUsingLocation("Boundary_Layer","INTERSECT","Point_Layer",0,"NEW_SELECTION")
		# Select left side points
		MgmtInterface.SelectUsingAttributes("Point_Layer","NEW_SELECTION","\"Id\" = 0 OR \"Id\" = 10")
		# Deselect lines which intersect left side points
		MgmtInterface.SelectUsingLocation("Boundary_Layer","INTERSECT","Point_Layer",0,"REMOVE_FROM_SELECTION")
		# Get the FID of the right side line
		RightLineFID=ShpProp.ListFromField("Boundary_Layer","FID")
	
		### Select 2 side lines to new shapefile
		# Update user on process
		message="Extracting side lines from converted polyline..."
		MessageSwitch(AsArcGISTool,message)
		# Select 2 side lines
		SQLexp=("\"FID\" = "+format(LeftLineFID[0])+" OR \"FID\" = "+format(RightLineFID[0]))
		MgmtInterface.SelectUsingAttributes("Boundary_Layer","NEW_SELECTION",SQLexp)
		# Final side boundaries name
		FinalBoundaries=IntermedOutputFolder+TheFileName+"_finalsidepolylines.shp"
		# Copy side lines to new shapefile
		MgmtInterface.CopyFeatures("Boundary_Layer",FinalBoundaries)
		
		### Determine US end line midpoint coordinates for later use to check centerline orientation
		# Switch selection to the end lines
		MgmtInterface.SelectUsingAttributes("Boundary_Layer","SWITCH_SELECTION","")	
		# Select US side line by right US point (Point Id=11)
		MgmtInterface.SelectUsingAttributes("Point_Layer","NEW_SELECTION","\"Id\" = 11")
		MgmtInterface.SelectUsingLocation("Boundary_Layer","INTERSECT","Point_Layer",1,"SUBSET_SELECTION")
		# Get US end line FID
		USEndFID=ShpProp.ListFromField("Boundary_Layer","FID")
		# Get coordinates for the end line
		USEndLineCoords=ShpProp.Coordinates("Boundary_Layer")
		# Get rid of top list structure since there's only 1 feature
		USEndLineCoords=USEndLineCoords[0]
		# Separate the coordinates for the first and last points
		USEndLineStart=USEndLineCoords[0]
		USEndLineEnd=USEndLineCoords[-1]
		# Calculate midpoint xy coordinates for end line
		USEndLineMid=((USEndLineStart[0]+USEndLineEnd[0])/2,(USEndLineStart[1]+USEndLineEnd[1])/2)	
	
		### Convert boundary polylines to centerline
		# Update user on process
		message="Converting boundaries to centerline..."
		MessageSwitch(AsArcGISTool,message)
		# centerline name
		CenterlinePolyline=IntermedOutputFolder+TheFileName+"_centerlinepolyline.shp"
		CartInterface.Centerline(FinalBoundaries,CenterlinePolyline,MaxWidth*1.2,0)
		# Clean up attribute table
		MgmtInterface.DeleteField(CenterlinePolyline,"LnType")
		MgmtInterface.DeleteField(CenterlinePolyline,"LeftLn_FID")
		MgmtInterface.DeleteField(CenterlinePolyline,"RightLn_FI")
	
		### Check to see if any part of centerline is still on top of boundary line 
		### by looking for near to boundary
		AInterface.Near(CenterlinePolyline,FinalBoundaries,MaxWidth*.01,"NO_LOCATION","NO_ANGLE")
		# Look in added NEAR_FID field for anything other than -1 (-1 means not near)
		NearFID=ShpProp.ListFromField(CenterlinePolyline,"NEAR_FID")
		#Create empty list for FIDs
		OverlapFID=[]
		#create counter for row
		i=0
		for FID in NearFID:
			if FID <> -1:
				OverlapFID=OverlapFID+[i]
			i+=1	
		# if there is feature overlap between centerline and boundary, 
		#  tell user which features overlap and abort process
		if len(OverlapFID)>0:
			message="Aborting: Centerline features overlap boundary: FIDs: "+format(OverlapFID)
			MessageSwitch(message,AsArcGISTool)
			x=1/0
	
		# Clean up attribute table
		MgmtInterface.DeleteField(CenterlinePolyline,"NEAR_FID")
		MgmtInterface.DeleteField(CenterlinePolyline,"NEAR_DIST")	
	
		### Determine if centerline is oriented appropriately
		# Get centerline coordinates
		CenterlineCoords=ShpProp.Coordinates(CenterlinePolyline)
		# Get rid of top list structure since there's only 1 feature
		CenterlineCoords=CenterlineCoords[0]
		# Separate the coordinates for the end points
		CenterlineStartCoords=CenterlineCoords[0]
		CenterlineEndCoords=CenterlineCoords[-1]
		# Get distance between centerline start and us end line midpoint
		CenterlineStart2USEndlineMid=sqrt(
			(CenterlineStartCoords[0]-USEndLineMid[0])**2+
			(CenterlineStartCoords[1]-USEndLineMid[1])**2)
		# Get distance between centerline end and us end line midpoint
		CenterlineEnd2USEndlineMid=sqrt(
			(CenterlineStartCoords[0]-USEndLineMid[0])**2+
			(CenterlineStartCoords[1]-USEndLineMid[1])**2)	
		# Check to see which centerline end is closer to US end line
		if CenterlineStart2USEndlineMid < CenterlineEnd2USEndlineMid:
			FlipCenterline=0
		else:
			FlipCenterline=1
		
		return([CenterlinePolyline]+[FlipCenterline])

	#Print out error from Python
	except Exception, err: # an error occurred (probably in arcGIS)
		raise RuntimeError("** Error: Polygon2Centerline Failed ("+str(err)+")") #raise "grabs" error for use in higher level