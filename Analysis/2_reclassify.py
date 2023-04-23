from tkinter import Button
import numpy as np
from osgeo import gdal,ogr,osr
import argparse
import pandas as pd
import os,re
import os.path as osp
from osgeo import gdalconst

def GeoImgR(filename):
    dataset = gdal.Open(filename)
    im_porj = dataset.GetProjection()
    im_geotrans = dataset.GetGeoTransform()
    im_data = np.array(dataset.ReadAsArray())
    if len(im_data.shape) == 2:
        im_data = im_data[np.newaxis,:, :]
    del dataset
    return im_data, im_porj, im_geotrans

def GeoImgW(filename,im_data, im_geotrans, im_porj,bandNames,nodata, driver='GTiff'):
    im_shape = im_data.shape
    driver = gdal.GetDriverByName(driver)
    if "int8" in im_data.dtype.name:
        datetype = gdal.GDT_Byte
    elif "int16" in im_data.dtype.name:
        datetype = gdal.GDT_UInt16
    elif "int32" in im_data.dtype.name:
        datetype = gdal.GDT_UInt32
    else :
        datetype = gdal.GDT_Float32
    # datetype = gdal.GDT_Byte
    # driver.Create weight hight
    dataset = driver.Create(filename, im_shape[2], im_shape[1], im_shape[0], datetype,
    options=["TILED=YES", "COMPRESS={0}".format("LZW")])
    dataset.SetGeoTransform(im_geotrans)
    dataset.SetProjection(im_porj)
    for band_num in range(im_shape[0]):
        img = im_data[band_num,:,:]
        band_num = band_num + 1
        raster_band = dataset.GetRasterBand(band_num)
        raster_band.SetNoDataValue(nodata)
        # raster_band.SetDescription(bandNames[band_num-1])
        raster_band.WriteArray(img)
    del dataset

def parse_args():
    parser = argparse.ArgumentParser(
        description='Convert shp to semantic segmentation datasets')

    parser.add_argument('--inputpath', default=r'D:\2_HaoweiPapers\3_ESPAndRelated\2_output\1_MSPA+InVEST\InVEST\inputdir\input\input300' ,help='raster data path' )
    parser.add_argument('--output', default=r'D:\2_HaoweiPapers\3_ESPAndRelated\2_output\1_MSPA+InVEST\InVEST\inputdir\input\input300\input' ,help='raster data path' )
    args = parser.parse_args()
    return args

    # 

if __name__ == "__main__":
    args = parse_args()
    inputpath = args.inputpath
    output = args.output

    # *****************************************************************
    inputfile1 = r'D:\2_HaoweiPapers\3_ESPAndRelated\2_output\1_MSPA+InVEST\MSPA\lc2_china300_mspa_32649.tif'
    inputfile2 = r'D:\2_HaoweiPapers\3_ESPAndRelated\2_output\1_MSPA+InVEST\InVEST\quality_c.tif'
    outfile = r'D:\2_HaoweiPapers\3_ESPAndRelated\2_output\1_MSPA+InVEST\InVEST\quality_core.tif'

    im_data1, im_porj, im_geotrans = GeoImgR(inputfile1)
    im_data2, im_porj, im_geotrans = GeoImgR(inputfile2)
    sizea,sizeb,sizec = im_data1.shape[0],im_data1.shape[1],im_data1.shape[2]
    outImg = np.zeros((sizea,sizeb,sizec),dtype=np.float32)

    outImg[np.where((im_data1==17)| (im_data1==117))] = im_data2[np.where((im_data1==17)| (im_data1==117))]

    GeoImgW(outfile,outImg, im_geotrans, im_porj,'b1',0, driver='GTiff')


    # # 0.557520177,0.892078092
    # # 18.33933912 - 55.01801733
    # *****************************************************************
    inputfile1 = r'D:\2_HaoweiPapers\3_ESPAndRelated\2_output\1_MSPA+InVEST\MSPA\lc2_china300_mspa_32649.tif'
    inputfile2 = r'D:\2_HaoweiPapers\3_ESPAndRelated\2_output\1_MSPA+InVEST\InVEST\quality_core_class.tif'
    outfile = r'D:\2_HaoweiPapers\3_ESPAndRelated\2_output\1_MSPA+InVEST\MSPA\lc2_china300_remspa_32649.tif'

    im_data1, im_porj, im_geotrans = GeoImgR(inputfile1)
    im_data2, im_porj, im_geotrans = GeoImgR(inputfile2)
    sizea,sizeb,sizec = im_data1.shape[0],im_data1.shape[1],im_data1.shape[2]

    outImg = np.zeros((sizea,sizeb,sizec),dtype=np.int8) + 255

    outImg[np.where(((im_data1==17)|(im_data1==117)))] = 3 #Core3
    outImg[np.where(((im_data1==17)|(im_data1==117))&(im_data2==3))] = 1 #Core1
    outImg[np.where(((im_data1==17)|(im_data1==117))&(im_data2==2))] = 2 #Core2
    
    outImg[np.where((im_data1==9)|(im_data1==109))] = 4 #Islet
    outImg[np.where((im_data1==5)|(im_data1==105))] = 5 #Perforation
    outImg[np.where((im_data1==3)|(im_data1==103))] = 6 #Edge
    outImg[np.where((im_data1==65)|(im_data1==165))] = 7 #Loop
    outImg[np.where((im_data1==67)|(im_data1==167))] = 8 #LoopE
    outImg[np.where((im_data1==69)|(im_data1==169))] = 9 #LoopP
    outImg[np.where((im_data1==33)|(im_data1==133))] = 10 #Bridge
    outImg[np.where((im_data1==35)|(im_data1==135))] = 11 #BridgeE
    outImg[np.where((im_data1==37)|(im_data1==137))] = 12 #BridgeP
    outImg[np.where((im_data1==1)|(im_data1==101))] = 13 #Branch
    outImg[np.where((im_data1==0))] = 14 #Open
    outImg[np.where((im_data1==220))] = 15 #BOpen
    outImg[np.where((im_data1==100))] = 16 #COpen
    outImg[np.where((im_data1==129))] = 17 #Nodata

    GeoImgW(outfile,outImg, im_geotrans, im_porj,'b1',0, driver='GTiff')



# reclass_table = [
#     1.	1;
#     2	5;
#     3	10;
#     4	15;
#     5	20;
#     6	30;
#     7	25;
#     8	35;
#     9	20;
#     10	30;
#     11	35;
#     12	25;
#     13	40;
#     14	500;
#     15	300;
#     16	200;
#     17	missing;
# ]

# reclass_table = [
#     17.	1;
#     117	1;
#     109	200;
#     9	200;
#     105	150;
#     5	150;
#     103	100;
#     3	100;
#     165	30;
#     65	30;
#     167	30;
#     67	30;
#     169	30;
#     69	30;
#     133	10;
#     33	10;
#     135	10;
#     35	10;
#     137	10;
#     37	10;
#     101	100;
#     1	missing;
#     220	missing;
#     100	missing;
#     129	missing;
#     128	missing;
# ]