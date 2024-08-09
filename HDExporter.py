import bpy
import pprint
import bmesh
import os
import re
import pathlib
import math
from bpy.types import Operator


from .HDUtils import * # Import some def :

'''
Classes::
    HDExportSingle
    HDExportMotion
    HDExportSkeleton
    HDExportPose
'''

class HDExportSingle(Operator):
    bl_idname = 'object.exportsingle'
    bl_label  = 'Single dmesh export'

    fUnitMultiplier = 32.0
    
    def execute(self, context):

        # Collect and check selected meshes for export
        objectList = []                                 # Null objectList
        for ob in context.scene.objects:                # Get selected "MESH" objects
            if ob.select_get() and ob.type == 'MESH':   #
                objectList.append(ob)                   #
        #print(objectList)                              # Debug print

        '''
        Later here we start <for> for batch export, and in objectList[0] we need change '0' to 'i'
        '''
        
        pName = objectList[0].name                      # Write Active object name
        pMesh = objectList[0].to_mesh()                 # Write object to pMesh
        pObj  = objectList[0]
        print(f'Start object to export: {pName}')      # DebugP rint
        
            
        data_vertices = pMesh.vertices
        data_materials = pMesh.materials
        data_polygons = pMesh.polygons
        #data_uv = pMesh.uv_layers[0]

        # Check skin data  !!!!!!!!!!!!!!!!!!!! Need Refactoring !!!!!!!!!!!!!!!!!!!!
        if pObj.parent != None:
            if pObj.parent.type == 'ARMATURE':
                bSkinData = True
            else:
                bSkinData = False
        else:
            bSkinData = False


        # Calculate Smooth Groups (SG)
        data_SG = pMesh.calc_smooth_groups(use_bitflags=False)  # Calculate smooth groups, 
                                                                # return list with 2 list data
                                                                # [0] = SG list per face index
                                                                # [1] = total count smooth groups
                                                                                                                              
        data_uv = []

        #print(objectList[0].data.uv_layers[0].data)
        for loop in objectList[0].data.uv_layers[0].data:
            data_uv.append(loop.uv)
            #print(loop.uv)
            
        #print('UV List length')
        #print(len(data_uv))
                                                               
        #--------------------------------------------------------------------------------------------
        iVertexCount = len(data_vertices)
        iPolyCount = len(data_polygons)
        iUVsCount = len(data_uv) #len(data_uv.uv)
        iMatGroups = len(data_materials)
        #print(iUVsCount)
        
        print('Start calculate polys groups >>>')
        # Set Smooth Groups data in better container 
        
        SGPolyList = []           # CleanUp
        SGPolyList = data_SG[0]   # Take SG list per face index
        
        # Calculate Material Group (Index of polys) // polyCollectionTotal have len = data_materials
        # Later we can get list of polys index by mtl index
        
        polyCollectionTotal = []        
        for n in range(len(data_materials)):
            tmpMtlIndex = n
            tmpListPolys = []
            polyCollectionTotal.append(tmpListPolys)
            #print(polyCollectionTotal)
            #print(tmpMtlIndex)
            
            for ax in range(len(data_polygons)):
                #print(data_polygons[ax].material_index == tmpMtlIndex)
                if data_polygons[ax].material_index == tmpMtlIndex:
                    #print(data_polygons[ax].index)
                    tmpA = int(data_polygons[ax].index)
                    polyCollectionTotal[tmpMtlIndex].append(tmpA)
                        



        print(SGPolyList)
        print('polyList---------<<<')
        for n in range(len(polyCollectionTotal)):
            print(len(polyCollectionTotal[n]))
        
        #VB = [] # Vertex Block
        #for n in range(len(data_vertices)):
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        
        wdOutputBlock = 'HD_DATA_TXT 300\n\n'
        
        # VERTEX BLOCK <<<<<<<<<<<<<<<<<<<<<<<<<<<<
        wdOutputBlock += 'mesh\n{\n'
        wdOutputBlock += f'\tverts {iVertexCount}'
        wdOutputBlock += '\n\t{\n'
        for n in range(iVertexCount):
                    #print(pMesh.vertices[n].co)    # Debug line
                    tmpPos = pMesh.vertices[n].co  # Get Vector Position value // Take Local pos arount origin
                    #testPenis = pObj.matrix_basis
                    tmpVector = ob.matrix_world @ tmpPos.to_4d()
                    zalupa = tmpVector.to_3d()
                    zalupa = tmpPos * 32.0
                    print(tmpVector)
                    print(tmpPos)
                    print(zalupa)
                    #tmpPos[1] = tmpPos[1] * -1.0
                    tmpX = round(zalupa[0], 5)     # Separate XYZ values and round it
                    tmpY = round(zalupa[1], 5)     #
                    tmpZ = round(zalupa[2], 5)     #
                    wdOutputBlock += f'\t\tvert {tmpX} {tmpZ} {tmpY};\n' # Write position in X->X Y->Y Z->Z, axis flip in exporter here!
                    #print(data_vertices[n].)
                    #print(activeObj.data.vertices[n])
        wdOutputBlock += '\t}\n'  #Endl VertexBlock
        
        # UV Block     <<<<<<<<<<<<<<<<<<<<<<<<<<<< ---------------------------------------------------------------------------------
        uvRAWList = []
        uvCorrectList = []
        uvRedirectIndex = []

        tmpMissCheck = 0

        # Collect RAW uv data
        for loop in objectList[0].data.uv_layers[0].data:
            uvRAWList.append(loop.uv)
            
        # Calculate correct uv list 
        for n in range(len(uvRAWList)):
            
            #ONCE
            if len(uvCorrectList) == 0:
                print('SimpleOne!')
                uvCorrectList.append(uvRAWList[n])
                uvRedirectIndex.append(n)
                continue ### Skip other 'for' body in first time, in this 'if' we add first correct index 
            
            # Check if this uv coord exsist, then add Correct UV index in uvRedirectIndex
            BoolXY = False
            
            for i in range(len(uvCorrectList)):
                
                if math.isclose(uvRAWList[n].x, uvCorrectList[i].x) and math.isclose(uvRAWList[n].y, uvCorrectList[i].y):
                    BoolXY = True
                    tmpMissCheck += 1                     
                    uvRedirectIndex.append(i)
           
            if not BoolXY: 
                uvCorrectList.append(uvRAWList[n])
                uvRedirectIndex.append(len(uvCorrectList) - 1)



        print('------------UV TOTAL------------')  
        print('RawList:')  
        print(len(uvRAWList))  
        print('CorrectList:')  
        print(len(uvCorrectList))
        print('RedirIndexList:')
        print(len(uvRedirectIndex))
        print('Dublicates:')                 
        print(tmpMissCheck)
        print('------------UV TOTAL ENDL------------')  

        iUVsCount = len(uvCorrectList) # Set correct num of uvs
        wdOutputBlock += f'\tuvs {iUVsCount}'
        wdOutputBlock += '\n\t{\n'
        for ax in range(len(uvCorrectList)):
            tmpU = round(uvCorrectList[ax].x, 8)
            tmpV = round(uvCorrectList[ax].y, 8)       
            wdOutputBlock += f'\t\tuv {tmpU} {tmpV};\n'      
        wdOutputBlock += '\t}\n'  #Endl UV Block
        
        ### GROUPS (FACES)      <<<<<<<<<<<<<<<<<<<<<<<<<<<< Materials, polys and Smooth Groups ----------------------------
        
        wdOutputBlock += f'\tgroups {iMatGroups}'
        wdOutputBlock += '\n\t{\n'
        
        for n in range(len(data_materials)):            # Start <for> GROUPS_MATERIAL <<<
            tmpMtlName = data_materials[n].name         # Get name of material for write 'wdOutputBlock +='            
            tmpMtlIndex = n                             # Remove maybe?
            tmpList = polyCollectionTotal[tmpMtlIndex]  # Take list of polys by material index // Maybe 'tmpMtlIndex' dont need
            iPolyCount = len(tmpList)
            
            faceNGon = 0                 # Reset face data to default
            faceVertex = ''              #[]
            faceVertexRaw = []
            faceUV = ''                  #[]
            faceUVraw = []
            faceSG = 0                   # 
            
            #if len(data_materials) == 1: # Depricated Check
            #    tmpMtlName = 'Model'     #
            if tmpMtlName.split('_')[0] == 'surface':  # Remove 'surface' prefix for correct work 'Auto Surface' function in Aurora model component(Importer) 
                tmpMtlName = tmpMtlName.split('_')[1]  # exsample: surface_SurfaceName -> SurfaceName
            
                          
            wdOutputBlock += f'\t\tgroup {tmpMtlName} {iPolyCount}'  # Start Material Group
            wdOutputBlock += '\n\t\t{\n'            
            for ax in range(len(tmpList)):              # Start <for> FACE_LIST in GROUP_MATERIAL <<<
                
                wdOutputBlock += '\t\t\tface\n' # Start face data
                wdOutputBlock += '\t\t\t{\n'
                                
                CurrentPolyIndex = tmpList[ax] # Take Face index from mat group  ^^^
                
                # /// Face Vertex Count Data Collect <-            
                faceNGon = len(data_polygons[CurrentPolyIndex].vertices)
                
                # /// Face Vertex Index Data Collect <-
                for bx in range(faceNGon):
                    if bx == 0:
                        faceVertex = ''
                    faceVertex += f'{data_polygons[CurrentPolyIndex].vertices[bx]}'
                    if bx != faceNGon-1:
                        faceVertex += ' '
                        
                # /// Face UV Data Collect <-
                faceUVraw = []
                GetUVindex = data_polygons[CurrentPolyIndex].loop_start
                #for bx in range(len(data_polygons[CurrentPolyIndex])):                
                for gx in range(data_polygons[CurrentPolyIndex].loop_total):   # Here we get global loops index for current face
                    faceUVraw.append(GetUVindex)
                    #print(GetUVindex)
                    #print(data_uv[GetUVindex])    
                    GetUVindex += 1
                                    
                for i in range(len(faceUVraw)):
                    if i == 0:
                        faceUV = '' #Remove???
                    faceUV += f'{uvRedirectIndex[faceUVraw[i]]}' #<-  uvRedirectIndex   uvCorrectList
                    if i != len(faceUVraw)-1:
                        faceUV += ' '
                 
                # /// Smooth Group Data Collect <-
                faceSG = SGPolyList[CurrentPolyIndex]
                
                # ------------------------------------------------------------------
                
                wdOutputBlock += f'\t\t\t\tcount {faceNGon};\n'
                #wdOutputBlock += ''
                wdOutputBlock += f'\t\t\t\tverts {faceVertex};\n'
                #wdOutputBlock += '\n'
                wdOutputBlock += f'\t\t\t\tuvs {faceUV};\n'
                #wdOutputBlock += '\n'
                wdOutputBlock += f'\t\t\t\tsmoothGroup {faceSG};\n'
                #wdOutputBlock += '\n'
                wdOutputBlock += '\t\t\t}\n' # End face data
                
                
                
            wdOutputBlock += '\t\t}\n' # End current group
            
            #-----------------------------------------------------------------
            
        wdOutputBlock += '\t}\n' # End groups

        ### JOINTS (Bones)      <<<<<<<<<<<<<<<<<<<<<<<<<<<< Joints --------------------------------------------------------
        if bSkinData:
            print('We have skin data')
            pBones = pObj.parent.data.bones

            wdOutputBlock += f'\tjoints {len(pBones)}'
            wdOutputBlock += '\n\t{'

            for i in range(len(pBones)):
                wdOutputBlock += f'\n\t\tjoint {pBones[i].name}'
                wdOutputBlock += '\n\t\t{\n'
                tmpVector = f_ConvertPosition(pBones[i].head_local)
                wdOutputBlock += f'\t\t\torigin {tmpVector[0]} {tmpVector[1]} {tmpVector[2]};'
                wdOutputBlock += '\n'
                tmpQuaternion = f_ConverQuaternion(pBones[i].matrix_local.to_quaternion())  # matrix_local.to_quaternion()
                wdOutputBlock += f'\t\t\taxis {tmpQuaternion[0]} {tmpQuaternion[1]} {tmpQuaternion[2]} {tmpQuaternion[3]};'
                wdOutputBlock += '\n\t\t}'

            # End
            wdOutputBlock += '\n\t}\n'

        ### VERTEX_WEIGHTS      <<<<<<<<<<<<<<<<<<<<<<<<<<<< Vertex, Joint, Value ------------------------------------------

            weightsList = f_CalculateWeights(pObj, pBones)

            wdOutputBlock += f'\tweights {len(weightsList)}'
            wdOutputBlock += '\n\t{'

            for i in range(len(weightsList)):
                wValue = weightsList[i]
                wdOutputBlock += f'\n\t\tweight {wValue[0]} {wValue[1]} {wValue[2]};' #weightsList[i].[0] weightsList[i].[1] weightsList[i].[2] weightsList[i[0]]
            wdOutputBlock += '\n\t}'



        wdOutputBlock += '\n}'   # End mesh
                   
        #bpy.path.abspath
        #path_to_file = pathlib.Path.home() / 'tmp' / 'penis.txt'
        
        #path_to_file = bpy.path.abspath(path_to_file) / 'tmp' / 'penis.txt'
        
        #Correct file path below        
        #tmpBlendPath = pathlib.Path(bpy.data.filepath)                    # Get blender file path
        #path_to_file = str(tmpBlendPath.parent) + '/' + pName + '.dmesh'  # Calculate savePath file to blend file folder
        path_to_file = 'P:/Haydee Interactive/0-dMeshes/BlendTest' + '/' + pName + '.dmesh'

        f_SaveDataToFile(path_to_file, wdOutputBlock)

        '''
        with open(path_to_file, 'w') as pFile:
            #pFile.write('HD_DATA_TXT 300\n\n')
            HDData = wdOutputBlock
            #HDData = '11111Test!'
            pFile.write(HDData)
            #HDData = str(len(data_vertices))
            #pFile.write(HDData)
        '''

        return {'FINISHED'}
    
#-------Add later export bones staff------
    
class HDExportMotion(Operator):
    bl_idname = 'object.exportmotion'
    bl_label  = 'Motion export'
    
    def execute(self, context):
        bpy.ops.object.metaball_add(type='BALL', radius=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        return {'FINISHED'}
    
        
class HDExportSkeleton(Operator):
    bl_idname = 'object.exportskeleton'
    bl_label  = 'Skeleton export'
    
    def execute(self, context):
        #bpy.ops.object.metaball_add(type='CAPSULE', enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

        # PREPARE BLOCK <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        # Collect and check selected meshes for export


        objectList = []                                 # Null objectList
        for ob in context.scene.objects:                # Get selected "MESH" objects
            if ob.select_get() and ob.type == 'MESH':   #
                objectList.append(ob)                   #
        #print(objectList)                              # Debug print

        # TODO Checks if(Armature)

        pName = objectList[0].name
        pObj = objectList[0]
        pBones = pObj.parent.data.bones

        path_to_file = 'P:/Haydee Interactive/0-dMeshes/BlendTest' + '/' + pName + '.dskel'

        # SKELETON DATA BLOCK <<<<<<<<<<<<<<<<<<<<<<<<<<<<
        ExportData = 'HD_DATA_TXT 300\n\n' # Start file
        ExportData += f'skeleton {len(pBones)}'
        ExportData += '\n{'
        # ---

        for i in range(len(pBones)):

            ExportData += f'\n\tbone {pBones[i].name}'
            ExportData += '\n\t{'

            fSideMetrics = round(pBones[i].head_radius, 4) * 32.0
            fBoneLength = round(pBones[i].length, 4) * 32.0

            ExportData += f'\n\t\twidth {fSideMetrics};'
            ExportData += f'\n\t\theight {fSideMetrics};'
            ExportData += f'\n\t\tlength {fBoneLength};'

            if(pBones[i].parent):
                ExportData += f'\n\t\tparent {pBones[i].parent.name};'

            tmpVector = f_ConvertPosition(pBones[i].head_local)
            ExportData += f'\n\t\torigin {tmpVector[0]} {tmpVector[1]} {tmpVector[2]};'

            #matrix_local.to_quaternion()
            tmpQuaternion = f_ConverQuaternion(pBones[i].matrix_local.to_quaternion())
            ExportData += f'\n\t\taxis {tmpQuaternion[0]} {tmpQuaternion[1]} {tmpQuaternion[2]} {tmpQuaternion[3]};'


            '''
            width 3.0;
		    height 3.0;
		    length 24.3013;
		    parent SK_Root;
		    origin 2.39171e-07 0.0 0.0;
		    axis 0.0 0.0 0.707107 -0.707107;
            '''

            ExportData += '\n\t}'

        # ---
        ExportData += '\n}'  # End file

        f_SaveDataToFile(path_to_file, ExportData)
        return {'FINISHED'}
    
    
class HDExportPose(Operator):
    bl_idname = 'object.exportpose'
    bl_label  = 'Pose export'
    
    def execute(self, context):
        fTest()
        bpy.ops.object.metaball_add(type='PLANE', enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        return {'FINISHED'}