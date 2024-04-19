import klayout.db as db #require 0.26.12

# def format_execute_lsf():
        # #export settings to lsf
        # mysettings = #
        # "layer_def=[" .... #Conitune here with a for loop
        # +"gds_filename=\""+gds_filename+"\";\n"
        # +"top_cell=\""+top_cell+"\";\n"
        # +"n_circle="+num2str(n_circle)+";\n"
        # +"n_ring="+num2str(n_ring)+";\n"
        # +"n_custom="+num2str(n_custom)+";\n"
        # +"n_wg="+num2str(n_wg)+";\n"
        # +"round_to_nm="+num2str(round_to_nm)+";\n"
        # +"grid="+num2str(grid)+";\n"
        # +"max_objects="+num2str(max_objects)+";\n"
        # +"Lumerical_GDS_autoexp_functions;\nLumerical_GDS_autoexp;\n";

        # write("export_settings.lsf",mysettings,"overwrite");
        # export_settings; #lsf file to run.

def klayout_formatfile(input="output.gds"):
    #Due to a format update in Klayout 0.27+, newer version of Klayout cannot read the file format exported
    #by the lumerical encrypted library. The work around is to load the file in Klayout26 and resave it.
    #I believe the issue is because the Lumerical encrpyted library is saving multiple topcells
    #This can be seen from the errors when loading them directly into Klayout 0.27+
    #Resaving seems to correct this as Klayout 26 will force a topcell (?)
    
    ly = db.Layout()
    ly.read(input)
    ly.write(input)

def klayout_mergefiles(directory="output",outputname = "lumexport.gds",removetempfiles=True):
    import os
    ly = db.Layout()
    top_cell = ly.create_cell("TOP")
    
    for file in os.listdir(directory):
        if file.endswith(".gds"):
            ly_import = db.Layout()
            ly_import.read(os.path.join(directory, file))
            imported_top_cell = ly_import.top_cell()

            target_cell = ly.create_cell(imported_top_cell.name)
            target_cell.copy_tree(imported_top_cell)

            # frees the resources of the imported layout
            ly_import._destroy()

            inst = db.DCellInstArray(target_cell.cell_index(), db.DTrans(db.DVector(0, 0)))
            top_cell.insert(inst)
            
            if removetempfiles:
                os.remove(os.path.join(directory, file))

    outputfullname = os.path.join(directory, outputname)
    ly.write(outputfullname)
    print("GDS files merged.")       
 
if __name__ == '__main__':
    klayout_mergefiles()