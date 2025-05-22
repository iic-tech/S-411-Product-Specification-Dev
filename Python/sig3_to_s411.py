# -*- coding: UTF-8 -*-
#
# !!!

import datetime
import geopandas as gp
from sigrid3 import sigrid3ToS411ObjectsN as sigrid3ToS411Objects
import s411metadatanew as s411metadata
from s411 import s411ObjectsToGml,createS411DataSet,createS411ExchangeSet,zipdir
from s411 import s411_readshape
import zipfile
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from pyproj import CRS,Transformer

"""
     Parameters
     ----------
     Datei : full path to the Sigrid-3 File (extension will be skipped) 
         as string or Path
    
     Returns
     -------
     None.
    
     The S411 output is written in the same directory as the input file with an 
     "S411_" in front of the Sigrid-3 Filename
"""  



def s3_to_s411(Datei):
     if type(Datei) == str: 
         Datei=Path(Datei)
     filename = Datei.name
     ICEshape = filename.split(".")[0]
     metadatafile=Path(Datei.parent,ICEshape+'.xml')
     N_411='S411_'+ICEshape
     
     InPath=Datei.parent
     OutPath=Datei.parent   # Outputpath equals inputpath
     if (OutPath/Path(N_411+'.zip')).exists(): return  # S411 File already present
     heute=datetime.datetime.today()
     laufzeit=datetime.datetime.now().strftime('%Y/%m/%d %H:%M ')
     print(laufzeit+' Starting S411 chart production:'+N_411)
    
     # Sigrid3 file naming convention:
     # organization-code_region-name_yyyymmddd_feature-type_version.ext
     # Get Template out of Organization if needed
     # but first place to search is in the Inputfile directory
     Org=filename.split('_')[0]
     ECtemplate=Datei.with_name("ecTemplate.xml")
     if not ECtemplate.exists():
         ECtemplate=Datei.with_name("ecTemplate"+Org+".xml")
     if not ECtemplate.exists():
         ECtemplate=Datei.parent.with_name("ecTemplate"+Org+".xml")
     if not ECtemplate.exists():
         sys.exit('No ECtemplate found')
     MDtemplate=Datei.with_name("mdTemplate.xml")
     if not MDtemplate.exists():
         MDtemplate=Datei.with_name("mdTemplate"+Org+".xml")
     if not MDtemplate.exists():
         MDtemplate=Datei.parent.with_name("mdTemplate"+Org+".xml")
     if not MDtemplate.exists():
         print(MDtemplate)
         sys.exit('No MDtemplate found')
     
  
     # get metadata out of metadatafile if the file exists
     # else try differently
     # Publication date for datestamp (or root.findall('.//timeinfo/*caldate') ??)
     try:
         tree = ET.parse(metadatafile)
         root = tree.getroot()
         q=root.findall('.//citation/*pubdate')
         datum1 = datetime.datetime.strptime(q[0].text,"%Y%m%d")
     except:
         datum1 = datetime.datetime(1900,1,1)    
     
     # Sigrid3 file naming convention:
     # organization-code_region-name_yyyymmddd_feature-type_version.ext
     try: 
         JDATUM=filename.split('_')[2]
         datum2 = datetime.datetime.strptime(JDATUM[0:8],"%Y%m%d")
     except:
         dumy=ICEshape.find('_20')
         JDATUM=ICEshape[dumy+1:dumy+9]
         datum2 = datetime.datetime.strptime(JDATUM,"%Y%m%d")
     if datum1==datum2:
        datum=datum1
     else:
         print('Different Publication dates:',datum1,' and ',datum2)
         if datum1-heute > datum2-heute:
             datum=datum1
         else:
             datum=datum2
             print('taking date nearest to today:',datum)
     dateStamp0=datum.strftime("%Y%m%d")
     dateStampS=datum.strftime("%Y%m%d")
     dateStampE=(datum + datetime.timedelta(days=5)).strftime("%Y%m%d")
     
     try:
         IArea=s411_readshape(Path(InPath,ICEshape+'.shp'))        
         extent = IArea.WGS84extent
         S411epsg = IArea.crs.to_epsg()

         s411FeatureList = sigrid3ToS411Objects(IArea)
         s411FeatureElementsList = s411ObjectsToGml(s411FeatureList,S411epsg=S411epsg)
         datasetTree = createS411DataSet(s411FeatureElementsList)
 
         metadataTree = s411metadata.getS411MetadataFromTemplate(MDtemplate, N_411, dateStamp0,
                     extent, dateStampS, dateStampE)
         # the S411 directory structure is written to the subdirectory with the icearea
         createS411ExchangeSet(OutPath, N_411, datasetTree, metadataTree)

         exchangeCatalogueTree = s411metadata.getS411ExchangeCatalogueFromTemplate(ECtemplate,
                     metadataTree, N_411, N_411 + ".gml", extent, 
                     OutPath/Path(N_411)/Path("data")/Path(N_411 + ".gml"))
         exchangeCatalogueTree.write(Path(OutPath,N_411,"catalogue.xml"), 
                     encoding ='utf-8', xml_declaration=True)
         # a S411-zipfile is written to the chartdirectory =dirPath
         dumy=Path(OutPath, N_411)
         zf = zipfile.ZipFile(dumy.with_suffix('.zip'), mode='w')
         zipdir(dumy,zf)
         zf.close()
         return dumy
     except:
         print(sys.exc_info()[0])
         print(laufzeit+"Error in the S411 Production")
#end of S411 production
