### Dr. Komo

from qgis.core import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
import processing
from processing.core.Processing import Processing


class county_vector_aggregate(QgsProcessingAlgorithm):
    
    # Init

    Processing.initialize()
    feedback = QgsProcessingFeedback()

    state_abbr = 'IL'
    state_name = 'illinois'
    field = 'nccpi2cs'
    
    f = open('C:/Users/Shriyash/Documents/DoA Modeling/DoA/'+state_name+'_soil/nccpi2cs.csv', 'w+')
    
    
    for i in range(1,298, 2):
        #county_num = '051'
        county_num = str(i).zfill(3)
        
        
        # Find County
        extract_params = {
            'EXPRESSION': '\"AREASYMBOL\" = \'' + state_abbr + county_num + '\'',
            'INPUT': 'C:/Users/Shriyash/Documents/DoA Modeling/DoA/'+state_name+'_soil/soils/gssurgo_g_'+state_abbr.lower()+'/gSSURGO_'+state_abbr+'.gdb|layername=SAPOLYGON',
            #'OUTPUT': 'memory:'
            'OUTPUT': 'C:/Users/Shriyash/Documents/DoA Modeling/DoA/'+state_name+'_soil/test/extract_' + state_abbr + county_num + '.shp',
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
            'OUTPUT': 'C:/Users/Shriyash/Documents/DoA Modeling/DoA/'+state_name+'_soil/test/buffer_'+state_abbr+county_num+'.shp',
            'SEGMENTS': 5
        }
        bf_res = processing.run('native:buffer', parameters=buffer_params, feedback=feedback)
        buffer_layer = QgsVectorLayer(bf_res['OUTPUT'], "new_clip")
        
        
        # Clip Raster
        clip_params = {
            'ALPHA_BAND' : False, 
            'CROP_TO_CUTLINE' : True, 
            'DATA_TYPE' : 5, 
            'INPUT' : 'C:/Users/Shriyash/Documents/DoA Modeling/DoA/'+state_name+'_soil/rasterized_soil_'+state_abbr+'.tif',
            'KEEP_RESOLUTION' : False,
            'MASK' : buffer_layer, 
            'NODATA' : None,
            'OPTIONS' : '', 
            'OUTPUT' : 'C:/Users/Shriyash/Documents/DoA Modeling/DoA/'+state_name+'_soil/test/clip_'+state_abbr+county_num+'.tif',
        }
        clip_res = processing.run('gdal:cliprasterbymasklayer', parameters=clip_params, feedback=feedback)
        clip_layer = QgsRasterLayer(clip_res['OUTPUT'], "new_stats")
        
        # Get Statistics
        stats_params = {
            'BAND' : 1,
            'INPUT' : clip_layer, 
            'OUTPUT_HTML_FILE' : 'C:/Users/Shriyash/Documents/DoA Modeling/DoA/'+state_name+'_soil/test/stats_'+state_abbr+county_num+'.html'
        }
        stats_res = processing.run('qgis:rasterlayerstatistics', parameters=stats_params)
        
        # Write to file
        f.write(state_abbr+county_num+','+str(stats_res['MEAN'])+'\n')
        
    f.close()

