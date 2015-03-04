# Functions to deal with messaging

''' Function to switch messaging between command line and ArcGIS dialog
    Input: 
	  AsGISTool: 0 if operating in command line, 1 if using as ArcGIS tool
	  Message: string for output to command line or ArcGIS dialog'''
def MessageSwitch(AsGISTool,Message):
	try:
		if AsGISTool==0:
			print(Message)
		else:
			from arcpy import AddMessage
			AddMessage("**"+Message+"**")
	except Exception, err:
		raise RuntimeError("** Error: MessageSwitch Failed ("+str(err)+")") 

