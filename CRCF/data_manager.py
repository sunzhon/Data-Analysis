#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
This module was developed to manage robot data, including sensory feedback, controller variable values, locomotion 
data of robot. It's operations includes: read log file of datasets, load datasets file, assign data into variables 



It has data loading and preprocessing functions:

    load_csv_file()
    load_a_trial_data()
    load_data_log()



Author: suntao
Email: suntao.hn@gmail.com
Created date: before 16-12-2021
'''


import sys
import numpy as np
import math
import os
import pdb 
import termcolor
import gnureadline
import pandas as pd
import re
import time as localtimepkg
from brokenaxes import brokenaxes
import warnings

#import metrics


def load_data_log(data_file_dic):
    '''
    Load a log file that stores file names and their categoires of the robot run data,
    Group data by experiment_categories/categories and output the categories (experiemnt classes)

    '''

    #- This function to check whether the entry parameter is a number
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass

        return False

    #1.1) load file list 
    data_file_log = os.path.join(data_file_dic,"ExperimentDataLog.csv")
    data_files = pd.read_csv(data_file_log, sep='\t',delimiter=r'\t',skiprows=1,header=None, names=['titles', 'data_files','categories'], skip_blank_lines=True,dtype=str,engine='python')
    #data_files = pd.read_csv(data_file_log, skiprows=1, names=['titles', 'data_files','categories'], skip_blank_lines=True, dtype=str)

    data_files_categories=data_files.groupby('categories')

    '''
    keys = data_files_categories.groups.keys() # categories should be a list of number
    categories=[]
    pdb.set_trace()
    for ll in keys: #drop off the non-number categories
        if is_number(ll):
            categories.append(ll)
    
    temp_dic={}
    for idx, value in enumerate(categories):
        temp_dic[str(float(categories[idx]))]=value

    temp_dic_keys =[str(ll) for ll in sorted([ float(ll) for ll in temp_dic.keys()])]

    for idx,value in enumerate(temp_dic_keys):
        categories[idx]=temp_dic[value]

    '''
    return data_files_categories



def load_csv_file(fileName,folderName="/home/suntao/workspace/experiment_data/0127113800",columnsName=None):
    '''
    load data from a file
    fileName: the name of file that you want to read
    columnsName: it the column name of the file
    Note: the args of sys is file_id and date of the file
    '''
        
    #1) load data from file
    data_file = os.path.join(folderName,fileName + ".csv")
    if(columnsName==None): # 没有设定 column name, 因为文件中有了, 使用文件中的第一行作为columns name
        try:
            resource_data = pd.read_csv(data_file, sep='\t', index_col=0, header=0, skip_blank_lines=True, dtype=str) # use the first row as clomun names
        except:
            print("Please check the data file!, see: ", data_file)
            pdb.set_trace()
    else: # 设定了columns, 因为文件中没有
        try:
            resource_data = pd.read_csv(data_file, sep='\t', index_col=0, header=0, names=columnsName,skip_blank_lines=True,dtype=str)#names will replace the first row 
        except:
            print("Please check the data file! See: ", data_file)
            pdb.set_trace()

    #2) check data whether loss frame
    if(len(resource_data.index)!=resource_data.shape[0]):
        print("dataset loss frame in ",data_file)
        warnings.warn("Please note that the raw data loss some frame")

    read_rows=resource_data.shape[0]-1
    try:
        fine_data = resource_data.iloc[0:read_rows,:].astype(float)# 数据行对齐
    except ValueError:
        warnings.warn("data type is wrong, please check raw dataset")
        pdb.set_trace()

    return fine_data




# This function define column name manually

def load_a_trial_data_A(freq,start_time,end_time,folder_name):
    
    #read data from experiment files of a trial and retrieve a range of data [start_time, end_time]

   
    #1) Load data
    fileName_CPGs="controlfile_CPGs"
    fileName_commands='controlfile_commands'
    fileName_modules='controlfile_modules'
    fileName_parameters='parameterfile_rosparameters'
    fileName_joints='sensorfile_joints'

    columnsName_CPGs=['RFO1','RFO2','RHO1','RHO2','LFO1','LFO2','LHO1','LKO2']
    columnsName_GRFs=['RF','RH','LF','LH']
    columnsName_POSEs=['roll','picth','yaw', 'x','y','z','vx','vy','vz']
    columnsName_jointPositions=['p1','p2','p3','p4','p5','p6', 'p7','p8','p9','p10','p11','p12']
    columnsName_jointVelocities=['v1','v2','v3','v4','v5','v6', 'v7','v8','v9','v10','v11','v12']
    columnsName_jointCurrents=['c1','c2','c3','c4','c5','c6', 'c7','c8','c9','c10','c11','c12']
    columnsName_jointVoltages=['vol1','vol2','vol3','vol4','vol5','vol6', 'vol7','vol8','vol9','vol10','vol11','vol12']
    
    columnsName_modules=['ANC_stability', 'GRFNosie1','GRFNoise2','GRFNoise3','GRFNoise4','adfrl_w1', 'dfrl_w2', 'dfrl_w3', 'dfrl_w4', 'f1','f2','f3','f4','f5','f6','f7','f8','g1','g2','g3','g4','g5','g6','g7','g8','FM1','FM2','adapitve_gama1','adaptive_gamma2','NP_GRF_1','NP_GRF_2','phi_12','phi_13','phi_14']

    #columnsName_modules=['ANC_stability','adfrl_w1', 'dfrl_w2', 'dfrl_w3', 'dfrl_w4', 'f1','f2','f3','f4','f5','f6','f7','f8','g1','g2','g3','g4','g5','g6','g7','g8','FM1','FM2','adapitve_gama1','adaptive_gamma2','NP_GRF_1','NP_GRF_2','phi_12','phi_13','phi_14']

    #columnsName_modules=['ANC_stability','adfrl_w1', 'dfrl_w2', 'dfrl_w3', 'dfrl_w4', 'f1','f2','f3','f4','f5','f6','f7','f8','g1','g2','g3','g4','g5','g6','g7','g8','FM1','FM2','adapitve_gama1','adaptive_gamma2','phi_12','phi_13','phi_14']

    columnsName_rosparameters=['USER_MACRO','CPGtype','CPGMi','CPGPGain', 'CPGPThreshold', 'PCPGBeta', \
                            'RF_PSN','RF_VRN_Hip','RF_VRN_Knee','RF_MN1','RF_MN2','RF_MN3',\
                            'RH_PSN','RH_VRN_Hip','RH_VRN_Knee','RH_MN1','RH_MN2','RH_MN3',\
                            'LF_PSN','LF_VRN_Hip','LF_VRN_Knee','LF_MN1','LF_MN2','LF_MN3',\
                            'LH_PSN','LH_VRN_Hip','LH_VRN_Knee','LH_MN1','LH_MN2','LH_MN3'
                           ]
    columnsName_commands=['c1','c2','c3','c4','c5','c6', 'c7','c8','c9','c10','c11','c12']


    columnsName_joints = columnsName_jointPositions + columnsName_jointVelocities + columnsName_jointCurrents + columnsName_jointVoltages + columnsName_POSEs + columnsName_GRFs
    
    #read CPG output
    cpg_data=load_csv_file(fileName_CPGs,folder_name,columnsName_CPGs)    
    cpg_data=cpg_data.values

    #read commands
    command_data=load_csv_file(fileName_commands,folder_name,columnsName_commands)    
    command_data=command_data.values

    #read ANC stability value
    module_data=load_csv_file(fileName_modules,folder_name, columnsName_modules)    
    module_data=module_data.values

    #read ROS parameter value
    parameter_data=load_csv_file(fileName_parameters,folder_name, columnsName_rosparameters)    
    parameter_data=parameter_data.values

    #read joint sensory data
    jointsensory_data=load_csv_file(fileName_joints,folder_name, columnsName_joints)    

    grf_data=jointsensory_data[columnsName_GRFs].values
    pose_data=jointsensory_data[columnsName_POSEs].values
    position_data=jointsensory_data[columnsName_jointPositions].values
    velocity_data=jointsensory_data[columnsName_jointVelocities].values
    current_data=jointsensory_data[columnsName_jointCurrents].values
    voltage_data=jointsensory_data[columnsName_jointVoltages].values
    

    #2) postprecessing 
    read_rows=min([4000000,jointsensory_data.shape[0], cpg_data.shape[0], command_data.shape[0], parameter_data.shape[0], module_data.shape[0]])
    start_point=int(start_time*freq)
    end_point=int(end_time*freq)
    if end_point>read_rows:
        print(termcolor.colored("Warning:end_point out the data bound, please use a small one","yellow"),"end_point :{}, read_rows :{}".format(end_point,read_rows))
    time = np.linspace(start_time,end_time,end_point-start_point)
    #time = np.linspace(0,int(end_time/freq)-int(start_time/freq),end_time-start_time)
    return cpg_data[start_point:end_point,:], command_data[start_point:end_point,:], module_data[start_point:end_point,:], parameter_data[start_point:end_point,:], grf_data[start_point:end_point,:], pose_data[start_point:end_point,:], position_data[start_point:end_point,:],velocity_data[start_point:end_point,:],current_data[start_point:end_point,:],voltage_data[start_point:end_point,:], time




def load_a_trial_data_B(freq,start_time,end_time,folder_name):
    '''
    read data from experiment files of a trial and retrieve a range of data [start_time, end_time]

    '''
    #1) Load data
    fileName_CPGs="controlfile_CPGs"
    fileName_commands='controlfile_commands'
    fileName_modules='controlfile_modules'
    fileName_parameters='parameterfile_rosparameters'
    fileName_joints='sensorfile_joints'

    #read CPG output
    cpg_data=load_csv_file(fileName_CPGs,folder_name)    
    cpg_data=cpg_data.values

    #read commands
    command_data=load_csv_file(fileName_commands,folder_name)    
    command_data=command_data.values

    #read ANC stability value
    module_data=load_csv_file(fileName_modules,folder_name)    
    module_data=module_data.values

    #read ROS parameter value
    parameter_data=load_csv_file(fileName_parameters,folder_name)    
    parameter_data=parameter_data.values

    #read joint sensory data
    jointsensory_data=load_csv_file(fileName_joints,folder_name)    

    columnsName_GRFs=['GRF_0','GRF_1','GRF_2','GRF_3']

    columnsName_POSEs=['Pose_0','Pose_1','Pose_2','Pose_3','Pose_4','Pose_5','Pose_6','Pose_7','Pose_8']

    columnsName_jointPositions=[
        'JointPosition_0','JointPosition_1','JointPosition_2',
        'JointPosition_3','JointPosition_4','JointPosition_5',
        'JointPosition_6','JointPosition_7','JointPosition_8',
        'JointPosition_9','JointPosition_10','JointPosition_11'
                                      ]
    columnsName_jointVelocities=[
        'JointVelocity_0','JointVelocity_1','JointVelocity_2',
        'JointVelocity_3','JointVelocity_4','JointVelocity_5',
        'JointVelocity_6','JointVelocity_7','JointVelocity_8',
        'JointVelocity_9','JointVelocity_10','JointVelocity_11'
                                      ]
    columnsName_jointCurrents=[
        'JointCurrent_0','JointCurrent_1','JointCurrent_2',
        'JointCurrent_3','JointCurrent_4','JointCurrent_5',
        'JointCurrent_6','JointCurrent_7','JointCurrent_8',
        'JointCurrent_9','JointCurrent_10','JointCurrent_11'
                                      ]
    columnsName_jointVoltages=[
        'JointVoltage_0','JointVoltage_1','JointVoltage_2',
        'JointVoltage_3','JointVoltage_4','JointVoltage_5',
        'JointVoltage_6','JointVoltage_7','JointVoltage_8',
        'JointVoltage_9','JointVoltage_10','JointVoltage_11'
                                      ]

    grf_data=jointsensory_data[columnsName_GRFs].values
    pose_data=jointsensory_data[columnsName_POSEs].values
    position_data=jointsensory_data[columnsName_jointPositions].values
    velocity_data=jointsensory_data[columnsName_jointVelocities].values
    current_data=jointsensory_data[columnsName_jointCurrents].values
    voltage_data=jointsensory_data[columnsName_jointVoltages].values


    #2) postprecessing 
    read_rows=min([4000000,jointsensory_data.shape[0], cpg_data.shape[0], command_data.shape[0], parameter_data.shape[0], module_data.shape[0]])
    start_point=int(start_time*freq)
    end_point=int(end_time*freq)
    if end_point>read_rows:
        print(termcolor.colored("Warning:end_point out the data bound, please use a small one","yellow"),"end_point :{}, read_rows :{}".format(end_point,read_rows))
    time = np.linspace(start_time,end_time,end_point-start_point)
    #time = np.linspace(0,int(end_time/freq)-int(start_time/freq),end_time-start_time)

    return cpg_data[start_point:end_point,:], command_data[start_point:end_point,:], module_data[start_point:end_point,:], parameter_data[start_point:end_point,:], grf_data[start_point:end_point,:], pose_data[start_point:end_point,:], position_data[start_point:end_point,:],velocity_data[start_point:end_point,:],current_data[start_point:end_point,:],voltage_data[start_point:end_point,:], time



def load_a_trial_data(freq,start_time,end_time,folder_name):

    # whether dataset in the data file has its column name


    file_name="controlfile_CPGs"
    data_file = os.path.join(folder_name,file_name + ".csv")
    resource_data = pd.read_csv(data_file, sep='\t', skip_blank_lines=True, dtype=str)#

    if(resource_data.columns[0]=='Time'):
        has_coulum = True
    else:
        has_coulum = False

    # choose a way
    if(has_coulum):
        return  load_a_trial_data_B(freq, start_time, end_time, folder_name)
    else:
        return load_a_trial_data_A(freq, start_time, end_time, folder_name)



