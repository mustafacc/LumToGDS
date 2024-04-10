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
    
klayout_formatfile()