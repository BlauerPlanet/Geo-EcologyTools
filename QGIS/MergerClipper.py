#--- Description ---
# This script takes all visible (on QGIS MapCanvas) RasterLayers (e.g. DEMs) and merges them 
# and then clips them based on one selected (inside QGIS via LayerSelectionTool) feature of a MultiPolygon Vector Layer (e.g. areas of solar parks).
# The name of the Group/subgroup the layer is inside is used as layername for the merged layer. For the clipped Layer the value of a specific field for the selected feature is used as filename.
# It is tested with QGIS 3.44.9 (installed via mamba/conda-forge) and uses the Python Console inside QGIS.

#!!! IMPORTANT !!!
#! Only the raster layers (e.g. DEM) for the specific location need to be visible in canvas
#! Only the Feature (!SINGULAR) from the clipping layer with the location corresponding to the raster Layers need to be selected
#! Script needs an active QGIS GUI and be loaded inside QGIS Python Console (therefore no imports of packages needed)
#! Paths are coded with formattet string and slash symbol (e.g. f"{merge_path}/{filename_merge})
#! set the necessary variable BEFORE running the script for the first time:
merge_path = "..." # str to set the path where the merged raster should be saved (without filename.tif and without last /)
clip_path = "..." # str to set the path where the clipped raster should be saved (without filename.tif and without last /)
mask_layer = "..." # str to set the layername of the clipping mask (e.g. "clip.gpkg") !GPKG containing only one layer
field = "..." # str to set the field of the cliupping layer containing the information for the filename of the clipped Layer (e.g. "Name")


#docs: https://docs.qgis.org/3.44/en/docs/pyqgis_developer_cookbook/cheat_sheet.html#canvas
layers2merge = []  # list containing all layers that need to be merged together

# get visible layers on canvas since I am in QGIS GUI
canvas = iface.mapCanvas()
visible_layers = canvas.layers()

#get also layer tree in order to properly navigate structure (could be used to get the name when no iface possible)
root = QgsProject.instance().layerTreeRoot()

for layer in visible_layers:
    layersource=layer.source()
    layername=layer.name()
    if ((layersource.endswith('.tif') or layersource.endswith('.xyz')) and "Merged" not in layername): #DEM layers expected as .tif and .xyz; also account for the temp layer after Merging when a test is performed with teh GUI for gdal:merge
        print(f"Added {layername} to merge-list")
        layers2merge.append(layer)
        layer_node = root.findLayer(layer.id()) 
        
        # traverse the Layer Tree; expects all layers to merge be in the same Group and Group level
        groups = []                                 # will hold all the group names for this iteration "bottom‑up" from the current layer
        parent = layer_node.parent()                     
        while parent and parent != root:
            if isinstance(parent, QgsLayerTreeGroup):
                groups.append(parent.name())
            parent = parent.parent()
        #full_path = "/".join(reversed(groups))     
        filename_merge=groups[0] #since the group nearest to layer is the first in the list use this (as part of) the actual filename

# set parameters for the qgis Process gdal:merge
params_merge={
    'INPUT' : layers2merge,
    'SEPARATE' : False,
    'DATA_TYPE' : 6, # set to Float64
    'OUTPUT' : f"{merge_path}/{filename_merge}.tif"
}

result=processing.run("gdal:merge", params_merge) # run the process
merged_raster = QgsRasterLayer(result['OUTPUT']) # load the layer as QgsRasterLayer

#account for the situations where the CRS is not automatically detected and set by QGIS -> default is assumed to be EPSG:25832 (default from Data related to the German Open Government GeoData)
merged_crs = merged_raster.crs()

if not merged_crs.isValid(): 
    crs_for_clipping=QgsCoordinateReferenceSystem("EPSG:25832")
    merged_raster.setCrs(crs_for_clipping)
    print(f"Invalid crs: Raster CRS and source CRS during clipping set to {crs_for_clipping} (assumed to be the german geoata default)")
else: crs_for_clipping="" # leave blank if layer crs is actual valid for QGIS, tehrefore the Oprtion is not set at all

# hardcoded Layer for clipping
clipLayer= QgsProject.instance().mapLayersByName(mask_layer)[0]

for fid in clipLayer.selectedFeatureIds():
    filename_clip=clipLayer.getFeature(fid)[field]

if not merged_raster.isValid():
    print("Merged Layer ist invalid: Typische Ursache -> DEM innerhalb einer ZIP")

# define to use only the selected features (since otherwise only 0 is written - test with GUI results in python error when using without the check for slected layers)
mask_def = QgsProcessingFeatureSourceDefinition(
                clipLayer.id(),          # any string that identifies the layer
                selectedFeaturesOnly=True 
            )

params_clip={
    'INPUT' : merged_raster,
    'MASK' : mask_def, 
    'SOURCE_CRS': crs_for_clipping,
    'CROP_TO_CUTLINE' : True,
    'KEEP_RESOLUTION' : True,
    'DATA_TYPE' : 6,
    'OUTPUT' : f"{clip_path}/{filename_clip}.tif"
}

processing.run("gdal:cliprasterbymasklayer", params_clip)

print("fertsch")