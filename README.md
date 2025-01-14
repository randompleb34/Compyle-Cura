# Compyle for Cura 5.x 
Compyle is a two part plugin and post-processing script for slicing and exporting of AeroScript (.ascript) files all within Cura. This is designed to be used for Aerotech Automation1 motion controllers and Nordson fluid dispensers. The post-processing script rewrites the generated g-code into a format readable by Automation1. The plugin then takes the g-code in the entire scene and write it to an output device as an .ascript file.

The plugin is based on Cura's built in [GCodeWriter.py](https://github.com/Ultimaker/Cura/tree/main/plugins/GCodeWriter) plugin.

## Installation

**Script**

Download the compyle.py and compyle_static folder and place both into Cura's scripts folder which can be located here:
- Windows 10: [Cura installation folder]/scripts
- MacOS Sonoma+: ~/Library/Application Support/cura/[CURA VERSION]/scripts

<br />

**Plugin**

Download the AScriptWriter folder and place into Cura's plugins folder which can be located here:
- Windows 10: [Cura installation folder]/plugins
- MacOS Sonoma+: ~/Library/Application Support/cura/[CURA VERSION]/plugins

<br />

Note: The nested folder for AScriptWriter is intentional. The directory will not be found by Cura if it is removed.
