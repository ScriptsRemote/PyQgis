## Importar bibliotecas
import os
from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsProcessingFeatureSourceDefinition,
    QgsProcessingFeedback,
    QgsFeatureRequest,
    QgsProject
)
import processing

# Caminho para o raster (TIF)
path_to_tif = "F:/AMBGEO/PYQGIS/srtm_nasadem.tif"

# Carregar o raster
rlayer = QgsRasterLayer(path_to_tif, "NasaDem")
if not rlayer.isValid():
    print("Erro no carregamento do TIF!")
else:
    QgsProject.instance().addMapLayer(rlayer)

# Caminho para o shapefile (SHP)
path_to_shp_layer = "F:/AMBGEO/PYQGIS/BR_Municipios_2023.shp"

# Carregar o shapefile
vlayer = QgsVectorLayer(path_to_shp_layer, "Municipios BR", "ogr")
if not vlayer.isValid():
    print("Erro ao carregar o Layer SHP!")
else:
    QgsProject.instance().addMapLayer(vlayer)

# Lista de municípios para filtro
municipios = ['Torres', 'Mampituba', 'Itati']

# Filtro de municípios para criar um único shapefile filtrado
filtro_municipios = ' OR '.join([f'"NM_MUN" = \'{mun}\'' for mun in municipios])
municipios_layer = vlayer.materialize(QgsFeatureRequest().setFilterExpression(filtro_municipios))
municipios_layer.setName("Municípios Selecionados")
if municipios_layer.featureCount() > 0:
    QgsProject.instance().addMapLayer(municipios_layer)
else:
    print("Nenhum município encontrado com os nomes fornecidos!")

# Diretório de saída para os arquivos recortados
output_directory = "F:/AMBGEO/PYQGIS/Recortes/"
os.makedirs(output_directory, exist_ok=True)

# Loop para cada município individualmente
feedback = QgsProcessingFeedback()
for municipio in municipios:
    # Criar camada filtrada para o município atual
    filtro = f'"NM_MUN" = \'{municipio}\''
    municipio_layer = vlayer.materialize(QgsFeatureRequest().setFilterExpression(filtro))
    
    if municipio_layer.featureCount() == 0:
        print(f"Município '{municipio}' não encontrado no shapefile!")
        continue
    
    # Caminho do arquivo de saída do recorte raster
    output_path = os.path.join(output_directory, f"{municipio}_recorte.tif")
    
    # Configurações para o recorte
    processing_params = {
        'INPUT': path_to_tif,
        'MASK': municipio_layer,  # Usar o polígono filtrado como máscara
        'CROP_TO_CUTLINE': True,
        'KEEP_RESOLUTION': True,
        'OUTPUT': output_path
    }

    # Executar o recorte
    result = processing.run("gdal:cliprasterbymasklayer", processing_params, feedback=feedback)
    
    # Verificar e adicionar ao mapa
    if os.path.exists(output_path):
        print(f"Recorte salvo: {output_path}")
        recorte_raster = QgsRasterLayer(output_path, f"Recorte - {municipio}")
        if recorte_raster.isValid():
            QgsProject.instance().addMapLayer(recorte_raster)
    else:
        print(f"Erro ao recortar o raster para o município {municipio}!")
