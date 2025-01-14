####################################################################################################################################
# Copyright         : 2025 Michael C Song (randompleb34)
# File Name         : __init__.py
# Description       : Plugin to enable Cura to write .ascript files for Aerotech Automation 1
#                     Based on the GcodeWriter plugin by Ultimaker:https://github.com/Ultimaker/Cura/tree/master/plugins/GCodeWriter
#                     This plugin is released under the terms of the LGPLv3 or higher.
#
# Revision History  :
# Date		        Author 			    Comments
# ------------------------------------------------------------------
# 01/12/2024        Michael C Song      Rewritten for ascript
####################################################################################################################################

from . import AScriptWriter

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

def getMetaData():
    return {


        "mesh_writer": {
            "output": [{
                "extension": "ascript",
                "description": catalog.i18nc("@item:inlistbox", "AeroScript File"),
                "mime_type": "text/x-ascript",
                "mode": AScriptWriter.AScriptWriter.OutputMode.TextMode
            }]
        }
    }

def register(app):
    return { "mesh_writer": AScriptWriter.AScriptWriter() }
