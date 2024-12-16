"""
Description:
use ETO forms to genreate interaction form for users to process their g
Link; http://developer.rhino3d.com/guides/rhinopython/eto-forms-python/
"""

"""ObjToObj is from prev dev: Finds the closest distance between 2 Brep objects by iteration.
Starts with coarse mesh approximation of one part and refines answer
Written by Mitch Heynick in vb October 2011, --> Python/RhinoCommon 24.06.16
Revised 24.08.16 - fixed bug in initial meshing of object.
imported by Nathan Barnes 22.08.24"""

__author__ = "nbarnes"
__version__ = "0.01.0"

# Imports
import Rhino
import scriptcontext
import System
import Rhino.UI
import Eto.Drawing as drawing
import Eto.Forms as forms
import Eto
import webbrowser
import os
import rhinoscriptsyntax as rs
import time
import scriptcontext as sc

def leaderMaterial():
    #layer setup
    currentLayer = rs.CurrentLayer()
    rs.CurrentLayer('DRAFTING::NOTES')
    
    Rhino.RhinoApp.RunScript(r"!_-GrasshopperPlayer C:\Box\Engineering\parametric{COLAB}\_Tools\200_SubmittalTools\LEADER_WITH_SHAPE_SCRIPT092922.gh ", True)

    
    rs.CurrentLayer(currentLayer)

#__commandname__ = "BELT"

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filname minus "_cmd.py"
def runLeader():
        
    
    leaderMaterial()
    

if __name__ == '__main__':runLeader()