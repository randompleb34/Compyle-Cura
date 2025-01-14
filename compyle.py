####################################################################################################################################
# Copyright         : 2025 Michael C Song (randompleb34)
# File Name         : Compyle.py
# Description       : Plugin for Cura 5.8.x and above on MacOS Sonoma 14.6.x. Converts G-Code into ascript file for Aerotech 
#                     Automation 1 XR3 and Nordson pressure box.
#                    
# Revision History  :
# Date		        Author 			    Comments
# ------------------------------------------------------------------
# 01/13/2024        Michael C Song      Optimized file writing
# 01/12/2024        Michael C Song      Integated search and replace script
# 12/17/2024        Michael C Song      Rewritten into script for Cura 5.8
# 12/10/2024        Michael C Song      Working sample for Cura 5.8 with VSC on MacOS Sonoma 14.6.x
# 12/10/2024        Michael C Song      Deprecated use of Prusaslicer in favor of Cura and included coasting features
# 11/25/2024        Michael C Song      Working sample for PrusaSlicer with Google Colab
# 11/24/2024        Michael C Song      File created
####################################################################################################################################

#!/usr/bin/python3

import re
import os
import json
from pathlib import Path
from ..Script import Script # sliced G-Code

def search_and_replace(default_dict, default_data):
    if default_dict == 'default':
        default_dict = {"( E)(.*?)(\n)":    "; ON\n",
                        "(F)(.*?)( )":  "",
                        "(G1 ON)(.*?)(\n)":    "",}
    else:
        default_dict = json.loads(default_dict)
        
    for key, value in default_dict.items():         
        search_regex = re.compile(key)    
        for layer_number, layer in enumerate(default_data):
            default_data[layer_number] = re.sub(search_regex, value, layer)
            
    reformatted_data = []
            
    for layer in default_data[2 : len(default_data) - 2]:
        line_list = layer.split("\n")
        for line in line_list:
            reformatted_data.append(f'{line}\n')
    
    return reformatted_data

def file_reader(sys, data_in):
    if sys == "mac":
        header_file = r"/compyle_static/header.txt"
        footer_file = r"/compyle_static/footer.txt"
        temp_gen_file = r"/compyle_static/temp.txt"
    else:
        header_file = r"\compyle_static\header.txt"
        footer_file = r"\compyle_static\footer.txt" 
        temp_gen_file = r"\compyle_static\temp.txt"
       
    script_dir = os.path.dirname(os.path.abspath(__file__))
        
    with open(script_dir + header_file, "r") as f:
        temp_header = f.readlines()

    with open(script_dir + footer_file, "r") as f:
        temp_footer = f.readlines()
        
    # with open(script_dir + r"/compyle_static/data.txt", "w") as f:
    #     count = 0
    #     for layer in data_in:
    #         f.write(str(count))
    #         f.write(layer)
    #         cou += 1
            
    return temp_header, temp_footer, script_dir + temp_gen_file
    
class compyle(Script):
    """Formats G-Code to be compatable with AeroScript and Nordson Pressure Box"""
    def getSettingDataString(self):
        return """{
            "name": "Compyle",
            "key": "Compyle",
            "metadata": {},
            "version": 2,
            "settings":
            {   
                "system":
                {
                    "label": "Operating System",
                    "description": "Select computer operating system. Default is MacOS.",
                    "type": "enum",
                    "options": {
                        "mac": "MacOS Sonoma+",
                        "windows": "Windows 10+"
                    },
                    "default_value": "mac"
                },
                "flowrate":
                {
                    "label": "Flowrate (mm/s)",
                    "description": "Sets gantry speed.",
                    "type": "float",
                    "default_value": 60.0
                },
                "pressure":
                {
                    "label": "Pressure (psi)",
                    "description": "Sets the pressure of the pressure box.",
                    "type": "float",
                    "default_value": 60.0
                },
                "start_dwell":
                {
                    "label": "Extrude Dwell (s)",
                    "description": "Delay between start of extrusion and gantry move.",
                    "type": "float",
                    "default_value": 0.15
                },
                "end_dwell":
                {
                    "label": "Retract Dwell (s)",
                    "description": "Delay between end of extrusion and gantry move.",
                    "type": "float",
                    "default_value": 0.15
                },
                "pressure_step_type":
                {
                    "label": "Pressure Step",
                    "description": "Enables pressure increase based on layer height or object order.",
                    "type": "enum",
                    "options": {
                        "disable": "Disabled",
                        "layer_step": "Layer based (single object)",
                        "object_step": "Object based (multi-object sequential printing)"
                    },
                    "default_value": "disable"
                },
                "pressure_step_val":
                {
                    "label": "Pressure Step (psi)",
                    "description": "Set pressure increase based on layer height or object order. Set to 0 to disable.",
                    "type": "float",
                    "default_value": 0.5
                },
                "replace":
                {
                    "label": "[ADVANCED] Search and Replace (regex))",
                    "description": "Leave as default. Replaces all instances of given regex. Format as a Python dict.",
                    "type": "str",
                    "default_value": "default"
                }
            }
        }"""
            
    def execute(self, data):    
        header, footer, gen_file = file_reader(self.getSettingValueByKey("system"), data)  
        lines = search_and_replace(self.getSettingValueByKey("replace"), data)
            
        # System Parameters
        extrude = False
        coast_end = False
        count = 0

        # User Parameters
        extrude_dwell = self.getSettingValueByKey("start_dwell")
        retract_dwell = self.getSettingValueByKey("end_dwell")
        pressure = self.getSettingValueByKey("pressure")
        pressure_step_val = self.getSettingValueByKey("pressure_step_val")
        flow_rate = self.getSettingValueByKey("flowrate")
        pressure_step_type = self.getSettingValueByKey("pressure_step")

        pressure_increase = pressure_step_val

        # Write to temp file
        with open(gen_file, "w") as of:
            # Write header, feedrate, and pressure
            of.writelines(header)    
            of.write(f'Callback(1, [0], [{pressure}], ["setPressureNordson"], $integerOutputs, $realOutputs, $stringOutputs); Set Pressure\n')  
            of.write(f'F{flow_rate}; Flowrate\n\n')
            of.write(';start of g-code\n\n')              

            # Process G-Code
            for i, line in enumerate(lines):
                if '; ON' in line:
                    if '; ON' in lines[i - 1] or '; ON' in lines[i + 1]:
                        if not extrude:
                            of.write('Callback(1, [0], [], ["togglePressureNordson"], $integerOutputs, $realOutputs, $stringOutputs); ON\n')
                            of.write(f'G4 P{extrude_dwell}\n')
                            extrude = True
                            of.write(line)
                        
                        else:
                            of.write(line)
                            
                elif ';LAYER:' in line: # pressure stepping
                    
                    if pressure_step_type == 'layer_step':
                        of.write(line)
                        of.write(f'Callback(1, [0], [{pressure + pressure_increase}], ["setPressureNordson"], $integerOutputs, $realOutputs, $stringOutputs); increase pressure\n')

                        if (pressure + pressure_increase * 2) < 80:
                            pressure_increase += pressure_step_val
                            
                    elif pressure_step_type == 'object_step':
                        if ';LAYER:0' in line:
                            of.write(line)
                            of.write(f'Callback(1, [0], [{pressure + pressure_increase}], ["setPressureNordson"], $integerOutputs, $realOutputs, $stringOutputs); increase pressure\n')
                        
                        else:
                            of.write(line)
                            
                        if (pressure + pressure_increase * 2) < 80:
                            pressure_increase += pressure_step_val
                    
                    else:
                        of.write(line)

                elif extrude:
                    of.write('Callback(1, [0], [], ["togglePressureNordson"], $integerOutputs, $realOutputs, $stringOutputs); OFF\n')
                    of.write(line)
                    extrude = False
                    coast_end = True
                    count += 2

                elif coast_end == True and count == 2:
                    of.write(line)
                    of.write(f'G4 P{retract_dwell}; Dwell\n')
                    coast_end = False
                    count = 0
                    
                else:
                    of.write(line)
                    coast_end = True
                    count = 0

        # Write footer
        of.writelines(footer)
            
        with open(gen_file, "r") as f:
            content = f.readlines()
        
        # Offset datalist
        content.insert(0, data[0])
            
        return content
            
    