### Dr. Komo

from qgis.core import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtCore import *
import processing
from processing.core.Processing import Processing


class county_vector_aggregate(QgsProcessingAlgorithm):
    
    # Init
    
    f = open('C:/Users/Shriyash/Documents/DoA Modeling/DoA/iowa_soil/nccpi2cs - 500.csv', 'w+')

    Processing.initialize()
    feedback = QgsProcessingFeedback()

    state_abbr = 'IA'
    field = 'nccpi2cs'
    
    for i in range(1,298, 2):
        #county_num = '051'
        county_num = str(i).zfill(3)
        
        
        # Find County
        extract_params = {
            'EXPRESSION': '\"AREASYMBOL\" = \'' + state_abbr + county_num + '\'',
            'INPUT': 'C:/Users/Shriyash/Documents/DoA Modeling/DoA/iowa_soil/gSSURGO_IA.gdb|layername=SAPOLYGON',
            #'OUTPUT': 'memory:'
            'OUTPUT': 'C:/Users/Shriyash/Documents/DoA Modeling/DoA/iowa_soil/test/extract_' + state_abbr + county_num + '.shp',
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
            'OUTPUT': 'C:/Users/Shriyash/Documents/DoA Modeling/DoA/iowa_soil/test/buffer_'+state_abbr+county_num+'.shp',
            'SEGMENTS': 5
        }
        bf_res = processing.run('native:buffer', parameters=buffer_params, feedback=feedback)
        buffer_layer = QgsVectorLayer(bf_res['OUTPUT'], "new_stats")
        
        #Calculate 
        stats_params = {
            'COLUMN_PREFIX' : '_',
            'INPUT_RASTER' : 'C:/Users/Shriyash/Desktop/corn_layers/rasters/qgs2r1.tif',
            'INPUT_VECTOR' : buffer_layer,
            'RASTER_BAND' : 1,
            'STATS' : [2]
        }
        stats_res = processing.run('qgis:zonalstatistics', stats_params, feedback=feedback)
        
        # Write to file
        for feature in buffer_layer.getFeatures():
            mean = feature["_mean"]
            f.write(state_abbr+county_num+','+str(mean)+'\n')
        
    f.close()
