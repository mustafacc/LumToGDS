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
    
    import klayout.db as db #require 0.26.12
    ly = db.Layout()
    ly.read(input)
    ly.write(input)

def main():
    #detect if multiple files or one
    #format all files
    #merge if more than 1
    return

def klayout_mergefiles():
    return 
 
klayout_formatfile()