import PY_klayout
import sys, os
#default path for current release 
sys.path.append("C:\\Program Files\\Lumerical\\v241\\api\\python\\") 
sys.path.append(os.path.dirname(__file__)) #Current directory
import lumapi
import numpy as np
import re

#Run Lum files
def main():
    metadata, dupe, ori = get_object_metadata()
    assign_layerinfo(metadata,dupe,ori)
    #run klayout python

def get_object_metadata():
    FDTD = lumapi.FDTD(hide=True, filename="example/test.fsp")
    code = open('LUM_auto_detect.lsf', 'r').read()
    FDTD.eval(code) #loads the function into Lumerical
    metadata = FDTD.get_objects_info() #calls the function from LSF
    
    dupdata = FDTD.get_duplicate_layers(metadata)
    dupe = dupdata[:,1]
    ori = dupdata[:,0]
    dupe = np.delete(dupe,0) #strip of the -1 index that Lumerical cannot remove (index lines up with names of the dictionaries)
    ori = np.delete(ori,0)
    
    #print(dupe)
    return metadata,dupe,ori

def assign_layerinfo(metadata,dupe,ori,loadfile=False,savefile=True,filename="layerinfo"):
    #automatically assign the layers based on material, then heights
    #can have a full list of Lumerical's material names, ahve it written that way
    layerinfo = []
    
    if not loadfile:
        layerinfo = layerinfo_creator_UI(metadata,dupe,ori,layerinfo)
        
    #import a defined matrix
    else:
        print("TBD: load from file")
    
    if savefile:
        print("TBD: save to file")
    
    return layerinfo

def layerinfo_creator_UI(metadata,dupe,ori,layerinfo):
    #similar as the GUI wizard, printout asking for layer assignments
    layerinfo = [[0 for i in range(2)] for j in range(len(metadata['material']))]
    for layer in layerinfo:
        layer[0] = None
    
    #calculate regex range
    rangesupported = True
    table_length = len(metadata['material'])
    
    print(table_length)
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
            layervalue = command[1]
            commandoutput=''
            commandoutput = '\nOutput: Object {} assigned with: Layer {}\n'
            commandoutput = commandoutput.format(objectindex,layervalue)
            layerinfo[int(objectindex)][0] = int(layervalue)
            
        #assign layer and datatype
        elif re.match('^{} ([0-9]|[1-9][0-9]|100) ([0-9]|[1-9][0-9]|100)$'.format(regex_obj),command):
            command = command.split(' ')
            objectindex = command[0] 
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
                entry3 = str(metadata['material'][data_index])
                entry3 = '{:<30}'.format(entry3[:30])
                entry4 = str(metadata['zmin'][data_index])
                entry4 = '{:<10}'.format(entry4)
                entry5 = str(metadata['zmax'][data_index])
                entry5 = '{:<10}'.format(entry5)
                #print(entry1+" | "+entry2+" | "+entry3+" | "+entry4+" | "+entry5+" | ")
                output = output+ (entry1+" | "+entry2+" | "+entry3+" | "+entry4+" | "+entry5+" | \n")
    
    return output
                
def generate_export_info(metadata,dupe,ori,layerinfo,optionsettings):
    #using a given layer info, write out the array needed by Lumerical's export function
    #takes in option settings as well
    exportinfo = [] #formatted info
    return exportinfo

if __name__ == "__main__":
    main()
