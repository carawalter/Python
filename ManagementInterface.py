###################################################################################
# ArcGIS Interface Module for management tools
# This module includes classes to interface with ArcGIS.
# The class provides insulation from ArcGIS changes and provides friendlier error
# messages.
# Original Author: Jim Graham
# Date: 4th of November, 2011
#
# Modified by Cara Walter
# Modified: 2/23/2013
# Most descriptions directly from arcpy documentation
###################################################################################
import arcpy # import ArcGIS Python bindings
###################################################################################
# Class to interface with data management
###################################################################################
class ManagementInterface: # class to interface with data management tools

	###################################################################################
	# Constructor for the management interface class
	###################################################################################
	def __init__(self): # called when the class is created
		# Set environment to allow file overwrite
		arcpy.env.overwriteOutput=True

	###################################################################################
	# Add a field to a shapefile attribute table
	# Inputs: 
	#         InShapefile - polyline shapefile with parallel lines
	#         FieldName - Field name string
	#         FieldType - Field type string: e.g. "TEXT", "DOUBLE", "FLOAT", "LONG"
	#         FieldDigits - integer for number of digits to store in field
	#         FieldDecimal - integer for number of decimal places for field
	#         FieldLength - integer for length of field if text or blob
	###################################################################################
	def AddField(self,InputShapefile,FieldName,FieldType,FieldDigits,FieldDecimal,FieldLength): # add a field to a attribute table
		try:
			# Create a list of the field names
			TheFieldNames = [f.name for f in arcpy.ListFields(InputShapefile)]
			# Check to see if field already exists
			for Item in TheFieldNames:
				if FieldName==Item:
					raise RuntimeError(FieldName+" already exists.")			

			#Call function depending on the type of field
			if FieldType==('TEXT' or 'BLOB'):
				arcpy.management.AddField(InputShapefile,FieldName,FieldType,
				                          "#","#",FieldLength)
			elif FieldType==('LONG' or 'SHORT'):
				arcpy.management.AddField(InputShapefile,FieldName,FieldType,FieldDigits)
			elif FieldType==('DATE' or 'RASTER' or 'GUID'):
				arcpy.management.AddField(InputShapefile,FieldName,FieldType)				
			else:
				arcpy.management.AddField(InputShapefile,FieldName,FieldType,
				                          FieldDigits,FieldDecimal)				

		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: AddField Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Appends multiple input datasets into an existing target dataset.
	# Inputs: 
	#         InShapefile - Shapefile name as a string
	#         TargetShapefile - destination shapefile path and name as a string
	###################################################################################
	def Append(self,InShapefile,TargetShapefile): # convert polygon to polyline 
		try:
			arcpy.management.Append(InShapefile,TargetShapefile)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Append Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Converts polygon boundaries to lines, or splitting line, polygon, or both features at their intersections.
	# Inputs: 
	#         InShapefile - shapefile path and name to be converted
	#         OutLayer - string for layer name
	###################################################################################
	def CreateLayer(self,InShapefile,OutLayer): # create feature layer from feature class 
		try:
			arcpy.management.MakeFeatureLayer(InShapefile,OutLayer)	
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: CreateLayer Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Copies features from the input feature class or layer to a new feature class.
	# Inputs: 
	#         InLayer - Layer name as a string
	#         OutShapefile - copied shapefile path and name as a string
	###################################################################################
	def CopyFeatures(self,InLayer,OutShapefile): # convert polygon to polyline 
		try:
			arcpy.management.CopyFeatures(InLayer,OutShapefile)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: CopyFeatures Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Determines the total number of rows for a feature class, table, layer, or raster.
	# Inputs: 
	#         TheTable: the string for the name and path of a feature class, table, layer, or raster
	# Output: 
	#         TheCount: an integer for the number of rows
	###################################################################################
	def CountRows(self,TheTable): # count rows 
		try:
			#As is returns arcobject, therefore need int, and getOutput(0)
			TheCount=int(arcpy.management.GetCount(TheTable).getOutput(0))
			return(TheCount)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: CountRows Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Permanently deletes data from disk
	# Inputs: 
	#         InData - Data element name as a string
	###################################################################################
	def Delete(self,InData):
		try:
			arcpy.management.Delete(InData)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Delete Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Deletes a field from a table
	# Inputs: 
	#         InTable - table path and name to be manipulated
	#         DropField - string for field name to be deleted
	###################################################################################
	def DeleteField(self,InTable,DropField): # create feature layer from feature class 
		try:
			arcpy.management.DeleteField(InTable,DropField)	
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: DeleteField Failed ("+str(err)+")") #raise "grabs" error for use in higher level


	###################################################################################
	# Aggregates features based on specified attributes.
	# Inputs:
	#         InShapefile - shapefile path and name to be merged
	#         OutShapefile - merged polyline shapefile path and name
	#         DissolveField - The field or fields on which to aggregate features.
	#         StatsField - The fields and statistics with which to summarize attributes: e.g. "FIRST"
	#         Multi - Specifies whether multipart features are allowed in the output feature class: "MULTI_PART", "SINGLE_PART"
	#         Unsplit - Controls how line features are dissolved: "DISSOLVE_LINES": single feature,
	#                    "UNSPLIT_LINES": single feature only when lines share a vertex
	###################################################################################
	def Dissolve(self,InShapefile,OutShapefile,DissolveField,StatsField,Multi,Unsplit): # merge polylines
		try:		
			arcpy.management.Dissolve(InShapefile,OutShapefile,DissolveField,StatsField,Multi,Unsplit)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Dissolve Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Merge together multiple shapefiles into one
	# Inputs: 
	#         InShapefiles - shapefile names as a list - or separted by semi-colons
	#         OutShapefile - output shapefile path and name as a string
	###################################################################################
	def MergeShapefiles(self,InShapefiles,OutShapefile): 
		try:
			arcpy.management.Merge(InShapefiles,OutShapefile,"#")
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: MergeShapefiles Failed ("+str(err)+")") #raise "grabs" error for use in higher level


	###################################################################################
	# Creates a feature class containing singlepart features generated by separating
	#  multipart input features.
	# Inputs: 
	#         InShapefiles - input shapefile path and name as a string
	#         OutShapefile - output shapefile path and name as a string
	###################################################################################
	def Multipart2Single(self,InShapefiles,OutShapefile): 
		try:
			arcpy.management.MultipartToSinglepart(InShapefiles,OutShapefile)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: MergeShapefiles Failed ("+str(err)+")") #raise "grabs" error for use in higher level




	###################################################################################
	# Creates lines from points according to a field and sorts according to a field
	# Inputs: 
	#         InShapefile - Shapefile name as a string
	#         LineField - string of field name to define lines by
	#         SortField - string of field name to sort lines by
	#         OutShapefile - output shapefile path and name as a string
	###################################################################################
	def Points2Line(self,InShapefile,OutShapefile,LineField,SortField): # convert polygon to polyline 
		try:
			arcpy.management.PointsToLine(InShapefile,OutShapefile,LineField,SortField)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Points2Line Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Converts polygon boundaries to lines, or splitting line, polygon, or both features at their intersections.
	# Inputs: 
	#         InShapefile - shapefile path and name to be converted
	#         OutShapefile - polyline shapefile path and name
	#         MinDistance - The minimum distance separating all feature coordinates as an integer
	#         Attributes - Specifies whether to preserve or omit the input attributes in the output feature class.
	###################################################################################
	def Polygon2Polyline(self,InShapefile,OutShapefile,MinDistance,Attributes): # convert polygon to polyline 
		try:
			arcpy.management.FeatureToLine(InShapefile,OutShapefile,MinDistance,Attributes)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Polygon2Polyline Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Projects a shapefile from one coordinate system to another
	# Inputs: 
	#         InShapefile - shapefile path and name to be converted
	#         OutShapefile - polyline shapefile path and name
	#         OutCoordinateSys - name of output projection as a string
	#         TransMethod - Transformation method as a string
	###################################################################################
	def ProjectShapefile(self,InShapefile,OutShapefile,OutCoordinateSys,TransMethod): 
		try:
			arcpy.management.Project(InShapefile,OutShapefile,OutCoordinateSys,TransMethod)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: ProjectFile Failed ("+str(err)+")") #raise "grabs" error for use in higher level


	###################################################################################
	# Creates random points along a guide shapefile or within extent
	# Inputs: 
	#         TheFilePath - folder to put output shapefile in
	#         OutPoints - name of output point shapefile
	#         InPolyline - polyline shapefile path and name for "guide" (can be "" if using extent)
	#         Extent - extent to use to constain points (can be "" if using shapefile)
	#         PointNumber - number of points to create or field used to create
	#         PointSpacing - minimum allowed spacing between points
	#         Multi - multipart or single part feature: "POINT" (default), or "MULTIPOINT"
	#         MultiSize - number of points in each multipoint
	###################################################################################
	def RandomPts(self,TheFilePath,OutPoints,InPolyline,Extent,PointNumber,PointSpacing,Multi,MultiSize): # create guided random points 
		try:
			arcpy.management.CreateRandomPoints(TheFilePath,OutPoints,
			                                    InPolyline,Extent,PointNumber,PointSpacing,Multi,MultiSize)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: RandomPts Failed ("+str(err)+")") #raise "grabs" error for use in higher level


	###################################################################################
	# Extacts the properties for a raster
	# Inputs: 
	#         InRaster - raster path and name as a string
	#         InParameters - string or list of desired properties as strings
	# Outputs:        
	#         OutValues - string or list of values for properties as strings
	###################################################################################
	def RasterProp(self,InRaster,InParameters): 
		try:
			if isinstance(InParameters,str):
				#Get the geoprocessing result object
				PropertyObject=arcpy.management.GetRasterProperties(InRaster,InParameters)
				#Get the value from geoprocessing result object
				OutValues=PropertyObject.getOutput(0)				
			else:
				OutValues=[]
				for Parameter in InParameters:
					#Get the geoprocessing result object
					PropertyObject=arcpy.management.GetRasterProperties(InRaster,Parameter)
					#Get the value from geoprocessing result object
					OutValues=OutValues+[PropertyObject.getOutput(0)]				
			return(OutValues)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: RasterProp Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Adds, updates, or removes a selection on a layer or table view based on an attribute query.
	# Inputs: 
	#         InLayer - Layer name as a string
	#         Type - type of selection as string: e.g. "NEW_SELECTION", "ADD_TO_SELECTION"
	#         SQLexp - SQL statement used to select a subset of records.
	###################################################################################
	def SelectUsingAttributes(self,InLayer,Type,SQLexp):  
		try:
			arcpy.management.SelectLayerByAttribute(InLayer,Type,SQLexp)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: SelectUsingAttribute Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Adds, updates, or removes a selection on a layer or table view based on an attribute query.
	# Inputs: 
	#         InLayer - Layer name as a string
	#         Relationship - The spatial relationship to be evaluated. ("INTERSECT" is default)
	#         SelectFeatures - The features in the Input Feature Layer will be selected based on their relationship 
	#            to the features from this layer or feature class.
	#         Distance - value for how far away to look
	#         Type - type of selection as string: e.g. "NEW_SELECTION", "ADD_TO_SELECTION"
	###################################################################################
	def SelectUsingLocation(self,InLayer,Relationship,SelectFeatures,Distance,Type):
		try:
			arcpy.management.SelectLayerByLocation(InLayer,Relationship,SelectFeatures,Distance,Type)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: SelectUsingAttribute Failed ("+str(err)+")") #raise "grabs" error for use in higher level	

	###################################################################################
	# Split a line at points
	# Inputs: 
	#        InLine: Input polyline Shapefile
	#        InPoints: Input point shapefile to split at
	#        OutShapefile: name of output shapefile
	#        Radius: Number used to split lines by their proximity to point features.
	###################################################################################
	def SplitLineAtPoints(self,InLine,InPoints,OutShapefile,Radius):
		try:
			arcpy.management.SplitLineAtPoint(InLine,InPoints,OutShapefile,Radius)

		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: SplitLineAtPoints Failed ("+str(err)+")") #raise "grabs" error for use in higher level		

	###################################################################################
	# Converts feature vertices to points
	# Inputs: 
	#         InShapefile - shapefile path and name to be converted
	#         OutShapefile - point shapefile path and name
	#         WhichVertices - species which vertices to create points at: e.g. "ALL", "MID", "START", "END", "BOTH_ENDS"...
	###################################################################################
	def Vertices2Points(self,InShapefile,OutShapefile,WhichVertices): # convert polygon to polyline 
		try:
			arcpy.management.FeatureVerticesToPoints(InShapefile,OutShapefile,WhichVertices)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Vertices2Points Failed ("+str(err)+")") #raise "grabs" error for use in higher level


	###################################################################################
	# Write to a field in a shapefile attribute table
	# Inputs: 
	#        InShapefile: Input Shapefile
	#        FieldName: Field name string
	#        Statement: string expression for entering into field
	#        StatementType: Code base for the expression "VB", "PYTHON"
	###################################################################################
	def WriteField(self,InShapefile,FieldName,Statement,StatementType): # write to a field in a attribute table
		try:
			arcpy.management.CalculateField(InShapefile,FieldName,Statement,StatementType)			

		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: WriteField Failed ("+str(err)+")") #raise "grabs" error for use in higher level		








