#Example script for a simple rockfall model
#Andreas Zischg, 23.03.2018
#Seminar Geodata Analysis and Modelling, Spring Semseter 2018

#imports
import arcpy
import numpy
import math
import matplotlib.pyplot as plt
if arcpy.CheckExtension("Spatial") == "Available":
    arcpy.CheckOutExtension('Spatial')
else:
    print "no spatial analyst license available"

#**************************************************************************
#ENVIRONMENT variables - set workspace and names of input files
#**************************************************************************
#set environment and workspace
myworkspace = "D:/OneDrive/UNIBE/Lehre/GeodataAnalysisAndModelling/Arcpy1/GIS"
tempdir="C:/temp"
print "Workspace: " + myworkspace
arcpy.env.workspace = myworkspace
arcpy.env.overwriteOutput = True
demraster=arcpy.Raster(myworkspace+"/"+"clipdem.img")
referenceraster=demraster
arcpy.env.cellSize = referenceraster
arcpy.env.extent = referenceraster
arcpy.env.snapRaster = referenceraster
arcpy.env.Mask = referenceraster
arcpy.env.overwriteOutput = True
cellsize=referenceraster.meanCellWidth
lowerLeft = arcpy.Point(referenceraster.extent.XMin,referenceraster.extent.YMin)

#**************************************************************************
#create an array from the dem raster
demarr=arcpy.RasterToNumPyArray(demraster)
plt.imshow(demarr)
#import startpoint raster as numpy array. Input is a raster dataset with values = 1 for starting points of rockfall processes
startarr=arcpy.RasterToNumPyArray(arcpy.Raster(myworkspace+"/"+"startpoint.img"))

#Model Parameter (slope angle, parameter that determines stop condition of a rockfall process
pauschalgefaelle=0.58 #% = 30 grad

#compute flow direction
outFlowDirection = arcpy.sa.FlowDirection(demraster)
flowdirarray=arcpy.RasterToNumPyArray(outFlowDirection)
#outFlowDirection.save(tempdir+"/"+"flowdir.img")
plt.imshow(flowdirarray)

#create outarray for writing outraster
rows=int(numpy.shape(demarr)[0])
cols=int(numpy.shape(demarr)[1])
#create an array for output (with the same dimensions as dem array)
outarr=numpy.zeros((rows, cols), dtype=int)

i=0
j=0
count=0
#frist loop through all rows in array
while i <rows:
    j=0
    #second loop through all colums in row
    while j<cols:
        #check if cell is a staarting point of rockfall prrocess
        if startarr[i,j]==1:
            #read out the z-coordinate of starting point
            z0 = demarr[i, j]
            print "row: " + str(i) + "/" + "col: " + str(j)
            print "flowdirection: " + str(flowdirarray[i,j])
            print "z-coordinate: "+str(z0)
            print "rockfall starts ..."
            # start inner loop of rockfall trajectory
            #set initial conditions
            flowlength=0.0
            stopcondition = 0
            angle=0.0
            #x and y are the rows/column indices for the inner loop (trajectory modelling of a rockfall)
            x=i
            y=j
            #each pixel passed by the rockfall is set to value = 1
            outarr[i, j] += 1
            flowdir=flowdirarray[x,y]
            #check the next cell of the trajectory
            while x>=0 and x<rows and y>=0 and y<cols and stopcondition == 0:
                flowdir = flowdirarray[x, y]
                if flowdir==1:
                    y+=1
                    flowlength+=cellsize
                elif flowdir==2:
                    x+=1
                    y+=1
                    flowlength += cellsize * math.sqrt(2)
                elif flowdir==4:
                    x+=1
                    flowlength += cellsize
                elif flowdir==8:
                    x+=1
                    y-=1
                    flowlength += cellsize * math.sqrt(2)
                elif flowdir==16:
                    y-=1
                    flowlength += cellsize
                elif flowdir==32:
                    x-=1
                    y-=1
                    flowlength += cellsize * math.sqrt(2)
                elif flowdir==64:
                    x-=1
                    flowlength += cellsize
                elif flowdir==128:
                    x-=1
                    y+=1
                    flowlength += cellsize * math.sqrt(2)
                else:
                    stopcondition=1
                    break
                #z-coordinate of the actual cell
                z1=demarr[x,y]
                #compute condition for continuing/stopping the process
                if flowlength>0:
                    slope=(z0-z1)/flowlength
                else:
                    stopcondition=1
                if slope < pauschalgefaelle:
                    stopcondition = 1
                #write the trajectory to the output raster
                outarr[x,y]+=1
                #make a snapshot of the actual process
                plt.imsave(myworkspace+"/"+"step"+str(count)+".png", outarr)
                count+=1
        j+=1
    i+=1
#display results
plt.imshow(outarr)
#write the output to a raster file
outraster = arcpy.NumPyArrayToRaster(outarr, lowerLeft, cellsize)
outraster.save(myworkspace+"/"+"outtrajectory.img")
print "done ..."
