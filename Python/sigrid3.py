#from __future__ import print_function        # dies wechselt print ohne klammern zu print()
#from __future__ import unicode_literals      # dies macht Textstrings in python2 zu unicode

import os
import s411objects

import geopandas as gp
import pandas as pd
import fiona
def multi2single(gpdf):  # probably not needed anymore, as we can use gp.explode
    gpdf_singlepoly = gpdf[gpdf.geometry.type == 'Polygon']
    gpdf_multipoly = gpdf[gpdf.geometry.type == 'MultiPolygon']

    for i, row in gpdf_multipoly.iterrows():
        Series_geometries = pd.Series(row.geometry)
        df = pd.concat([gp.GeoDataFrame(row, crs=gpdf_multipoly.crs).T]*len(Series_geometries), ignore_index=True)
        df['geometry']  = Series_geometries
        gpdf_singlepoly = pd.concat([gpdf_singlepoly, df])

    gpdf_singlepoly.reset_index(inplace=True, drop=True)
    return gpdf_singlepoly


def sigrid3ToS411Objects(shpFile):
    
    s411SeaIceFeatureList = []
    
    shpFile = os.path.normpath(shpFile)    
    #####################################################
    # Multipart to Singlepart, because s411 does not support multigeometries
    gpdf = gp.read_file(shpFile)
    #singlegpdf=multi2single(gpdf)
    singlegpdf=gpdf.explode(index_parts=True)   # try to convert to single usinf explode, which seeems to work fine
    singleShpFile='temp_single.shp'
    singlegpdf.to_file(singleShpFile)
    

    iceapc = None   
        
    # Iterate trough icearea featues and put into S-411 Objects
    with fiona.open(singleShpFile) as IAreas:
        if IAreas.schema['geometry'] != 'Polygon': 
            print('error')   # oder type anstatt gemetry??
            return s411SeaIceFeatureList
        #CoordinateReference=IAreas.crs
        #IAbounds=IAreas.bounds
        #IAproperties=IAreas.schema['properties']
        known_sigrid3=['AREA','PERIMETER','POLY_TYPE',
                       'CT','CA','CB','CC','SA','SB','SC','FA','FB','FC',
                       'CN','CD']
        for jj in IAreas.schema['properties']: 
            if jj.upper() not in known_sigrid3:
                print('unknown Sigrid3-property:',jj)
    
        for IArow in IAreas:
            row=IArow['properties']
            # we just process polygons with sea ice or ice of land origin 
            try:
              if not ( row['POLY_TYPE']=='I' or row['POLY_TYPE']=='S'  ): continue
            except:
              pass

            # Create seaice object
            # not all things are handeld up till now
            # missing CF and all optional objects
            s411SeaIceFeature = s411objects.Seaice()

            #geometry = row.getValue(geomFieldName).WKT #üüüüüüüüüüüüüüüü
            geometry=IArow['geometry']   #['coordinates']
            #feature id for gml
            fid = IArow['id']
            if fid is not None:
                s411SeaIceFeature.set_gml_id(fid)
        
            # ICEACT from CT
            ct = None
            if 'CT' in row:
                try:
                    ct = int(row['CT'])
                except:
                    ct = 99
                if ct<0:
                    ct=99
                elif ct<=3:
                    ct=ct+1
             
            # ICEAPC from CA,CB,CC
            iceapc = None 
            if 'CA' in row:
                try:
                   iceapc = [ int(row['CA']) ]
                except:
                   iceapc = [ 99]
                if 'CB' in row:
                    try:
                        iceapc.append( int(row['CB']) )
                    except:
                        iceapc.append( 99 )
                    if 'CC' in row:
                        try:
                            iceapc.append( int(row['CC']) )
                        except:
                            iceapc.append( 99 )
                for ii in range(len(iceapc)):
                    if iceapc[ii]<0:
                        iceapc[ii]=99
                    elif iceapc[ii]<=3:
                        iceapc[ii]=iceapc[ii]+1

            # ICESOD
            icesod = None
            if 'SA' in row:
                try:
                    icesod = [ int(row['SA']) ]
                except:
                    icesod = [ 99 ]
                if 'SB' in row:
                    try:
                        icesod.append( int(row['SB']) )
                    except:
                        icesod.append( 99 )
                    if 'SC' in row:
                        try: 
                            icesod.append( int(row['SC']) )
                        except:
                            icesod.append( 99 )
                for ii in range(len(icesod)):
                    if icesod[ii]<0:
                        icesod[ii]=99
                    elif icesod[ii]<1:
                        icesod[ii]=icesod[ii]+1
            # ICEFLZ
            iceflz = None
            if 'FA' in row:
                try:
                    iceflz = [ int(row['FA']) ]
                except:
                    iceflz = [ 99 ]
                if 'FB' in row:
                    try:
                        iceflz.append( int(row['FB']) )
                    except:
                        iceflz.append( 99 )
                    if 'FC' in row:
                        try:
                            iceflz.append( int(row['FC']) )
                        except:
                            iceflz.append( 99 )
                for ii in range(len(iceflz)):
                    if iceflz[ii]<0:
                        iceflz[ii]=99
                    elif iceflz[ii]<11:
                        iceflz[ii]=iceflz[ii]+1
                    else:
                        iceflz[ii]=99

                
            CNCD = None
            if 'CN' in row:
                try:
                    CNCD = [ int(row['CN']) ]
                except:
                    CNCD = [ 99 ]
                for ii in range(len(CNCD)):
                    if CNCD[ii]<0:
                        CNCD[ii]=99
                    elif CNCD[ii]<=3:
                        CNCD[ii]=CNCD[ii]+1
                    if CNCD[ii] != 99:
                        iceapc.insert(0,2)
                        icesod.insert(0,CNCD[ii])
                        iceflz.insert(0,99)
                        
            if 'CD' in row:
                try:
                    CNCD = [ int(row['CD']) ]
                except:
                    CNCD = [ 99 ]
                for ii in range(len(CNCD)):
                    if CNCD[ii]<0:
                        CNCD[ii]=99
                    elif CNCD[ii]<=3:
                        CNCD[ii]=CNCD[ii]+1
                    if CNCD[ii] != 99:
                        iceapc.append(2)
                        icesod.append(CNCD[ii])
                        iceflz.append(99)
                        
            if ct is not None:
                s411SeaIceFeature.set_iceact(ct)
            if iceapc is not None:
                s411SeaIceFeature.set_iceapc(iceapc)
            if icesod is not None:
                s411SeaIceFeature.set_icesod(icesod)
            if iceflz is not None:
                s411SeaIceFeature.set_iceflz(iceflz)

            #  ia_sfa fro ca,cb,cc
                 
            # geometry as WKT to seaice feature
            
            if geometry is not None:
                s411SeaIceFeature.set_geometry(geometry)
                    
            s411SeaIceFeatureList.append(s411SeaIceFeature)
        
    return s411SeaIceFeatureList
                    
                    

def sigrid3ToS411ObjectsN(gpdf):
    
    s411SeaIceFeatureList = []
    
   #####################################################
    # Multipart to Singlepart, because s411 does not support multigeometries
    #singlegpdf=multi2single(gpdf)
    singlegpdf=gpdf.explode(index_parts=True)   # try to convert to single usinf explode, which seeems to work fine

    iceapc = None   
        
    for g,row in singlegpdf.iterrows():
        if row['geometry'].geom_type != 'Polygon': continue
        if 'POLY_TYPE' in row:
          if not ( row['POLY_TYPE']=='I' or row['POLY_TYPE']=='S'  ): continue
    
        # Create seaice object
        # not all things are handeld up till now
        # missing CF and all optional objects
        s411SeaIceFeature = s411objects.Seaice()
    
        #geometry 
        geometry=row['geometry']   #['coordinates']
        #feature id for gml
        if 'id' in row:
            fid = row['id']
            if fid is not None:
                s411SeaIceFeature.set_gml_id(fid)
    
        # ICEACT from CT
        ct = None
        if 'CT' in row:
            try:
                ct = int(row['CT'])
            except:
                ct = 99
            if ct<0:
                ct=99
            elif ct<=3:
                ct=ct+1
         
        # ICEAPC from CA,CB,CC
        iceapc = None 
        if 'CA' in row:
            try:
               iceapc = [ int(row['CA']) ]
            except:
               iceapc = [ 99]
            if 'CB' in row:
                try:
                    iceapc.append( int(row['CB']) )
                except:
                    iceapc.append( 99 )
                if 'CC' in row:
                    try:
                        iceapc.append( int(row['CC']) )
                    except:
                        iceapc.append( 99 )
            for ii in range(len(iceapc)):
                if iceapc[ii]<0:
                    iceapc[ii]=99
                elif iceapc[ii]<=3:
                    iceapc[ii]=iceapc[ii]+1
    
        # ICESOD
        icesod = None
        if 'SA' in row:
            try:
                icesod = [ int(row['SA']) ]
            except:
                icesod = [ 99 ]
            if 'SB' in row:
                try:
                    icesod.append( int(row['SB']) )
                except:
                    icesod.append( 99 )
                if 'SC' in row:
                    try: 
                        icesod.append( int(row['SC']) )
                    except:
                        icesod.append( 99 )
            for ii in range(len(icesod)):
                if icesod[ii]<0:
                    icesod[ii]=99
                elif icesod[ii]<1:
                    icesod[ii]=icesod[ii]+1
        # ICEFLZ
        iceflz = None
        if 'FA' in row:
            try:
                iceflz = [ int(row['FA']) ]
            except:
                iceflz = [ 99 ]
            if 'FB' in row:
                try:
                    iceflz.append( int(row['FB']) )
                except:
                    iceflz.append( 99 )
                if 'FC' in row:
                    try:
                        iceflz.append( int(row['FC']) )
                    except:
                        iceflz.append( 99 )
            for ii in range(len(iceflz)):
                if iceflz[ii]<0:
                    iceflz[ii]=99
                elif iceflz[ii]<11:
                    iceflz[ii]=iceflz[ii]+1
                else:
                    iceflz[ii]=99
    
            
        CNCD = None
        if 'CN' in row:
            try:
                CNCD = [ int(row['CN']) ]
            except:
                CNCD = [ 99 ]
            for ii in range(len(CNCD)):
                if CNCD[ii]<0:
                    CNCD[ii]=99
                elif CNCD[ii]<=3:
                    CNCD[ii]=CNCD[ii]+1
                if CNCD[ii] != 99:
                    iceapc.insert(0,2)
                    icesod.insert(0,CNCD[ii])
                    iceflz.insert(0,99)
                    
        if 'CD' in row:
            try:
                CNCD = [ int(row['CD']) ]
            except:
                CNCD = [ 99 ]
            for ii in range(len(CNCD)):
                if CNCD[ii]<0:
                    CNCD[ii]=99
                elif CNCD[ii]<=3:
                    CNCD[ii]=CNCD[ii]+1
                if CNCD[ii] != 99:
                    iceapc.append(2)
                    icesod.append(CNCD[ii])
                    iceflz.append(99)
                    
        if ct is not None:
            s411SeaIceFeature.set_iceact(ct)
        if iceapc is not None:
            s411SeaIceFeature.set_iceapc(iceapc)
        if icesod is not None:
            s411SeaIceFeature.set_icesod(icesod)
        if iceflz is not None:
            s411SeaIceFeature.set_iceflz(iceflz)
    
        #  ia_sfa fro ca,cb,cc
             
        # geometry as WKT to seaice feature
        
        if geometry is not None:
            s411SeaIceFeature.set_geometry(geometry)
                
        s411SeaIceFeatureList.append(s411SeaIceFeature)
    
    return s411SeaIceFeatureList
                    
                    
