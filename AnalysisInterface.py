###################################################################################
# ArcGIS Interface Module for Analysis tools
# This module includes classes to interface with ArcGIS.
# The class provides insulation from ArcGIS changes and provides friendlier error
# messages.
# Original Author: Jim Graham
# Date: 4th of November, 2011
#
# Modified by Cara Walter
# Modified: 3/17/2013
# Most descriptions directly from arcpy documentation
###################################################################################
import arcpy # import ArcGIS Python bindings
###################################################################################
# Class to interface with analysis
###################################################################################
class AnalysisInterface: # class to interface with analysis tools

	###################################################################################
	# Constructor for the management interface class
	###################################################################################
	def __init__(self): # called when the class is created
		# Set environment to allow file overwrite
		arcpy.env.overwriteOutput=True

	###################################################################################
	# Creates buffer polygons around input features to a specified distance. An
	#   optional dissolve can be performed to combine overlapping buffers.
	# Inputs: 
	#         TheInShp: name and path of the input shapefile
	#         TheOutShp: name and path of the output shapefile
	#         BufferDist: numeric value for distance to extend buffer
	#         LineSide: (String): The side(s) of the input features that will be buffered. e.g. "FULL", "LEFT",...
	#         LineEndType: (String): The shape of the buffer at the end of line input features. - not valid for polygon inputs. "ROUND", "FLAT"
	#         Dissolve: Specifies the dissolve to be performed to remove output buffer overlap. "NONE", "ALL"
	#         DissolveField: The list of field(s) from the input features on which to dissolve the output buffers.
	###################################################################################
	def Buffer(self,TheInShp,TheOutShp,BufferDist,LineSide,LineEndType,Dissolve,DissolveField): 
		try:
			arcpy.analysis.Buffer(TheInShp,TheOutShp,BufferDist,LineSide,LineEndType,Dissolve,DissolveField)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Buffer Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Extracts input features that overlay the clip features.
	#   optional dissolve can be performed to combine overlapping buffers.
	# Inputs: 
	#         TheInShp: name and path of the input features
	#         TheClipShp: name and path of clipping features
	#         TheOutShp: name and path of the output shapefile
	#         ClusterTolerance: The minimum distance separating all feature coordinates (nodes and vertices) as
	#          well as the distance a coordinate can move in X or Y (or both).
	###################################################################################
	def Clip(self,TheInShp,TheClipShp,TheOutShp,ClusterTolerance): 
		try:
			arcpy.analysis.Clip(TheInShp,TheClipShp,TheOutShp,ClusterTolerance)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Clip Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Creates a feature class by overlaying the Input Features with the polygons of
	#  the Erase Features. Only those portions of the input features falling outside
	#  the erase features outside boundaries are copied to the output feature class.
	# Inputs: 
	#         TheInShp: name and path of the input features
	#         TheEraseShp: name and path of erasing features
	#         TheOutShp: name and path of the output shapefile
	#         ClusterTolerance: The minimum distance separating all feature coordinates (nodes and vertices) as
	#          well as the distance a coordinate can move in X or Y (or both).
	###################################################################################
	def Erase(self,TheInShp,TheEraseShp,TheOutShp,ClusterTolerance): 
		try:
			arcpy.analysis.Erase(TheInShp,TheEraseShp,TheOutShp,ClusterTolerance)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Erase Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Computes a geometric intersection of the input features and identity features.
	#  The input features or portions thereof that overlap identity features will get
	#  the attributes of those identity features.
	# Inputs: 
	#         TheInShp: name and path of the input features
	#         TheIDShp: name and path of identifying features. Must be polygons or the same geometry type
	#          as the Input Features.
	#         TheOutShp: name and path of the output shapefile
	#         JoinAttr {string}: Determines what attributes will be transferred to the Output Feature Class: "ALL","NO_FID","ONLY_FID"
	#         ClusterTolerance: The minimum distance separating all feature coordinates (nodes and vertices) as
	#          well as the distance a coordinate can move in X or Y (or both).
	#         Rel: Choose if you want additional spatial relationships between the Input Features
	#           and Identity Features to be written to the output. This only applies when the
	#           Input Features are lines and the Identity Features are polygons: "NO_RELATIONSHIPS","KEEP_RELATIONSHIPS"
	###################################################################################
	def Identity(self,TheInShp,TheIDShp,TheOutShp,JoinAttr,ClusterTolerance,Rel): 
		try:
			arcpy.analysis.Identity(TheInShp,TheIDShp,TheOutShp,JoinAttr,ClusterTolerance,Rel)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Identity Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Determines the total number of rows for a feature class, table, layer, or raster.
	# Inputs: 
	#         TheInShp: name and path of the input shapefile
	#         TheNearShp: name and path of the near shapefile
	#         SearchRadius: number for distance to look for near shapefile feature from input feature
	#         Location: Specifies whether x and y coordinates of the nearest location of the near
	#                   feature will be written to new fields NEAR_X and NEAR_Y respectively: "NO_LOCATION", "LOCATION"
	#         Angle: Specifies whether the near angle values in decimal degrees will be calculated
	#                and written to a new field, NEAR_ANGLE: "NO_ANGLE", "ANGLE"
	###################################################################################
	def Near(self,TheInShp,TheNearShp,SearchRadius,Location,Angle): 
		try:
			arcpy.analysis.Near(TheInShp,TheNearShp,SearchRadius,Location,Angle)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Near Failed ("+str(err)+")") #raise "grabs" error for use in higher level

	###################################################################################
	# Creates a feature class by overlaying the Input Features with the polygons of
	#  the Erase Features. Only those portions of the input features falling outside
	#  the erase features outside boundaries are copied to the output feature class.
	# Inputs: 
	#         TheInShp (Value Table): A list of the input feature classes or layers. When the distance between
	#          features is less than the cluster tolerance, the features with the lower rank
	#          will snap to the feature with the higher rank. The highest rank is one. All of
        #          the input features must be polygons.
	#         TheOutShp {string}: name and path of the output shapefile
	#         JoinAttr {string}: Determines what attributes will be transferred to the Output Feature Class: "ALL","NO_FID","ONLY_FID"
	#         ClusterTolerance {Linear unit}: The minimum distance separating all feature coordinates (nodes and vertices) as
	#          well as the distance a coordinate can move in X or Y (or both).
	#         Gaps {Boolean}: Gaps are areas in the output feature class that are completely enclosed by other
        #          polygons. This is not invalid, but it may be desirable to identify these for
        #          analysis. To find the gaps in the output, set this option to NO_GAPS, and a
        #          feature will be created in these areas. To select these features, query the
        #          output feature class based on all the input feature's FID values being equal to -1.
	###################################################################################
	def Union(self,TheInShp,TheOutShp,JoinAttr,ClusterTolerance,Gaps): 
		try:
			arcpy.analysis.Union(TheInShp,TheOutShp,JoinAttr,ClusterTolerance,Gaps)
		except Exception, err: # an error occurred (probably in arcGIS)
			raise RuntimeError("** Error: Union Failed ("+str(err)+")") #raise "grabs" error for use in higher level

