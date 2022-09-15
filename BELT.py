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


def RefineDist2Objs(objA, objB, ptA, ptB,tol):
    #ptA, ptB are initial estimations of closest point between objA and objB
    #pingpong function stolen from Pascal Golay
    curr_dist = ptA.DistanceTo(ptB)
    n=0 ; safe=1000 ; max_check=10 ; tol_factor=10.0
    
    for i in range(safe):
        ptB = objB.ClosestPoint(ptA)
        ptA = objA.ClosestPoint(ptB)
        new_dist = ptA.DistanceTo(ptB)
        #=========================================================
        if abs(curr_dist-new_dist)<(tol/tol_factor): n+=1 #tighter tolerance?
        else: n = 0
        if new_dist < curr_dist: curr_dist = new_dist
        if n > max_check: break
        
    return ptA, ptB, i-max_check #less the 10 iterations within tolerance

def ClosestPt2Objects():
    msg = "Select 2 objects for comparison"
    objIDs = rs.GetObjects(msg,8+16,preselect=True,minimum_count=2,maximum_count=2)
    if not objIDs: return
    
    tol=sc.doc.ModelAbsoluteTolerance
    obj_A=rs.coercebrep(sc.doc.Objects.Find(objIDs[0]).Geometry, True)
    obj_B=rs.coercebrep(sc.doc.Objects.Find(objIDs[1]).Geometry, True)
    
    #layer setup
    currentLayer = rs.CurrentLayer()
    rs.CurrentLayer('DRAFTING::DIM')
    
    #check for intersections and exit if found
    rc,crvs,pts=Rhino.Geometry.Intersect.Intersection.BrepBrep(obj_A,obj_B,tol)
    if rc:
        if len(crvs)!=0 or len(pts)!=0:
            print ("Objects intersect!" ); return
    #timer
    st=time.time()
    
    mesh_A=Rhino.Geometry.Mesh()
    mp=Rhino.Geometry.MeshingParameters.Default #fairly coarse mesh
    #mp=Rhino.Geometry.MeshingParameters.Coarse #default jagged and faster mesh
    mesh_parts=Rhino.Geometry.Mesh.CreateFromBrep(obj_A,mp)
    for mesh_part in mesh_parts: mesh_A.Append(mesh_part)
    mesh_A.Compact()
    verts_A=mesh_A.Vertices #returns point3f's must convert
    verts_A=[Rhino.Geometry.Point3d(vert) for vert in verts_A]
    
    #brute force method to get rough estimate
    rs.Prompt("Calculating initial value...")
    index_A=0
    for i in range(verts_A.Count):
        temp_cp=obj_B.ClosestPoint(verts_A[i])
        calc_dist=verts_A[i].DistanceTo(temp_cp)
        if i==0:
            dist=calc_dist
        else:
            if calc_dist < dist:
                dist=calc_dist ; index_A = i
                
    #have shortest rough distance: between verts_A(index_A)and temp_cp on obj_B
    pt_on_A = verts_A[index_A]
    pt_on_B = temp_cp    
    #rs.AddLine(ptOnA,ptOnB) #rough check
    #refine results by iteration
    rs.Prompt("Refining calculation...")
    final_pts = RefineDist2Objs(obj_A, obj_B, pt_on_A, pt_on_B,tol)
    
    #add final distance line and points
    rs.EnableRedraw(False)
    final_dist=final_pts[0].DistanceTo(final_pts[1])
    display_pts = rs.AddPoints([final_pts[0],final_pts[1]])    
    display_line = rs.AddLine(final_pts[0],final_pts[1])    
    group = rs.AddGroup()
    rs.AddObjectsToGroup(display_pts,group)
    rs.AddObjectToGroup(display_line,group)
    rs.ObjectColor(rs.ObjectsByGroup(group,True), rs.coercecolor([255, 0, 0]))
    rs.EnableRedraw(True)
    
    #reporting
    units = rs.UnitSystemName(False, True, True, True)
    prec=sc.doc.ModelDistanceDisplayPrecision
    
    msg="Minimum distance between objects is "
    msg+="{} {}".format(round(final_dist,prec),units)
    msg+="  |  {} refinement iterations".format(final_pts[2])
    msg+="  |  Calc time: {:.2f} seconds".format(time.time()-st)
    
    print (msg)
    
    Rhino.RhinoApp.RunScript("-_DimCurveLength -_SelID {} Style=Zahner_Regular _ZoomSelected ".format(display_line), False)
    
    
    rs.CurrentLayer(currentLayer)
    

def ClosestPtCrvFunc():
    #layer setup
    currentLayer = rs.CurrentLayer()
    rs.CurrentLayer('DRAFTING::DIM')
    
    Rhino.RhinoApp.RunScript("!_SelNone", False)
    Rhino.RhinoApp.RunScript("_ClosestPt pause Object", False)
    Rhino.RhinoApp.RunScript("_SelLast _LineThroughPt Delete ", False)
    Rhino.RhinoApp.RunScript("_SelLast Length ", True)
    Rhino.RhinoApp.RunScript("-_DimCurveLength selLast Style=Zahner_Regular _ZoomSelected ", False)
    
    rs.CurrentLayer(currentLayer)

def surfPlaneDim():
    #layer setup
    currentLayer = rs.CurrentLayer()
    rs.CurrentLayer('DRAFTING::DIM')
    
    Rhino.RhinoApp.RunScript("!_SelNone", False)
    Rhino.RhinoApp.RunScript("'_CPlane _Surface _Pause _Pause _Pause ", True)
    Rhino.RhinoApp.RunScript("_-Dim AnnotationStyle Zahner_Regular _Pause _Pause _Pause ", True)
    Rhino.RhinoApp.RunScript("_CPlane _World _Top ", False)
    
    rs.CurrentLayer(currentLayer)

#-----------------setup menu items----------------------

CheckBoxLabel = ['Brep to Brep', 'Brep/Crv To Crv', 'Surface plane Dim']
dimToolFunctionList = [ClosestPt2Objects, ClosestPtCrvFunc, surfPlaneDim]


class SetupMenu():
    def CreateOptions(self,options,default):
        #---------------------------------create option list
        
        self.m_combobox = forms.ComboBox()
        self.m_combobox.DataStore = options #'Rhino', 'Draft',
        
        self.m_combobox.SelectedIndex = default
        
        layout = forms.DynamicLayout()
        layout.AddRow (self.m_combobox)
        
        return layout
    def CreateCheckBox(self,label,default):
        # ------------------------------------Create checkboxes
        
        
        self.checkbox = forms.CheckBox(
            Text = label, 
            Checked = default,
            ThreeState = False
        )
        
        # ------------------------------------Create table layout
        layout = forms.DynamicLayout()      
        layout.AddRow (self.checkbox)
        
        return layout



class RunForm(forms.Dialog[bool]):
    
    
    # ------------------------------------Dialog box Class initializer
    def __init__(self):
        
        self.cboutput = [0]*CheckBoxLabel.Count
        
        # ------------------------------------Initialize dialog box
        self.Title = "BELT: Cook, convesationlist and a set of Dimension tools"
        self.Padding = drawing.Padding(15)
        self.Resizable = False
        
        #self.ClientSize = drawing.Size(300, 400) #sets the (Width, Height)
        
        layout = forms.DynamicLayout(Visible = True, 
        Padding = drawing.Padding(1, 1), 
        DefaultSpacing = drawing.Size(5, 15))
        #layout.Spacing = drawing.Size(15, 20)
        
        #        layout.AddRow("-------------------------------------------------------------------------------------------")
        #        layout.BeginVertical()
        
        #---------------------------------------Check box options
        layout.AddRow("Select one dimension option below")
        layout.BeginVertical()
        
        #DropDownMenuTest = SetupMenu()
        global CheckBox0
        CheckBox0=SetupMenu()
        #        layout.AddRow(None, CheckBox0.CreateCheckBox(CheckBoxLabel[0],False ))#CheckBoxStates[0]))
        
        global CheckBox1
        CheckBox1=SetupMenu()
        global CheckBox2
        CheckBox2=SetupMenu()
        #        layout.AddRow(None, CheckBox1.CreateCheckBox(CheckBoxLabel[1],False ))#CheckBoxStates[0]))
        
        layout.AddRow(CheckBox0.CreateCheckBox(CheckBoxLabel[0],False ), CheckBox1.CreateCheckBox(CheckBoxLabel[1],False ), CheckBox2.CreateCheckBox(CheckBoxLabel[2],False ))#CheckBoxStates[0]))
        
        
        # ------------------------------------Create controls for the dialog
        self.m_label = forms.Label(Text = 'Run the dim tool')
        
        # ------------------------------------Create the default button
        self.DefaultButton = forms.Button(Text = 'Yes')
        self.DefaultButton.Click += self.OnOKButtonClick
        
        # ------------------------------------Create the abort button
        self.AbortButton = forms.Button(Text = 'Cancel')
        self.AbortButton.Click += self.OnCloseButtonClick
        
        layout.AddRow(None, self.m_label, self.DefaultButton, self.AbortButton)
        
        layout.EndVertical()
        
        # ------------------------------------Set the dialog content        
        self.Content = layout
    
    # -------------------------------------Close button click handler
    def L(text):
        m_label = forms.Label()
        m_label.Text = text
        m_label.VerticalAlignment = forms.VerticalAlignment.Center
        m_label.TextAlignment = forms.TextAlignment.Right
        return m_label
    
    def OnCloseButtonClick(self, sender, e):
     self.Close(False)

    # -------------------------------------OK button click handler
    def OnOKButtonClick(self, sender, e):
    #        self.ddoutput[0] = DropDown0.m_combobox.DataStore[DropDown0.m_combobox.SelectedIndex]
    #        self.ddoutput[1] = DropDown1.m_combobox.DataStore[DropDown1.m_combobox.SelectedIndex]
    #        self.ddoutput[2] = DropDown2.m_combobox.DataStore[DropDown2.m_combobox.SelectedIndex]
    #        self.ddoutput[3] = DropDown3.m_combobox.DataStore[DropDown3.m_combobox.SelectedIndex]
    #        self.ddoutput[4] = DropDown4.m_combobox.DataStore[DropDown4.m_combobox.SelectedIndex]
    #        
    #        self.txoutput[0] = self.m_textbox0.Text
    #        self.txoutput[1] = self.m_textbox1.Text
        self.cboutput[0] = CheckBox0.checkbox.Checked
        self.cboutput[1] = CheckBox1.checkbox.Checked
        self.cboutput[2] = CheckBox2.checkbox.Checked
    #        self.cboutput[2] = CheckBox2.checkbox.Checked
    #        self.cboutput[3] = CheckBox3.checkbox.Checked
        
        self.Close(True)
        

def validateOnlyone(CheckboxList):
    i = 0
    
    for each in CheckboxList:
        if each == True:
            i+=1
    
    if i != 1:
        rs.MessageBox('hey, either too many checked \nor you did not check any, try again',0)
        
        RunCommand(True)
    return i



#__commandname__ = "BELT"

# RunCommand is the called when the user enters the command name in Rhino.
# The command name is defined by the filname minus "_cmd.py"
def TestBELT():
        
    
    dialog = RunForm()
    rc = dialog.ShowModal(Rhino.UI.RhinoEtoApp.MainWindow)
#    print rc
    
    CheckBoxOutput=dialog.cboutput
    
    if(rc):
        
        if validateOnlyone(CheckBoxOutput) != 1: return
        
#        print CheckBoxOutput
        for i in range(len(CheckBoxOutput)):
            if (CheckBoxOutput[i]):
                moduleToRun = dimToolFunctionList[i]
                
        
        moduleToRun()
    

if __name__ == '__main__':TestBELT()