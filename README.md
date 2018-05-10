# class exercices arcpy

This is a class exercise of the Seminar Geodata Analysis and Modelling, Spring Semester 2018, University of Bern

By Andreas Zischg, Pascal Horton and Jorge Ramirez

## What's in there ##

This repository contains two scripts:
* a simple rockfall model
* an example for batch-processing viewshed analyses and for combining raster data and vector data

## How to use the models ##
The rockfall model can be used with any digital terrain model. It needs a raster with the same size of the DEM raster having values = 1 for all starting points of rockfall processes

The viewshed analysis model requires a shapefile (observer.shp) with the observer points (must have the following colums in the attribute table: "maxdist, "maxarea"), and a digital elevation raster (DEM)
