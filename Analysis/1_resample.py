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
        raster_band.SetDescription(bandNames[band_num-1])
        raster_band.WriteArray(img)
    del dataset

def pixel_geo_register(infile,outfile,reffile,methods):
    in_ds  = gdal.Open(infile, gdalconst.GA_ReadOnly) # 输入文件
    ref_ds = gdal.Open(reffile, gdalconst.GA_ReadOnly) # 参考文件
    
    in_trans = in_ds.GetGeoTransform()
    in_proj = in_ds.GetProjection()
    ref_trans = ref_ds.GetGeoTransform()
    ref_proj = ref_ds.GetProjection()
    # 参考文件的波段参考信息
    band_ref = ref_ds.GetRasterBand(1)
    
    # 输入文件的行列数
    x = ref_ds.RasterXSize 
    y = ref_ds.RasterYSize
    
    # 创建输出文件
    driver= gdal.GetDriverByName('GTiff')
    # GDT_Byte  GDT_Float32
    output = driver.Create(outfile, x, y, 1, gdalconst.GDT_Byte,options=["TILED=YES", "COMPRESS={0}".format("LZW")])
    # 设置输出文件地理仿射变换参数与投影
    output.SetGeoTransform(ref_trans)
    output.SetProjection(ref_proj)
    raster_band = output.GetRasterBand(1)
    raster_band.SetNoDataValue(0)
    
    # 重投影，插值方法为GRA_NearestNeighbour
    gdal.ReprojectImage(in_ds, output, in_proj, ref_proj, methods)
    
    # 关闭数据集与driver
    in_ds = None
    ref_ds = None
    driver  = None
    output = None


def parse_args():
    parser = argparse.ArgumentParser(
        description='Convert shp to semantic segmentation datasets')
    # parser.add_argument('--stable', default=r'D:\2_HaoweiPapers\3_ESPAndRelated\2_output\china_32649.tif' ,help='raster data path' )
    parser.add_argument('--stabledir',     default=r'D:\2_HaoweiPapers\3_ESPAndRelated\1_input\chinaMap\shp' ,help='raster data path' )
    parser.add_argument('--hfppath', default=r'D:\2_HaoweiPapers\3_ESPAndRelated\2_output\1_MSPA+InVEST\MSPA\bufferOutput1' ,help='raster data path' )
    parser.add_argument('--output', default=r'D:\2_HaoweiPapers\3_ESPAndRelated\2_output\1_MSPA+InVEST\MSPA\output' ,help='raster data path' )
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    stabledir = args.stabledir
    hfppath = args.hfppath
    output = args.output

    for i in range(4):
        newfile = 'lc2_china30_32649_' + str(i) + '_8_5_1_1.tif'
        stable = osp.join(osp.join(stabledir, 'b' + str(i) + '.tif'))
        file = 'lc2_china30_32649_' + str(i) + '_8_5_1_1.tif'
        methods=gdalconst.GRA_NearestNeighbour
        pixel_geo_register(osp.join(hfppath,file),osp.join(output,newfile),stable,methods)
        print(i)