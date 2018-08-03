### Dr. Komo

from qgis.core import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
import processing
from processing.core.Processing import Processing
import os


class county_vector_aggregate(QgsProcessingAlgorithm):
    
    # Init
    
    abbr_state_dict = {
        'WY': 'wyoming',
        'WV': 'westvirginia', 
        'WA': 'washington', 
        'WI': 'wisconsin', 
        'VT': 'vermont', 
        'VA': 'virginia', 
        'UT': 'utah', 
        'SD': 'southdakota', 
        'TX': 'texas', 
        'SC': 'southcarolina', 
        'RI': 'rhodeisland', 
        'PA': 'pennsylvania', 
        'OR': 'oregon',
        'NY': 'newyork', 
        'OK': 'oklahoma', 
        'OH': 'ohio', 
        'NV': 'nevada', 
        'NM': 'newmexico', 
        'NJ': 'newjersey', 
        'NH': 'newhampshire', 
        'NE': 'nebraska', 
        'ND': 'northdakota', 
        'MT': 'montana', 
        'MO': 'missouri', 
        'NC': 'northcarolina', 
        'MS': 'mississippi', 
        'MI': 'michigan', 
        'MN': 'minnesota', 
        'ME': 'maine', 
        'MA': 'massachusetts', 
        'KY': 'kentucky', 
        'LA': 'louisiana', 
        'KS': 'kansas', 
        'IN': 'indiana', 
        'ID': 'idaho', 
        'IL': 'illinois', 
        'IA': 'iowa', 
        'GA': 'georgia', 
        'FL': 'florida', 
        'DE': 'delaware', 
        'DC': 'dc', 
        'CT': 'connecticut', 
        'CO': 'colorado', 
        'CA': 'california', 
        'AZ': 'arizona', 
        'AR': 'arkansas', 
        'AL': 'alabama', 
        'MD': 'maryland'
    }

    Processing.initialize()
    feedback = QgsProcessingFeedback()
    
    field = 'nccpi2cs'
    
    # Interate over every state.
    for state_abbr in abbr_state_dict:
        state_name = abbr_state_dict[state_abbr]
        
        # Skip states that have been processed previously.
        if os.path.exists('F:/DoA Modeling/DoA/'+state_name+'_soil/nccpi2cs.csv') or os.path.exists('F:/DoA Modeling/DoA/'+state_name+'_soil/'+field+'_'+state_abbr+'.csv'):
            continue
    
        f = open('F:/DoA Modeling/DoA/'+state_name+'_soil/'+field+'_'+state_abbr+'.csv', 'w')
        os.mkdir('F:/DoA Modeling/DoA/'+state_name+'_soil/temp_files/')
        
        
        for i in range(1,298, 2):
            county_num = str(i).zfill(3)
            
            
            # Find County
            extract_params = {
                'EXPRESSION': '\"AREASYMBOL\" = \'' + state_abbr + county_num + '\'',
                'INPUT': 'F:/DoA Modeling/DoA/'+state_name+'_soil/soils/gSSURGO_'+state_abbr+'.gdb|layername=SAPOLYGON',
                #'OUTPUT': 'memory:'
                'OUTPUT': 'F:/DoA Modeling/DoA/'+state_name+'_soil/temp_files/extract_' + state_abbr + county_num + '.shp',
            }
            
            extract_res = processing.run('native:extractbyexpression', extract_params, feedback=feedback)
            QgsMessageLog.logMessage('buffer_layer:  ' + str(extract_res['OUTPUT']), "Sanity Check")
            
            #Create Buffer
            buffer_params = { 
                'DISSOLVE': False, 
                'DISTANCE': 0,
                'END_CAP_STYLE': 0,
                'INPUT': QgsVectorLayer(extract_res['OUTPUT'], "new_buffer"),
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 2,
                #'OUTPUT': 'memory:',
                'OUTPUT': 'F:/DoA Modeling/DoA/'+state_name+'_soil/temp_files/buffer_'+state_abbr+county_num+'.shp',
                'SEGMENTS': 5
            }
            bf_res = processing.run('native:buffer', parameters=buffer_params, feedback=feedback)
            buffer_layer = QgsVectorLayer(bf_res['OUTPUT'], "new_clip")
            
            
            # Clip Raster
            clip_params = {
                'ALPHA_BAND' : False, 
                'CROP_TO_CUTLINE' : True, 
                'DATA_TYPE' : 5, 
                'INPUT' : 'F:/DoA Modeling/DoA/'+state_name+'_soil/rasterized_soil_'+state_abbr+'.tif',
                'KEEP_RESOLUTION' : False,
                'MASK' : buffer_layer, 
                'NODATA' : None,
                'OPTIONS' : '', 
                'OUTPUT' : 'F:/DoA Modeling/DoA/'+state_name+'_soil/temp_files/clip_'+state_abbr+county_num+'.tif',
            }
            clip_res = processing.run('gdal:cliprasterbymasklayer', parameters=clip_params, feedback=feedback)
            clip_layer = QgsRasterLayer(clip_res['OUTPUT'], "new_stats")
            
            # Get Statistics
            stats_params = {
                'BAND' : 1,
                'INPUT' : clip_layer, 
                'OUTPUT_HTML_FILE' : 'F:/DoA Modeling/DoA/'+state_name+'_soil/temp_files/stats_'+state_abbr+county_num+'.html'
            }
            stats_res = processing.run('qgis:rasterlayerstatistics', parameters=stats_params)
            
            # Write to file
            f.write(state_abbr+county_num+','+str(stats_res['MEAN'])+'\n')
            
        f.close()
    