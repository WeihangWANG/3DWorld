#!/usr/bin/python3
# coding=utf-8

import numpy as np
import cv2

####################
# 调试说明
# PLAYBACK
# RECT_TRK_ALPHA
# BG_NOISE_TH
# MEAS_CONV
# MEAS_WID_LEN_CORR
# MEAS_HGT_CORR
#
# GROUND_DIST_MEAS
# GROUND_DIST     
####################

####################
# 回放
PLAYBACK        = False              # 是否回放
CALIBRATION_MODE=False #校准模式
MANUAL_CALI=True #手动校准
DEP_CORR = True #手动修正三维空间计算长宽高
DEP_CORR_K=[1.00,0.0]  #投射到三维空间受不同相机内参影响，简单修正系数

PLAYBACK_DEP    = './data/dep_19_11_58.bin' # 回放文件名
PLAYBACK_AMP    = './data/amp_19_11_58.bin' # 回放文件名
LOG_FNAME = 'log181030_0.txt'
STANDARD_BOX_SIZE = {1: [0.20, 0.20, 0.10],
                     2: [0.30, 0.30, 0.20],
                     3: [0.40, 0.40, 0.30],
                     4: [0.60, 0.40, 0.40]}

BOX_GROUND_TRUTH=STANDARD_BOX_SIZE[1]
PLAYBACK_SKIP   = 0
PLAYBACK_REWIND = np.inf
PLAYBACK_END    = 2900

####################
# 图像常量
IMG_WID=320
IMG_HGT=240
IMG_SZ=IMG_WID*IMG_HGT
IMG_SHAPE=(IMG_HGT,IMG_WID)

FRAME_DEP_SZ=IMG_SZ

FRAME_SZ=IMG_SZ*4   # float32 per pix
FRAME_BYTE_SZ=FRAME_SZ

####################
# 硬件启动配置
DMCAM_INTG      = 600   # 积分时间
DMCAM_FRAMERATE = 30    # 帧率
DMCAM_FREQ      = 24e6  # 频率
DMCAM_PIX_CALIB = 1     # 像素校准
DMCAM_HDR       = 0     # HDR模式
DMCAM_GAUSS     = 0     # 高斯滤波
DMCAM_MED       = 0     # 中值滤波
DMCAM_MODE ='2DCS'
####################
# 背景检测
BACKGROUND_PLOT     = False
BACKGROUND_MID_FILTER=5
BACKGROUND_SKIP     = 50    # 背景检测时跳过开始的图像帧数
BACKGROUND_CUM      = 10   # 背景检测累积帧数

BACKGROUND_MASK = np.zeros((IMG_HGT,IMG_WID),dtype=bool) # 预定义的背景屏蔽区域
BACKGROUND_MASK[20:IMG_HGT-20,20:IMG_WID-20]=True
#BACKGROUND_MASK = None

####################
# 地面检测
GROUND_CORR     = False             # 地面倾角修正

GROUND_MASK     = np.ones((IMG_HGT,IMG_WID),dtype=bool)
GROUND_MASK_EDGE = 20
GROUND_MASK[:GROUND_MASK_EDGE,:]=False; GROUND_MASK[IMG_HGT-GROUND_MASK_EDGE:,:]=False
GROUND_MASK[:,:GROUND_MASK_EDGE]=False; GROUND_MASK[:,IMG_WID-GROUND_MASK_EDGE:]=False


GROUND_DIST_MEAS   = False          # 是否测量相机到地面距离
GROUND_DIST        = 1.38 #0.715          # 相机距地面高度(标称值)
GROUND_FILL        = True           # 无效区域是否用地面高度填充？

####################
# 立方体检测
IMG_EDGE_POINT_MAX = 1800           # 边沿检测点过多，停止检测门限
EDGE_DET_TH        = 0.5            # 边沿检测门限
EDGE_DEP_BY_AMP    = True           # 用强度图检测边界
EDGE_DEP_AMP_TH    = 50            # 用强度图检测边界的门限

HOUGH_LINE_CUM_MIN = 10             # hough直线检测门限
HOUGH_LINE_TH_COEFF= 0.5#0.2            # hough直线参数提取门限，越小，提取的直线越多
LINE_NUM_MAX       = 30             # 执行矩形检测的直线数目上限

RECT_AREA_MIN      = 100            # 矩形最小面积
RECT_SIZE_RATIO_MAX= 10             # 矩形长短边比例
RECT_CENT_DIST_MIN = 5              # 两个矩形合并的中心距离门限
RECT_EDGE_DIST_MAX = 6              # 矩形边界直线和深度图边沿距离门限
RECT_EDGE_CUT      = 5              # 矩形边界直线和深度图边沿距离计算时，矩形边界截断量
RECT_MATH_TH       = 2              # 矩形匹配时定点距离

RECT_TRK           = False#True           # 矩形跟踪
RECT_TRK_ALPHA     = 0.85           # 矩形跟踪匹配的遗忘因子
RECT_TRK_T_MAX     = 3              # 矩形跟踪的时间窗口
RECT_TRK_CNT_TH    = 3              # 跟踪时间窗口内，矩形被检出次数

RECT_KEEP_MAX      = True           # 设置成只保留最大面积的盒子

ENABLE_USER_CALIB_PARAM=True        # 加载额外的用户校准数据

####################
# 图像处理

IMG_DEP_SAT_TH     = 20             # 深度图过曝光门限

AMP_FILTER         = True           # 光强过滤
AMP_TH             =50            # 光强过滤门限

MID_FILTER         = False 

IIR_FILTER         = False#True
IIR_ALPHA          = 0.5            # 深度图时域滤波因子

LAPLACE_FILTER     = False

SPACE_MID_FILTER   = False#True           # 中值滤波
SPACE_MID_FILTER_SZ= 3

FLY_NOISE_FILTER   = False#True 
FLY_NOISE_TH       = 0.02           # 飞散点过滤门限 
FLY_NOISE_WIN      = 3              # 飞散点过滤窗口尺寸

FILL_HOLE          = True

MORPH_OPEN         = False
MORPH_CLOSE        = False
KER_OPEN           = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)) # 开运算核（减少分散点带来的误差）
KER_CLOSE          = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)) # 闭运算核（减少分散点带来的误差）
KER_ERODE          = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)) # 计算面积使用的腐蚀核（减少边界误差）

BG_NOISE_TH        = 0.05          # 背景噪声切割门限，低于他的被认为是噪声

####################
# 镜头参数检测
MEAS_UNDISTORT     = True           # 镜头去畸变
MEAS_DEP_TO_Z      = True           # 射线距离转成Z距离
MEAS_CONV          = True           # 显示转换后的物理尺寸（而不是像素尺寸）
MEAS_FILTER        = True           # 测量结果滤波
MEAS_SHOW_RANGE    = [80,120]       # 显示测量结果的盒子中心位置

MEAS_HGT_CORR=0
MEAS_HGT_PARAM_A=0.557828119654
MEAS_HGT_PARAM_B=-1.587817929791
MEAS_HGT_PARAM_C=0.860890954240

MEAS_WID_LEN_CORR=0
MEAS_WID_LEN_PARAM_A=-0.301178030713
MEAS_WID_LEN_PARAM_B=1.330468715751
MEAS_WID_LEN_PARAM_C=-0.119452193623

MEAS_FX            = 319.331685     # 计算x/y尺寸的镜头参数
MEAS_FY            = 319.258460     # 计算x/y尺寸的镜头参数
MEAS_F             = (MEAS_FX+MEAS_FY)/2.0
MEAS_CX            = 162.00372
MEAS_CY            = 110.05493
MEAS_DMAT          = np.array([[MEAS_FX,      0,MEAS_CX],\
                               [      0,MEAS_FY,MEAS_CY],\
                               [      0,      0,      1]])
MEAS_DVEC          = np.array([-0.27131, 0.14523, -0.00099, 0.00032, 0.0])

####################
# 其他

SPEED_OF_LIGHT=299792458.0

#VIEW_DMIN, VIEW_DMAX = 0.0, 1.5 # 伪彩色显示的距离范围
VIEW_DMIN, VIEW_DMAX = 0.5, 2.0 # 伪彩色显示的距离范围
VIEW_AMP_SCALE     = 1        # 强度图显示时亮度压缩
PRINT_FPS=True #输出程序运行帧率
def print_config():
    print('PLAYBACK:', PLAYBACK)
    if PLAYBACK:
        print('PLAYBACK_DEP   :', PLAYBACK_DEP)
        print('PLAYBACK_AMP   :', PLAYBACK_AMP)
        print('PLAYBACK_SKIP  :', PLAYBACK_SKIP)
        print('PLAYBACK_REWIND:', PLAYBACK_REWIND)
        print('PLAYBACK_END   :', PLAYBACK_END)

    print('GROUND_CORR        :', GROUND_CORR)
    print('GROUND_DIST_MEAS   :', GROUND_DIST_MEAS)
    if not GROUND_DIST_MEAS: print('    GROUND_DIST:', GROUND_DIST)
    print('GROUND_FILL        :', GROUND_FILL)
    
    print()
    print('IMG_EDGE_POINT_MAX :', IMG_EDGE_POINT_MAX)
    print('EDGE_DET_TH        :', EDGE_DET_TH)
    print('HOUGH_LINE_CUM_MIN :', HOUGH_LINE_CUM_MIN)
    print('HOUGH_LINE_TH_COEFF:', HOUGH_LINE_TH_COEFF)
    print('LINE_NUM_MAX       :', LINE_NUM_MAX)
    
    print()
    print('RECT_AREA_MIN      :', RECT_AREA_MIN)
    print('RECT_SIZE_RATIO_MAX:', RECT_SIZE_RATIO_MAX)
    print('RECT_CENT_DIST_MIN :', RECT_CENT_DIST_MIN)
    print('RECT_EDGE_DIST_MAX :', RECT_EDGE_DIST_MAX)
    print('RECT_EDGE_CUT      :', RECT_EDGE_CUT)
    print('RECT_MATH_TH       :', RECT_MATH_TH)
    print('RECT_TRK           :', RECT_TRK)
    if RECT_TRK:
        print('    RECT_TRK_ALPHA :', RECT_TRK_ALPHA)
        print('    RECT_TRK_T_MAX :', RECT_TRK_T_MAX)
        print('    RECT_TRK_CNT_TH:', RECT_TRK_CNT_TH)
    print('RECT_SIZE_RATIO_MAX:', RECT_SIZE_RATIO_MAX)
    print('RECT_SIZE_RATIO_MAX:', RECT_SIZE_RATIO_MAX)

    print()
    print('IMG_DEP_SAT_TH     :', IMG_DEP_SAT_TH)
    print('AMP_FILTER         :', AMP_FILTER)
    if AMP_FILTER: print('    AMP_TH:', AMP_TH)
    print('MID_FILTER         :', MID_FILTER)
    print('IIR_FILTER         :', IIR_FILTER)
    if IIR_FILTER: print('IIR_ALPHA:', IIR_ALPHA)
    print('LAPLACE_FILTER     :', LAPLACE_FILTER)
    print('SPACE_MID_FILTER   :', SPACE_MID_FILTER)
    if SPACE_MID_FILTER: print('SPACE_MID_FILTER_SZ:', SPACE_MID_FILTER_SZ)
    print('FLY_NOISE_FILTER:', FLY_NOISE_FILTER)
    if FLY_NOISE_FILTER:
        print('FLY_NOISE_TH :', FLY_NOISE_TH)
        print('FLY_NOISE_WIN:', FLY_NOISE_WIN)
    print('FILL_HOLE          :', FILL_HOLE)
    print('MORPH_OPEN         :', MORPH_OPEN)
    print('MORPH_CLOSE        :', MORPH_CLOSE)
    print('BG_NOISE_TH        :', BG_NOISE_TH)
    
    print()
    print('MEAS_UNDISTORT     :', MEAS_UNDISTORT)
    print('MEAS_DEP_TO_Z      :', MEAS_DEP_TO_Z)
    print('MEAS_CONV          :', MEAS_CONV)
    print('MEAS_HGT_CORR      :', MEAS_HGT_CORR)
    print('MEAS_WID_LEN_CORR  :', MEAS_WID_LEN_CORR)
    print('MEAS_F             :', MEAS_F)
    
    print()
    print('LOG_FNAME:', LOG_FNAME)
    print('VIEW_DMIN:', VIEW_DMIN)
    print('VIEW_DMAX:', VIEW_DMAX)
