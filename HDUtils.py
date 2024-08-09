import bpy
import math
import mathutils
from mathutils import Quaternion, Vector, Matrix
from math import radians, pi

#def fTest(self, context):
def fTest():
    print('fTest from HDUtils')
    
def f_GedBones():
    print('GetBones')
    return 1

def f_RestoreRecentFilePath():
    pass

def f_ConvertPosition(tmpVector):
    '''
    Conver to HDAurora units, flip y/z axis, round position
    '''

    fUnitMultiplier = 32.0
    iRoundFactor = 5

    '''
    tmpVector * fUnitMultiplier                        # Convert to HDAurora units
    tmpValue = round(tmpVector[1], iRoundFactor)       # Save 'y' value
    tmpVector[1] = round(tmpVector[2], iRoundFactor)   # Put 'z' into 'y'
    tmpVector[2] = tmpValue                            # Put 'y' into 'z' Flip complete
    tmpValue[0] = round(tmpVector[0], iRoundFactor)    # Round last X value
    '''

    valueX = round(tmpVector[0], iRoundFactor) * fUnitMultiplier
    valueY = round(tmpVector[1], iRoundFactor) * fUnitMultiplier
    valueZ = round(tmpVector[2], iRoundFactor) * fUnitMultiplier
    tmpVector = None
    tmpVector = []
    tmpVector.append(valueX)
    tmpVector.append(valueZ)
    tmpVector.append(valueY)

    return tmpVector                                   #

def f_ConverQuaternion(tmpQuaternion):
    # Blender  w, x, y, z
    # HDAurora x y z w
    # Y - Z Flipped
    # TODO remove Round()
    iRoundFactor = 7
    bRoundQuat = False


    # Old Code
    tmpFixA = Quaternion([1, 0, 0], radians(90))  # tmpFixA = Quaternion([0, 0, 1], -pi / 2)
    tmpFixB = Quaternion([0, 1, 0], radians(-90))
    tmpFixC = Quaternion([0, 0, 1], radians(-180))

    #tmpQuaternion = ( tmpQuaternion @ tmpFixA )
    #tmpQuaternion = ( tmpQuaternion @ tmpFixB )

    #
    tmpQuaternion = tmpQuaternion @ tmpFixA
    tmpQuaternion = tmpQuaternion @ tmpFixB
    tmpQuaternion = tmpFixC @ tmpQuaternion
    #tmpQuaternion = tmpQuaternion @ Quaternion([1, 0, 0], radians(180)) # P#%E&



    #tmpFixA = Quaternion([0, 1, 0], radians(90))  # tmpFixA = Quaternion([0, 0, 1], -pi / 2)
    #tmpFixB = Quaternion([1, 0, 0], radians(-90))

    #tmpQuaternion = (tmpQuaternion @ tmpFixA)
    #tmpQuaternion = (tmpQuaternion @ tmpFixB)







    if bRoundQuat:
        valueW = -round(tmpQuaternion.w, iRoundFactor)
        valueX = round(tmpQuaternion.x, iRoundFactor)
        valueY = round(tmpQuaternion.y, iRoundFactor)
        valueZ = -round(tmpQuaternion.z, iRoundFactor)
    else:
        valueW = -tmpQuaternion.w
        valueX = tmpQuaternion.x
        valueY = tmpQuaternion.y
        valueZ = -tmpQuaternion.z


    tmpQuaternion = None
    tmpOutQuat = []

    tmpOutQuat.append(valueX)
    tmpOutQuat.append(valueZ)  # * -1.0
    tmpOutQuat.append(valueY)
    tmpOutQuat.append(valueW)  # * -1.0


    #Old ver
    '''
    valueW = round(tmpQuaternion[0] * -1.0, iRoundFactor)
    valueX = round(tmpQuaternion[1], iRoundFactor)
    valueY = round(tmpQuaternion[2], iRoundFactor)
    valueZ = round(tmpQuaternion[3], iRoundFactor)
    tmpQuaternion = None
    tmpQuaternion = []
    tmpQuaternion.append(valueX)
    tmpQuaternion.append(valueY)
    tmpQuaternion.append(valueZ)
    tmpQuaternion.append(valueW)
    '''


    return tmpOutQuat

def f_GetVertexGroupIndex():
    '''
    Return index for function, where we get skin value for vertex (in range current joint )
    '''

    pass


def f_CalculateWeights(pObj, pBones):

    #
    #pObj.vertex_groups[i].name
    # Calculate vertex indexes per joints ----------------------------

    #weightsList = []



    jointsList = []
    weightsList = []

    for ax in range(len(pObj.vertex_groups)):

        bpy.ops.object.editmode_toggle()
        bpy.ops.object.vertex_group_set_active(group=pObj.vertex_groups[ax].name)  # group = pObj.vertex_groups[ax].name
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.vertex_group_select()
        bpy.ops.object.editmode_toggle()  # Important toggle edit mode back for update select data 'pObj.data.vertices[bx].select'

        for i in range(len(pBones)):   # Set correct joint index, when we don't have equal order vertex_groups
            if pObj.vertex_groups[ax].name == pBones[i].name:
                tmpCurJointIndex = i
                break
                #print('GroupName = JointName')

        vertexGroup = []

        for bx in range(len(pObj.data.vertices)): # Store vertex in joint/vertex group
            if pObj.data.vertices[bx].select:
                vertexGroup.append(bx)

        if len(vertexGroup) == 0: # Break loop if no vertex weight data
            continue



        for cx in range(len(vertexGroup)):
            wData = []
            tmpCurVertexGroupIndex = 0

            for i in range(len(pObj.data.vertices[vertexGroup[cx]].groups)):
                print(pObj.data.vertices[vertexGroup[cx]].groups[i].group)

                if pObj.data.vertices[vertexGroup[cx]].groups[i].group == pObj.vertex_groups[ax].index: #     pBones[tmpCurJointIndex].name
                    tmpCurVertexGroupIndex = i

            vertexIndex = vertexGroup[cx]
            jointIndex = tmpCurJointIndex
            skinValue = pObj.data.vertices[vertexGroup[cx]].groups[tmpCurVertexGroupIndex].weight

            wData = [vertexIndex, jointIndex, skinValue]
            weightsList.append(wData)



    print(f'Num Weights: {len(weightsList)}')






    # End calculate vertex indexes per joints ------------------------
    '''
    # Debug cout::
    debugCountWeights = 0
    for i in range(len(jointsList)):
        debugCountWeights + len(jointsList[i])
    print(f'Count Weights: {debugCountWeights}')
    #print(jointsList[0])
    #print(jointsList[1])
    #print(jointsList[2])
    #print(jointsList[3])
    #print('------------------------------')

    # Generate weight data for export -----------

    weightsList = []

    for ax in range(len(jointsList)):

        tmpVertexGroup = jointsList[ax]
        tmpVertexGroupName = 0 #pObj.vertex_groups[ax].index        #pObj.vertex_groups[ax]


        for bx in range(len(tmpVertexGroup)):
            wValue = []
            print(tmpVertexGroup[bx])
            wValue.append(  str(tmpVertexGroup[bx])    )
            wValue.append(  str(ax)   )
            wValue.append(  str( pObj.data.vertices[tmpVertexGroup[bx]].groups[tmpVertexGroupName].weight )   )
            print(str( pObj.data.vertices[tmpVertexGroup[bx]].groups[tmpVertexGroupName].weight ))

            weightsList.append(wValue)




    print(len(weightsList))

    # --------------------------------------------------
    
    

    for ax in range(len(pObj.vertex_groups)):
        
    
    
    
    
    weightsList.append(wValue)





    Как работает передача данных в функцию???
    
    Bones or vertex_groups some times not equal, and for this we need
    На каждую кость список вершин, если у кости нету вершин то ее скипаем ( не вносим в список )

    
    vGroupName = pObj.vertex_groups[0].name
    
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.vertex_group_set_active(group = vGroupName)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.vertex_group_select()
    print('---------')
    print(pObj.data.vertices[0].select)


    vertexIndex
    jointIndex



    joints vertexs -> Values


    print(pObj.data.vertices[2].groups[1].group)
    print(pObj.data.vertices[2].groups[1].weight)

    weightsList = []
    for i in range(len(tmpList))
        wValue = []
        wValue.append(vertexIndex)
        wValue.append(jointIndex)
        wValue.append(skinValue)
        weightsList.append(wValue)
    
    
    


    :return:
    '''
    return weightsList






def f_SaveDataToFile(tmpFilePath, HDData):
    with open(tmpFilePath, 'w') as pFile:
        pFile.write(HDData)