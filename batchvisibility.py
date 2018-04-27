#Example script for a viewshed analysis model
#Andreas Zischg, 23.03.2018
#Seminar Geodata Analysis and Modelling, Spring Semester 2018
#the model writes the maximum distanz and the visible area to each observer point in a point shape file of peaks

#imports
import arcpy
import numpy
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension('Spatial')
else:
    print "no spatial analyst license available"


#**************************************************************************
#ENVIRONMENT variables - set workspace and names of input files
#**************************************************************************
#set environment and workspace
myworkspace = "D:/arcpy1/GIS"
tempdir="C:/temp"
print "Workspace: " + myworkspace
arcpy.env.workspace = myworkspace
arcpy.env.overwriteOutput = True
#input data observerpoints
observerpoints=myworkspace+"/"+"observer.shp"
#input data dhm
dhm=arcpy.Raster("D:/arcpy1/GIS/DHM25/dhm25")
arcpy.env.cellSize = dhm
arcpy.env.extent = dhm
arcpy.env.snapRaster = dhm

#**************************************************************************
#create a list of feature ID's in observer points
obs=tempdir+"/"+"obs.shp" #temporary file for selected single observer point 
eucdist=tempdir+"/"+"eucdist" #temporary file for the euclidian distance raster
viewshed=tempdir+"/"+"viewshed" #temporary file for the viewshed analysis
zonstat=tempdir+"/"+"zonstat.dbf" #temporary file for the zonal statistics table
#create a feature cursor that iterates through all features in the shapefile and reads the required attribute
cursor = arcpy.da.UpdateCursor(observerpoints, ["FID", "maxdist", "maxarea"]) #maxdist and maxarea are the target attributes to which the results should be written
#loop through all feature in observer shapefile
for row in cursor:
    id = row[0]
    print "processing FID: " + str(id)
    maxdist=0.0
    #prepare a string for the where clause for selecting the observer with FID
    where_clause = '"FID" = ' + str(id)
    #extract 1 observer point from all points
    arcpy.Select_analysis(observerpoints,obs, where_clause)
    #calculate euclidean distance to this observer point
    outeucdistance=arcpy.sa.EucDistance(obs)
    outeucdistance.save(eucdist)
    #calculate viewshed
    zFactor = 1
    useEarthCurvature= "CURVED_EARTH"
    refractivityCoefficient = 0.13
    outViewshed=arcpy.sa.Viewshed(dhm, obs, zFactor, useEarthCurvature, refractivityCoefficient)
    outViewshed.save(viewshed)
    #set invisible areas to null
    arcpy.gp.SetNull_sa(outViewshed, "1", tempdir+"/"+"visr", """"VALUE" = 0""")
    # calculate maximum length of sight
    arcpy.gp.ZonalStatisticsAsTable_sa(arcpy.Raster(tempdir+"/"+"visr"), "VALUE", outeucdistance, zonstat, "DATA", "MAXIMUM")
    #compute a zonal statistics: count number of cells in visible area and extract maximum eucl. distance in visible area
    zonstatfields=["AREA", "MAX"]
    zonstatarr=arcpy.da.TableToNumPyArray(zonstat, zonstatfields, skip_nulls=False)
    area=zonstatarr[0][0]
    maxdist = zonstatarr[0][1]
    #write the results back in the row of the feature cursor
    row[1]=maxdist
    row[2]=area
    #save the result
    cursor.updateRow(row)
print "done ..."
