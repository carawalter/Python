#######################################################################
# SplitLineModule
#
# Purpose: Split line at points spaced at regular intervals
#   
# Created by: Cara Walter
#
# Includes code modified from OSU GEO 599: https://dl.dropbox.com/u/37858409/Geo599_GIS_Programming/index.html
#                              http://stackoverflow.com/questions/3579568/choosing-a-file-in-python-simple-gui
#
# Input: 
#        TheInFile: the name of a polyline feature class with 1 continuous line (as long as line is continuous, tool will run)
#        TheOutFilePath: the path of the folder to put the output shapefiles in
#        SplitLength: number specifying interval at which to split input line
#        AsArcGISTool: binary specifying if running as a GIS tool (1) or not (0) to control messaging
#        FlipLine: binary specifying whether the start of the centerline aligns with the desired start (0), and it actually the end (1)
#
# Outputs (name same as input shapefile with suffix): 
#        _single.shp (PolylineSingle): shapefile with polylines merged if input had more than one polyline
#        _random_points.shp (PointName): points along input polyline at specified spacing
#        _copy_points.shp (PointNameCopy): two sets of points along input polyline at specified spacing
#        _segmented_line.shp (LineSegmented): the output split polylines
#
# Returns: _segmented_line.shp (LineSegmented): the output split polylines path and name - contains "Station" field with distance from line start
#
# Process:
#         1) Check to see if polyline contains single, continous feature - try to fix if not
#         2) Create evenly spaced points along the line
#         2) Duplicate the points and append original points to duplicate points shapefile to create 
#            start and end points for each line segment 
#         3) Use points to line tool to create segmented line (use CID field as unique line identifier)
#         4) Add distance from start to attribute table in "Station" field
#
#         arcpy.management.SplitLineAtPoint supposedly does some of this, but it is unreliable for lots of splits
#
# Modified: 3/18/2013
#######################################################################
def SplitLine(TheInFile,TheOutFilePath,SplitLength,AsArcGISTool,FlipLine):
	try:
		import os
		import ManagementInterface as MgmtGIS
		import ShapefileProperties as ShpProp
		from MessagingModule import MessageSwitch

		'''Setup classes and file output'''
		#Create instance of management class
		MgmtInterface=MgmtGIS.ManagementInterface() 
			
		# Extract just the file name
		TheFileName=os.path.basename(TheInFile)		
		
		# check to see if out folder exists, if not create it
		if os.path.isdir(TheOutFilePath)!= True:        
			os.mkdir(TheOutFilePath)	
	
		'''Check to see if more than 1 feature, try to combine as 1 continuous, 
		   if that fails abort'''
		# Determine how many input line features there are
	
		NumFeatures=MgmtInterface.CountRows(TheInFile)
		#Merge input line into 1 feature if multiple features or 
		# rename previous variable to match new name
		if NumFeatures>1:
			PolylineSingle=TheOutFilePath+TheFileName[0:-4]+"_single.shp"
			# Merge lines only if they will be single part and therefore continuous
			MgmtInterface.Dissolve(TheInFile,PolylineSingle,"#","#",
			                       "SINGLE_PART","UNSPLIT_LINES")
		else:
			PolylineSingle=TheInFile
	
		# Count features again to make sure input line is continuous
		NumFeaturesSingle=MgmtInterface.CountRows(PolylineSingle)
		
		# Create error to exit out if input line still more than 1 feature
		if NumFeaturesSingle>1:
			message="Error: Input line is more than 1 feature and not continuous"
			MessageSwitch(message,AsArcGISTool)
			x=1/0
	
		'''Create evenly spaced points along input polyline at SplitLength distance'''
		# Update user on process
		message="Creating evenly spaced points along\n "+TheFileName+" \nat "+ format(SplitLength) +" interval..."
		MessageSwitch(AsArcGISTool,message)	
			
		#Determine input line length
		LineLength=ShpProp.Length(PolylineSingle)
	
		# Determine number of points from line split lengths
		PointNumber=(int(int(LineLength[0]+1)/SplitLength))
		# Output point shapefile name
		PointName=TheFileName[0:-4]+"_random_points.shp"
		# Use split length and number of point to constrain point creation along input line
		MgmtInterface.RandomPts(
			TheOutFilePath,PointName,PolylineSingle,"",PointNumber,SplitLength,"POINT","")
		
		''' Setting up for Point to Line tool:
		 need 2 points per line and a field to base line creation on - 
		 using CID with original points FID as unique line identifier'''
		# Update user on process
		message="Creating duplicate points as end points for segmented lines..."
		MessageSwitch(AsArcGISTool,message)	
			
		#Write FID values to CID field as identifier for line segments
		if FlipLine==0:
			# Centerline start is at desired output line start
			MgmtInterface.WriteField(TheOutFilePath+PointName,"CID","[FID]","VB")
		else:
			# Centerline start is at end of desired output line
			MgmtInterface.WriteField(TheOutFilePath+PointName,"CID",
			                         format(PointNumber-1)+"-[FID]","VB")
		
		# Select all but the first point and copy to new shapefile - 
		#   duplicate points will be end points for each line segment
		# Create feature layer
		MgmtInterface.CreateLayer(TheOutFilePath+PointName,"Point_layer")
		# Define selection
		SQLstatement="\"CID\" <> 0"
		#Run select tool to a get new selection of all points with a CID not equal to 0
		MgmtInterface.SelectUsingAttributes("Point_layer","NEW_SELECTION",SQLstatement)
		#Output shapefile name
		PointNameCopy=TheOutFilePath+TheFileName[0:-4]+"_copy_points.shp"
		#Run copy tool through class
		MgmtInterface.CopyFeatures("Point_layer",PointNameCopy)
	
		#Subtract 1 from CID value to treat duplicate points as "end" for each segment
		MgmtInterface.WriteField(PointNameCopy,"CID","[CID] - 1","VB") 
		
		'''Combine original and duplicate points to create new lines'''
		# Update user on process
		message="Combining original and duplicate points..."
		MessageSwitch(AsArcGISTool,message)
			
		# Append original points to copy except for last point 
		#  (don't need 2 last points as do not need 1 to be start point)
		# Run select tool through class to exclude last point
		SQLstatement2="\"CID\" <> "+format(PointNumber-1)
		MgmtInterface.SelectUsingAttributes("Point_layer","NEW_SELECTION",SQLstatement2)
		# append original to copy
		MgmtInterface.Append("Point_layer",PointNameCopy)
		
		'''Create line segments from points and add station (distance from start) 
		to attribute table'''
		# Update user on process
		message="Creating line segments from points..."
		MessageSwitch(AsArcGISTool,message)		
		
		#Split line name
		LineSegmented=TheOutFilePath+TheFileName[0:-4]+"_segmented_line.shp"
	
		# Create segmented line from points using CID as line identifier
		MgmtInterface.Points2Line(PointNameCopy,LineSegmented,"CID","#")
		
		# Add stationing to attribute table
		MgmtInterface.AddField(LineSegmented,"Station","DOUBLE",10,2,"#")
		MgmtInterface.WriteField(LineSegmented,"Station","!shape.length! * !CID!","PYTHON")
	
		# Clean up feature layer
		MgmtInterface.Delete("Point_layer")
		
		# Update user on process
		message="Split Line completed."
		MessageSwitch(AsArcGISTool,message)			
		
		return(LineSegmented)
	
	#Print out error from Python
	except Exception as TheError:
		raise RuntimeError("An error has occurred: "+format(TheError))