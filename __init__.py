import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.utils import register_class, unregister_class

from bpy.props import BoolProperty, FloatProperty, PointerProperty

############################################################################

bl_info = {
    "name": "Haydee Blender Tools",
    "author": "rekooo",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View 3D > UI > HDTools",
    "description": "Import/Export tools for HDAurora",
    "warning": "",
    "wiki_url": "Add later",
    "tracker_url": "Add later",
    "category": "Import-Export",
}

############################################################################
#from . import HDExporter
# import classes from others .py files
from .HDExporter import HDExportSingle, HDExportMotion, HDExportSkeleton, HDExportPose




def test1(self, context):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 1), scale=(2, 2, 2))
    return {'FINISHED'}

# Property ------------------------ //



class HDBProps(PropertyGroup):
    bSelectedOnly : BoolProperty(
        name = 'Selected only',
        default = False
    )
    bLocalPosition : BoolProperty(
        name = 'Local position',
        default = False
    )

# Export single mesh -------------------- //

class ExportDmeshSingle(Operator):
    bl_idname = 'object.dmeshexportsingle'
    bl_label  = 'Old Single dmesh export'
    
    def execute(self, context):
        test1(self, context)
        return {'FINISHED'}

# --------------------------------- //

class HDBExporter(Operator):
    bl_idname  = 'object.exporter' # Dont use up register and start 'object.==name=='
    bl_label   = 'Exporter'
        
    def execute(self, context):
        bpy.ops.wm.splash('INVOKE_DEFAULT')
              
        return {'FINISHED'}
    
# MENU PANEL -------------------------------------------

class OBJECT_PT_HDBEXPORTER(Panel):
    bl_label       = 'Haydee Exporter'  #
    bl_space_type  = 'VIEW_3D'          # Context where panel avalible
    bl_region_type = 'UI'               #
    bl_category    = 'HDTools'          # Name on right side of viewport
        
    def draw(self, context):
        layout = self.layout
        props  = context.scene.hdeProps # Take parameters from scene
        
        
        #layout.label(text="Big Button:")
        #col = col.box()
        row = layout.row()
        row.scale_y = 1.0
        row.operator("object.exportsingle", text='Single') # ButtonClick, text we take from class bl_label
        #row.operator("render.render")
        row = layout.row()
        row.scale_y = 1.0
        row.operator("object.dmeshexportsingle", text='Batch') # ButtonClick, text we take from class bl_label
        row = layout.row()
        row.scale_y = 1.0
        row.operator("object.exportmotion", text='Motion') # ButtonClick, text we take from class bl_label
        row = layout.row()
        row.scale_y = 1.0
        row.operator("object.exportskeleton", text='Skeleton') # ButtonClick, text we take from class bl_label
        row = layout.row()
        row.scale_y = 1.0
        row.operator("object.exportpose", text='Pose') # ButtonClick, text we take from class bl_label
        
        col = layout.column()
        #col.prop(props, 'bSelectedOnly')
        col.prop(props, 'bLocalPosition')

#-------------------------------------------------------
#-------------------------------------------------------
#-------------------------------------------------------

classes = [
    HDBProps,
    ExportDmeshSingle,
    HDBExporter,
    OBJECT_PT_HDBEXPORTER,
    HDExportSingle,
    HDExportMotion, 
    HDExportSkeleton, 
    HDExportPose
]



# Important sys code for addon

def register():   # Sys register classes in system
    for cl in classes:
        register_class(cl)
    bpy.types.Scene.hdeProps = PointerProperty(type = HDBProps) # set parameters on scene
#    bpy.types.Object.hdeProps = PointerProperty(type = HDBProps) 
#    If chose this options we have custom parameters evety object in Scene
        
def unregister(): # Sys unregister classes in system
    for cl in reversed(classes):
        unregister_class(cl)
        
if __name__ == '__main__':
    register() 
