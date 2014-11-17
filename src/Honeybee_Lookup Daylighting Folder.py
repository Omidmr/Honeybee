# By Mostapha Sadeghipour Roudsari
# Sadeghipour@gmail.com
# Honeybee started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Search Simulation Folder
-
Provided by Honeybee 0.0.55
    
    Args:
        studyFolder: Path to study folder
        refresh: Refresh the list
    Returns:
        resFiles: List of result files from grid based analysis
        illFiles: List of ill files from annual analysis
        ptsFiles: List of point files
        hdrFiles: List of hdr files
        gifFiles: List of gif files
        
"""

ghenv.Component.Name = "Honeybee_Lookup Daylighting Folder"
ghenv.Component.NickName = 'LookupFolder_Daylighting'
ghenv.Component.Message = 'VER 0.0.55\nNOV_16_2014'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "04 | Daylight | Daylight"
#compatibleHBVersion = VER 0.0.55\nAUG_25_2014
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "4"
except: pass

import scriptcontext as sc
import os
import System
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
from pprint import pprint

def main(studyFolder):
    msg = str.Empty
    
    if not (sc.sticky.has_key('ladybug_release')and sc.sticky.has_key('honeybee_release')):
        msg = "You should first let Ladybug and Honeybee fly..."
        return msg, None

    try:
        if not sc.sticky['honeybee_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Honeybee to use this compoent." + \
        " Use updateHoneybee component to update userObjects.\n" + \
        "If you have already updated userObjects drag Honeybee_Honeybee component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1

    try:
        if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
    except:
        warning = "You need a newer version of Ladybug to use this compoent." + \
        " Use updateLadybug component to update userObjects.\n" + \
        "If you have already updated userObjects drag Ladybug_Ladybug component " + \
        "into canvas and try again."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, warning)
        return -1
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    hb_serializeObjects = sc.sticky["honeybee_SerializeObjects"]
    
    if studyFolder==None:
        msg = " "
        return msg, None
        
    if not os.path.isdir(studyFolder):
        msg = "Can't find " + studyFolder
        return msg, None
        
    resFiles = []
    illFilesTemp = []
    ptsFiles = []
    hdrFiles = []
    gifFiles = []
    tifFiles = []
    bmpFiles = []
    jpgFiles = []
    epwFile = str.Empty
    analysisType = str.Empty
    analysisMesh = []
    
    radianceFiles = []
    materialFiles = []
    dgpFiles = []
    skyFiles = []
    octFiles = []
    
    if studyFolder!=None:
        fileNames = os.listdir(studyFolder)
        fileNames.sort()
        for fileName in fileNames:
            if fileName.lower().endswith(".res"):
                resFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".ill") and (fileName.find("space")== -1 or fileName.split("_")[-2]!="space"):
                illFilesTemp.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".pts") and (fileName.find("space")== -1 or fileName.split("_")[-2]!="space"):
                ptsFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".epw"):
                epwFile = os.path.join(studyFolder, fileName)
            elif fileName.lower().endswith(".hdr") or fileName.lower().endswith(".pic"):
                hdrFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".gif"):
                gifFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".oct"):
                octFiles.append(os.path.join(studyFolder, fileName))            
            elif fileName.lower().endswith(".tif") or fileName.lower().endswith(".tiff"):
                tifFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".bmp"):
                bmpFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".jpg") or fileName.lower().endswith(".jpeg"):
                jpgFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".rad") and not fileName.lower().startswith("daysim_"):
                if fileName.lower().startswith("material_"):
                    materialFiles.append(os.path.join(studyFolder, fileName))
                else:
                    radianceFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".sky"):
                skyFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".typ"):
                with open(os.path.join(studyFolder, fileName), "r") as typf:
                    analysisType = typf.readline().strip()
            elif fileName.lower().endswith(".dgp"):
                dgpFiles.append(os.path.join(studyFolder, fileName))
            elif fileName.lower().endswith(".msh"):
                try:
                    meshFilePath = os.path.join(studyFolder, fileName)
                    serializer = hb_serializeObjects(meshFilePath)
                    serializer.readFromFile()
                    analysisMesh = lb_preparation.flattenList(serializer.data)
                except:
                    pass
    
    # check if there are multiple ill files in the folder for different shading groups
    illFilesDict = {}
    
    for fullPath in illFilesTemp:
        fileName = os.path.basename(fullPath)
        
        if fileName.split("_")[:-1]!= []:
            if fileName.endswith("_down.ill") or fileName.endswith("_up.ill"):
                # conceptual blind
                gist = "_".join(fileName.split("_")[:-2]) + "_" + fileName.split("_")[-1]
            elif fileName.Contains("_state_"):
                # dynamic blinds with several states
                gist = "_".join(fileName.split("_")[:-3]) + "_" + fileName.split("_")[-1]
            else:
                gist = "_".join(fileName.split("_")[:-1])
                
        else:
            gist = fileName
            
        if gist not in illFilesDict.keys():
            illFilesDict[gist] = []
        illFilesDict[gist].append(fullPath)
    
    # sort the lists
    #try:
    illFiles = DataTree[System.Object]()
    for listCount, fileListKey in enumerate(illFilesDict.keys()):
        p = GH_Path(listCount)
        fileList = illFilesDict[fileListKey]
        try:
            if fileName.endswith("_down.ill") or fileName.endswith("_up.ill"):
                # conceptual blind
                if fileList[0].endswith("_down.ill"):
                    p = GH_Path(1)
                else:
                    p = GH_Path(0)
                
                illFiles.AddRange(sorted(fileList, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-2])), p)
            else:
                illFiles.AddRange(sorted(fileList, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1])), p)
        except:
            illFiles.AddRange(fileList, p)
            
    
    #except: pass
    try: resFiles = sorted(resFiles, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
    except: pass
    try: ptsFiles = sorted(ptsFiles, key=lambda fileName: int(fileName.split(".")[-2].split("_")[-1]))
    except: pass
    
    imgFiles = gifFiles + tifFiles + bmpFiles + jpgFiles
    
    return msg, [illFiles, resFiles, ptsFiles, hdrFiles, imgFiles, epwFile, \
           analysisType, analysisMesh, radianceFiles, materialFiles, skyFiles, \
           dgpFiles, octFiles]
    

ghenv.Component.Params.Output[1].NickName = "resultFiles"
ghenv.Component.Params.Output[1].Name = "resultFiles"
resultFiles = []

res = main(studyFolder)

if res != -1:
    msg, results = res
    
    if msg!=str.Empty:
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, msg)
    else:
        illFiles, resFiles, ptsFiles, hdrFiles, imageFiles, epwFile, analysisType, \
        analysisMesh, radianceFiles, materialFiles, skyFiles, dgpFiles, octFiles = results
    
        if resFiles != []:
            resultFiles = resFiles
        else:
            resultFiles = illFiles
            filesOutputName = "illFiles"
            ghenv.Component.Params.Output[1].NickName = filesOutputName
            ghenv.Component.Params.Output[1].Name = filesOutputName
            exec(filesOutputName + "= resultFiles")
