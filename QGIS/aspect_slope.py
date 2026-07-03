import os, processing 

todo=["aspect","slope"] #tasks to perform (correspondent to the name of the QGIS process after the :)
input_folder="..." #paths where the input files (e.g. clipped DEMs) are saved
path="..." #path where the files should be saved to (aspect and slope subfolders will be automatically generated)
for f in os.listdir(input_folder):
    if f.endswith('.tif'): 
        filename=f.split(".")[0]
        raster=QgsRasterLayer(f"{input_folder}/{f}")

        for task_item in todo:
            params={
                'INPUT': raster,
                'Z_FACTOR':1,
                'OUTPUT':f"{path}\{task_item}\{filename}_{task_item}.tif"
            }

            processing.run("native:{task_item}", params)
            
            print(f"{task_item} für {filename} sind ermitelt.")