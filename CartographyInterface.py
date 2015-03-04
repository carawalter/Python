###################################################################################
# ArcGIS Interface Module for cartography tools
# This module includes classes to interface with ArcGIS.
# The class provides insulation from ArcGIS changes and provides friendlier error
# messages.
# Original Author: Jim Graham
# Date: 4th of November, 2011
#
# Modified by Cara Walter
# Modified: 2/23/2013
###################################################################################
import arcpy # import ArcGIS Python bindings
###################################################################################
# Class to interface with cartography
###################################################################################
class CartographyInterface: # class to interface with cartography tools

	###################################################################################
	# Constructor for the cartography interface class
	###################################################################################
	def __init__(self): # called when the class is created
		# Set environment to allow file overwrite
		arcpy.env.overwriteOutput=True  		
	###################################################################################
	# Converts 2 "parallel" lines to a single line in between
	# Inputs: 
	#         InPolyline - polyline shapefile with parallel lines
	#         OutPolyline - centerline polyline shapefile
	#         MaxWidth - float value for the maximum space between lines to collapse
	#         MinWidth - float value for the minimum space between lines to collapse
	###################################################################################
	def Centerline(self,InPolyline,OutPolyline,MaxWidth,MinWidth): # parallel lines to centerline
		try:
			arcpy.cartography.CollapseDualLinesToCenterline(InPolyline,OutPolyline,MaxWidth,MinWidth)
		
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Centerline Failed ("+str(err)+")") #raise "grabs" error for use in higher level	

	###################################################################################
	# Performs a line simplification
	# Inputs: 
	#         InPolyline - polyline shapefile path and name to be simplified
	#         OutPolyline - simplified polyline shapefile path and name
	#         Method - type of simplification: "BEND_SIMPLIFY" or "POINT_REMOVE"
	#         Tolerance - The tolerance that determines the degree of simplification, integer
	###################################################################################
	def SimpleLine(self,InPolyline,OutPolyline,Method,Tolerance): # simplify a polyline shapefile
		try:
			# Simplify line with no error checking
			arcpy.cartography.SimplifyLine(InPolyline,OutPolyline,Method,Tolerance,"#","#","NO_CHECK")
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: SimplifyLine Failed ("+str(err)+")") #raise "grabs" error for use in higher level
		
	###################################################################################
	# Performs a line smoothing
	# Inputs: 
	#         InPolyline - polyline shapefile path and name to be smoothed
	#         OutPolyline - smoothed polyline shapefile path and name
	#         Method - type of simplification: "PAEK" "BEZIER_INTERPOLATION"
	#         Tolerance - The tolerance that determines the degree of smoothing, integer
	#         Endpoint - Specifies whether to preserve the endpoints for closed lines. This option works
        #                    with the PAEK algorithm only: "FIXED_CLOSED_ENDPOINT", "NO_FIXED"
	#         ErrorOpt - Specifies how the topological errors (possibly introduced in the process, such
        #                    as line crossing) will be handled:"NO_CHECK", "FLAG_ERRORS"
	###################################################################################
	def SmoothLine(self,InPolyline,OutPolyline,Method,Tolerance,Endpoint,ErrorOpt): 
		try:
			# Smooth line
			if Method=="BEZIER_INTERPOLATION":
				Tolerance=0
				Endpoint="#"
			arcpy.cartography.SmoothLine(InPolyline,OutPolyline,Method,Tolerance,Endpoint,ErrorOpt)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: SmoothLine Failed ("+str(err)+")") #raise "grabs" error for use in higher level
				
