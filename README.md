# LumToGDS
Lumerical GUI Wizard and Python Library for exporting geometries into GDS format.
Wrapper built around functions released by Lumerical: [Link](https://optics.ansys.com/hc/en-us/articles/1500006203341-GDSII-Export-Automation)

This wrapper uses a command-line Klayout 0.26 to resave GDS files to make them compatible with later Klayout releases.

# Installation
## Python Prerequistes
- [ ] Python x64, 3.9 ONLY (Tested on 3.9, x64).
- [ ] Klayout 0.26.12 Python API 
- [ ] LumAPI

# Installation Instructions
1. Install Python 3.9 x64
2. In the windows command-line, run the command: `pip install -r requirements.txt` to automatically install the required libraries.
3. Confirm/Add the Python 3.9 Environment Path
    1. Open the Start Menu and type "Edit system environment variables"
    2. In the popped up window, click "Environment Variables"
    3. Select the "Path" entry at the top, under "user variarables", and click edit.
    4. Click "New" on the right, and provide the path to the python 3.9 executable 
        - E.g.: `C:\users\YOURUSER\AppData\Local\Programs\Python\Python39\`
    5. Click "New" on the right, and provide a path to the python script folder.
        - E.g.: `C:\users\YOURUSER\AppData\Local\Programs\Python\Python39\Scripts\`
4. Launch FDTD and update the settings to use the local Python, not the integrated Python.
    - From the top drop-down menu, select help>Python Integration Status> and uncheck the "Use Python provided by Lumerical" option.
    - Also confirm the Executable path is pointing to the the python.exe from the Path in Step 3.4.
5. Clone or download this repository and save it to an accessible location.
    - The wrapper refers to the provided files locally, changing any of the files locations relative to each other will require updating the script.

# How to use
- All files must be in the same folder. The relative file hierarchy of `.py`, `.lsf`, and `.lsfx` files MUST remain as is.
- Do not delete the output folder
- File names beginnning with `TEMP_output` and ending with `.gds` in the output folder will be merged into `lumexport.gds` and deleted automatically. To avoid any chance of accidental deletion, please do not save important files in this folder.

## LSF Wizard Method
1. Launch Lumerical FDTD and load your .fsp file you wish to extract.
2. In the script editor, load "mainLSF.lsf" and click "Run".
    - A wizard should pop up and provide you with the detected objects for confirmation
    - Follow the wizard instructions and provide the layout layer number that will be assigned to each detected object/material
    - Objects with same material will automatically use the same entry, simplifying the entry process.
    - Objects with the same material and different height will each require an entry.
3. A command-line window should pop up. If the readout confirms successs GDS extraction, you can close the CMD window.
4. Navigate to where you have saved the folder containing the LumToGDS library. Under the "output" folder, you should find your exported file "lumexport.gds"

## Python Method
Example available in `Main.py`.
1. `Import lumtogds`.
2. Creating a settings object with the parameters you wish to run the export with.
3. call `main()`
    - If the layer assignment is not loaded from a file, the command-line will provide a UI to create layer assignments.

# Example File
A makefile is provided that generates geoemtries in different situations to demonstrate LumToGDS' functionality.
1. Launch FDTD and load/run the script `example/example_makefile.lsf`
2. Run via the LSF Wizard Method or Python Method.

# What does it do?
## LSF Wizard
1. Automatically extracts all geometries from the object hierarchy tree (note limitations, see below).
2. Prompts the user with a Wizard to quickly set the layer information for each detected, unique, object.
3. Exports all unique objects to a standalone GDS (Klayout 0.26 format, see limitations).
4. Merges all GDS into a single file.
5. Converts to up-to-date Klayout format by resaving using Klayout 0.26.

## Python Wizard
1. Uses `LumAPI` and `mainLSF.lsf` to obtain the object tree from Lumerical.
2. Attempts to load a Layer Assignment File (numpy array). If none found, a CMD UI procedure will be used to create layer assignments. Users can save the file to avoiding requiring manual assignment again.
3. Each object is exported into a GDS file.
4. All GDS files are merged into a single file.
5. Converts to up-to-date Klayout format by resvaing using Klayout 0.26.

## Limitations - Geometry Objects
- Geometry objects in the Lumerical object tree MUST have unique names. Same names will be overwritten by newer entries, no error will be prompted.
- Geoemtry objects cannot be nested (e.g. Groups, such as containers, structure groups, analysis groups, etc.). 
Please flatten the whole hierachy for extraction. You may consider copy and pasting the tree into a new FDTD instance by selecting the tree and ctrl+c/ctrl+v into a new FDTD file.

## Limitations - Klayout GDS Format Versions
- Klayout 0.27 went through a massive data structure update for GDS files resulting in an error when attempting to open files extracted by the functions provided by Lumerical. 
- Lumerical has confirmed there are no plans to update the function for newer Klayout versions at this time.
    - Please submit a feature request via: the [Ideas Exchange portal](https://ix.lumerical.com/) if you are interested in having newer versions supported. With enough interest, the Lumerical team will prioritize updating the functions.
- As a workaround, saving in Klayout 0.26 will update the GDS file into the newer formats used by later versions.

# For Complex geometries:
Please see this extraction method: [Link](https://optics.ansys.com/hc/en-us/articles/1500007228522-GDS-pattern-extraction-for-inverse-designed-devices-using-contours-method)
