import PY_klayout
import sys, os
#default path for current release 
sys.path.append("C:\\Program Files\\Lumerical\\v242\\api\\python\\") 
sys.path.append(os.path.dirname(__file__)) #Current directory
try:
    import lumapi
except:
    print("LumAPI could not be imported. Please check the path in lumtogds.py, line 4.")
import numpy as np
from numpy import savetxt
from numpy import loadtxt
import re
from pathlib import Path

class setting:
    INPUT_FILENAME = "example/test.fsp"           #STRING: path to file, the root folder is the library directory.
    EXPORT_FILENAME = "lumexport.gds"             #STRING: Final file name, saves in the "output" folder
    LAYER_UNASSIGNED = 99                         #INT: value to give a layer if it wasn't assigned by the user
    DEFAULT_GDS_NAME_TEMP = "output"              #STRING: intermediate file name
    DEFAULT_TOP_CELL_NAME = "model"               #STRING: top cell name of the GDS, required by Lumerical Functions, doesn't seem to be functional?
    HIDE_LUMERICAL = True                         #BOOLEAN: show or hide lumerical interface
    LOAD_LAYER_FILE = False                       #BOOLEAN: True to load layer information, false to use python CMD to set layers
    LOAD_LAYER_FILENAME = "example/mylayercsv"    #STRING: output file will have .csv extension
    SAVE_LAYER_FILE = True                        #BOOLEAN: True to save the generated layer file from the python CMD as .csv
    SAVE_LAYER_FILENAME = "example/mylayercsv"    #STRING: Filename to save .csv 

    #DEPRECATED    
    #Advanced settings (Lumerical Export Function)
    # n_circle = 64;	# number of sides to use for circle approximation (64 by default).
    # n_ring = 64;	# number of slices to use for ring approximation (64 by default).
    # n_custom = 64;	# number of slices to use for custom approximation (64 by default).
    # n_wg = 64;		# number of slices to use for waveguide approximation (64 by default). 
    # round_to_nm = 1;	# round the z and z span to the nearest integer of nm
    # grid = 1e-9;	# Round XY coordinates to this grid in SI. Will also update the database units if grid < 
    # max_objects = 10000;	# the maximum number of objects within the workspace (Increasing this will increase export time)
    #

#Run Lum files
#TODO add in configurable files.
def main(SETTING = setting()):
    metadata, dupe, ori, FDTD = get_object_metadata(SETTING)
    layerinfo = assign_layerinfo(metadata,dupe,ori,SETTING)
    export2gds(
        FDTD,
        layerinfo,
        metadata,
        dupe,
        ori,
        SETTING
        )
    if PY_klayout.klayout_mergefiles():
        print("Success: Export Complete.")
    else:
        print("Error: Final merge step did not complete.")

def get_object_metadata(SETTING=setting()):
    FDTD = lumapi.FDTD(hide=SETTING.HIDE_LUMERICAL, filename=SETTING.INPUT_FILENAME)
    code = open('LUM_auto_detect.lsf', 'r').read()
    FDTD.eval(code) #loads the function into Lumerical
    metadata = FDTD.get_objects_info() #calls the function from LSF
    print(type(metadata))
    
    dupdata = FDTD.get_duplicate_layers(metadata)
    dupe = dupdata[:,1]-1 #lumerical uses index starting at 1, so -1 is necessary
    ori = dupdata[:,0]-1
    dupe = np.delete(dupe,0) #strip of the -1 index that Lumerical cannot remove (index lines up with names of the dictionaries)
    ori = np.delete(ori,0)
    dupe = [int(item) for item in dupe]
    ori = [int(item) for item in ori]
    
    return metadata,dupe,ori,FDTD

def assign_layerinfo(metadata,dupe,ori,SETTING=setting()):
    #automatically assign the layers based on material, then heights
    #can have a full list of Lumerical's material names, ahve it written that way
    if not SETTING.LOAD_LAYER_FILE:
        layerinfo = layerinfo_creator_UI(metadata,dupe,ori)
        #replace any unassigned layers with the default layer number
        for i in range(0,len(layerinfo)):
            if layerinfo[i][0] == None:
                layerinfo[i][0] = SETTING.LAYER_UNASSIGNED    
    
    #Load an existing layer file
    else:        
        if Path(SETTING.LOAD_LAYER_FILENAME+".csv").is_file():
            layerinfo = loadtxt('{}.csv'.format(SETTING.LOAD_LAYER_FILENAME), delimiter=',') #maybe needs fmt="%d" ?
            print("Loading layer from: {}.csv".format(SETTING.LOAD_LAYER_FILENAME))
        else:
            input("Layer Assignemnt File not found. Defaulting to Python UI. Press enter to continue.")
            layerinfo = layerinfo_creator_UI(metadata,dupe,ori)
            #replace any unassigned layers with the default layer number
            for i in range(0,len(layerinfo)):
                if layerinfo[i][0] == None:
                    layerinfo[i][0] = SETTING.LAYER_UNASSIGNED
            
    if SETTING.SAVE_LAYER_FILE:
        savetxt('{}.csv'.format(SETTING.SAVE_LAYER_FILENAME), layerinfo, delimiter=',',fmt="%d")
        print("Layer Assignment saved to file: {}.csv".format(SETTING.SAVE_LAYER_FILENAME))
    
    return layerinfo

def layerinfo_creator_UI(metadata,dupe,ori):
    #similar as the GUI wizard, CMD UI asking for layer assignments
    layerinfo = [[0 for i in range(2)] for j in range(len(metadata['material']))]
    for layer in layerinfo:
        layer[0] = None
    
    #calculate regex range
    rangesupported = True
    table_length = len(metadata['material'])
    if table_length < 10:
        regex_obj = "([0-{}])".format(int(table_length))
    elif table_length >= 10 and table_length < 100:
        tens = str(table_length)[0]
        ones = str(table_length)[1]
        regex_obj = "([0-9]|[1-{}][0-{}])".format(tens,ones)
    elif table_length == 100:
        regex_obj = "([0-9]|[1-9][0-9]|100)"
    else: 
        rangesupported = False
        
    output = 'Command List===\n'+\
        '"X Y"    | Assign layer Y to object X. Datatype remainds untouched. Value up to 100.\n'+\
        '"X Y Z"  | Assign a layer Y and datatype Z to object X. Value up to 100.\n'+\
        '"X none" | Unassign the layer for Object X.\n'+\
        '"done"   | Continue to the next step of exporting with the above layer information.\n'+\
        '==============='
    
    if rangesupported:
        UI = True
        print("No layerinfo file provided, proceeding with UI to generate.")
        commandoutput=''
    else:
        UI = False
        print("Error: Metadata list to large (100+)")
        input("Enter to quit.")
        exit()   
    
    while UI:
        os.system('cls' if os.name == 'nt' else 'clear') #multi-platform clear terminal
    
        print(layer_table(metadata,dupe,ori,layerinfo))
        print(output+commandoutput)
        commandoutput=''
        command = input("Command: ")
        if command == 'done': 
            print("Generating LayerInfo.")
            UI = False
        
        #assign layer    
        elif re.match('^{} ([0-9]|[1-9][0-9]|100)$'.format(regex_obj),command): #regex, match 3 digits for 3 numbers, separated by a space
            command = command.split(' ')
            objectindex = command[0] 
            if int(objectindex) == any(dupe):
                commandoutput = '\nWarning: Layer not applied, Object shares a layer with another object.\n'
            else:
                layervalue = command[1]
                commandoutput=''
                commandoutput = '\nOutput: Object {} assigned with: Layer {}\n'
                commandoutput = commandoutput.format(objectindex,layervalue)
                layerinfo[int(objectindex)][0] = int(layervalue)
                
        #assign layer and datatype
        elif re.match('^{} ([0-9]|[1-9][0-9]|100) ([0-9]|[1-9][0-9]|100)$'.format(regex_obj),command):
            command = command.split(' ')
            objectindex = command[0]
            if int(objectindex) == any(dupe):
                commandoutput = '\nWarning: Layer not applied, Object shares a layer with another object.\n'
            else:
                layervalue = command[1]
                datavalue = command[2]
                commandoutput=''
                commandoutput = '\nOutput: Object {} assigned with: Layer {} Datatype {}\n'
                commandoutput = commandoutput.format(objectindex,layervalue,datavalue)
                layerinfo[int(objectindex)][0] = int(layervalue)
                layerinfo[int(objectindex)][1] = int(datavalue)
            
        else:
            commandoutput = "\nOutput: Command Error.\n"
    
    return layerinfo

def layer_table(metadata,dupe,ori,layertable):
    #Prints out the layer table information
    header1= "Obj#"
    header1= '{:<7}'.format(header1[:7])
    header2= "Layer"
    header2= '{:<7}'.format(header2) #do not truncate layer:data value
    header3= "Material"
    header3= '{:<30}'.format(header3[:30])
    header4 = "zmin"
    header4= '{:<10}'.format(header4) #zmin and zmax dont truncate
    header5 = "zmax"
    header5= '{:<10}'.format(header5)
    #print(header1+" | "+header2+" | "+header3+" | "+header4+" | "+header5+" | ")
    output = header1+" | "+header2+" | "+header3+" | "+header4+" | "+header5+" | \n"
    
    for data_index, data in enumerate(metadata['material']):
        for dup_index, dup_data in enumerate(dupe):
            if data_index == dup_data:
                entry1 = str(data_index)
                entry1 = '{:<7}'.format(entry1[:7])
                entry2 = "Obj{}".format(int(ori[dup_index]))
                entry2 = '{:<7}'.format(entry2[:7])
                if metadata['material'][data_index] == "<Object defined dielectric>":
                    entry3 = str(metadata['index'][data_index])
                else:
                    entry3 = str(metadata['material'][data_index])
                entry3 = '{:<30}'.format(entry3[:30])
                entry4 = str(metadata['zmin'][data_index])
                entry4 = '{:<10}'.format(entry4)
                entry5 = str(metadata['zmax'][data_index])
                entry5 = '{:<10}'.format(entry5)
                #print(entry1+" | "+entry2+" | "+entry3+" | "+entry4+" | "+entry5+" | ")
                output = output +(entry1+" | "+entry2+" | "+entry3+" | "+entry4+" | "+entry5+" | \n")
            else:
                entry1 = str(data_index)
                entry1 = '{:<7}'.format(entry1[:7])
                if str(layertable[data_index][0]) == "None":
                    entry2 = str(layertable[data_index][0])
                else:
                    entry2 = str(layertable[data_index][0])+":"+str(layertable[data_index][1])
                entry2 = '{:<7}'.format(entry2)
                #entry3 = str(metadata['material'][data_index])
                if metadata['material'][data_index] == "<Object defined dielectric>":
                    entry3 = str(metadata['index'][data_index])
                else:
                    entry3 = str(metadata['material'][data_index])
                entry3 = '{:<30}'.format(entry3[:30])
                entry4 = str(metadata['zmin'][data_index])
                entry4 = '{:<10}'.format(entry4)
                entry5 = str(metadata['zmax'][data_index])
                entry5 = '{:<10}'.format(entry5)
                #print(entry1+" | "+entry2+" | "+entry3+" | "+entry4+" | "+entry5+" | ")
                output = output+ (entry1+" | "+entry2+" | "+entry3+" | "+entry4+" | "+entry5+" | \n")
    
    return output

def export2gds(FDTD,layerinfo,metadata,dupe,ori,SETTING=setting()):
    #A copy of the latter half of the LSF GUI wizard
    #checks if the layer entry is a duplicate, if it is, copy the duplicate's original values
    #if not, write to the format used by Lumerical's export functions    
    layer_def = [dict['z':None,'material':None,'layer':None] for _ in range(len(metadata['material']))]
    for i in range(len(metadata['material'])):
        if i==any(dupe):
             for j in range(len(dupe)):
                 if i==dupe[j]:
                    #   layer_def[i][0] = layer_def[ori[j]][0] #layer 
                    #   layer_def[i][1] = layer_def[ori[j]][1] #datatype
                    #   layer_def[i][2] = layer_def[ori[j]][2] #zmin
                    #   layer_def[i][3] = layer_def[ori[j]][3] #zmax

                    #update
                    layer_def[i] = {
                        'z':    layer_def[ori[j]]['z'],
                        'material':layer_def[ori[j]]['material'],
                        'layer':layer_def[ori[j]]['layer']
                    }
              
        else:
            # layer_def[i][0] = layerinfo[i][0]
            # layer_def[i][1] = layerinfo[i][1]
            # layer_def[i][2] = metadata['zmin'][i]                      
            # layer_def[i][3] = metadata['zmax'][i]

            # update
            if metadata['material'][i] == "<Object defined dielectric>": #TEMP SOLUTION, DIELECTRIC
                layer_def[i] = {
                'z': (metadata['zmin'][i]+metadata['zmax'][i])/2,
                'material': metadata['index'][i],
                'layer': str(layerinfo[i][0])+":"+str(layerinfo[i][1])
                }
            else:
                layer_def[i] = {
                'z': (metadata['zmin'][i]+metadata['zmax'][i])/2,
                'material': metadata['material'][i],
                'layer': str(layerinfo[i][0])+":"+str(layerinfo[i][1])
                }

    # print(layer_def[0]['z'])
    # print(type(layer_def[0]['z']))
    # print(layer_def[0]['material'])
    # print(type(layer_def[0]['material']))
    # print(layer_def[0]['layer'])
    # print(type(layer_def[0]['layer']))
    #layer_def = np.insert(layer_def,0,np.array([0,0,0,0])) #re-insert the empty first line, because lumerical uses index 1
    
    #Directory needs to be changed to the libraries one to properly import lumerical's encrypted functions          
    thispath = os.path.dirname(os.path.abspath(__file__))
    thispath = thispath.replace(os.sep, '/')
    FDTD.eval("cd('"+thispath+"');")
    
    #putv can be used to pass variables, this is used here because sometimes LSF method of importing scripts doesn't work in nested functions
    code = open('PY_exportmacro.lsf', 'r').read()
    FDTD.putv('metadata',metadata)
    FDTD.putv('layer_def',layer_def)
    FDTD.putv('gds_filename_temp',SETTING.DEFAULT_GDS_NAME_TEMP)

    #deprecated:
    # FDTD.putv('top_cell',SETTING.DEFAULT_TOP_CELL_NAME)
    # FDTD.putv('n_circle',SETTING.n_circle)
    # FDTD.putv('n_ring',SETTING.n_ring)
    # FDTD.putv('n_custom',SETTING.n_custom)
    # FDTD.putv('n_wg',SETTING.n_wg)
    # FDTD.putv('round_to_nm',SETTING.round_to_nm)
    # FDTD.putv('grid',SETTING.grid)
    # FDTD.putv('max_objects',SETTING.max_objects)
    #

    FDTD.eval(code) #loads the function into Lumerical
    
if __name__ == "__main__":
    main()
