import export2gds

mysetting = export2gds.setting()
mysetting.INPUT_FILENAME = "example/test.fsp"           #STRING: path to file, the root folder is the library directory.
mysetting.EXPORT_FILENAME = "lumexport.gds"             #STRING: Final file name, saves in the "output" folder
mysetting.LAYER_UNASSIGNED = 99                         #INT: value to give a layer if it wasn't assigned by the user
mysetting.DEFAULT_GDS_NAME_TEMP = "output"              #STRING: intermediate file name
mysetting.DEFAULT_TOP_CELL_NAME = "model"               #STRING: top cell name of the GDS, required by Lumerical Functions, doesn't seem to be functional?
mysetting.HIDE_LUMERICAL = True                         #BOOLEAN: show or hide lumerical interface
mysetting.LOAD_LAYER_FILE = False                       #BOOLEAN: True to load layer information, false to use python CMD to set layers
mysetting.LOAD_LAYER_FILENAME = "example/mylayercsv"    #STRING: output file will have .csv extension
mysetting.SAVE_LAYER_FILE = True                        #BOOLEAN: True to save the generated layer file from the python CMD as .csv
mysetting.SAVE_LAYER_FILENAME = "example/mylayercsv"    #STRING: Filename to save .csv 
    
#Advanced settings (Lumerical Export Function)
mysetting.n_circle = 64;	    # number of sides to use for circle approximation (64 by default).
mysetting.n_ring = 64;	        # number of slices to use for ring approximation (64 by default).
mysetting.n_custom = 64;	    # number of slices to use for custom approximation (64 by default).
mysetting.n_wg = 64;		    # number of slices to use for waveguide approximation (64 by default). 
mysetting.round_to_nm = 1;	    # round the z and z span to the nearest integer of nm
mysetting.grid = 1e-9;	        # Round XY coordinates to this grid in SI. Will also update the database units if grid < 
mysetting.max_objects = 10000;	# the maximum number of objects within the workspace (Increasing this will increase export time)

export2gds.main(mysetting)
