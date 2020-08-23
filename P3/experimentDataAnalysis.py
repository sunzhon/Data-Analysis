#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib import gridspec
import os
import pdb 
import termcolor
import gnureadline
plt.rc('font',family='Arial')
import pandas as pd
import re
import time as localtimepkg
from brokenaxes import brokenaxes
from mpl_toolkits import mplot3d
from matplotlib import animation
import seaborn as sns
import matplotlib as mpl

'''
###############################
Data loading and preprocessing functions

loadData()
read_data()
load_data_log()

'''

class neuralprocessing:
    '''
    Neral processing unit for filter GRFs signals
    '''
    w_i= 20.0
    w_r= 7.2
    bias= -6.0

    def __init__(self):
        self.input=0.0
        self.output=0.0
        self.output_old=0.0

    def step(self, input_signal):
        self.input = input_signal 
        self.output_old = self.output;
        activity = self.w_i*self.input+self.w_r*self.output_old+self.bias
        self.output = 1.0/(1.0+math.exp(-activity))
        return self.output

def NP(data):
    neural_process= neuralprocessing()

    filter_output=[]
    for idx in range(len(data)):
        filter_output.append(neural_process.step(data[idx]))

    return np.array(filter_output)

def test_neuralprocessing():
    '''
    It is a test for the class of the neuralprocessing  and its function implementation
    '''

    np = neuralprocessing()
    filtered=[]
    source=[]
    for idx in range(100):
        source.append(0.15 * math.sin(idx/20*3.14))
        filtered.append(np.step(source[-1]))

    
    filtered=NP(source)
    plt.plot(source,'g')
    plt.plot(filtered,'r')
    plt.show()

def load_data_log(data_file_dic):
    '''
    Load data log that stores data files

    '''
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
    data_file_log = data_file_dic +"ExperimentDataLog.log"
    data_files = pd.read_csv(data_file_log, sep='\t',header=None, names=['file_name','experiment_classes'], skip_blank_lines=True,dtype=str)

    data_files_categories=data_files.groupby('experiment_classes')
    keys = data_files_categories.groups.keys()
    categories=[]
    for ll in keys:
        if is_number(ll):
            categories.append(ll)
    
    temp_dic={}
    for idx, value in enumerate(categories):
        temp_dic[str(float(categories[idx]))]=value

    temp_dic_keys =[str(ll) for ll in sorted([ float(ll) for ll in temp_dic.keys()])]

    for idx,value in enumerate(temp_dic_keys):
        categories[idx]=temp_dic[value]

    print(categories)
    return data_files_categories, categories

def loadData(fileName,columnsName,folderName="/home/suntao/workspace/experiment_data/0127113800"):
    '''
    load data from a file
    fileName: the name of file that you want to read
    columnsName: it the column name of the file
    Note: the args of sys is file_id and date of the file
    '''
        
    #1) load data from file
    data_file = folderName +"/"+ fileName + ".csv"
    resource_data = pd.read_csv(data_file, sep='\t', index_col=0,header=None, names=columnsName, skip_blank_lines=True,dtype=str)

    read_rows=resource_data.shape[0]-1
    fine_data = resource_data.iloc[0:read_rows,:].astype(float)# 数据行对齐
    return fine_data

def read_data(freq,start_point,end_point,folder_name):
    '''
    read data from file cut a range data

    '''
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
    columnsName_modules=['ss','Noise1','Noise2','Noise3','Noise4']
    columnsName_parameters=['MI','CPGBeta','CPGType', \
                            'RF_PSN','RF_VRN_Hip','RF_VRN_Knee','RF_MN1','RF_MN2','RF_MN3',\
                            'RH_PSN','RH_VRN_Hip','RH_VRN_Knee','RH_MN1','RH_MN2','RH_MN3',\
                            'LF_PSN','LF_VRN_Hip','LF_VRN_Knee','LF_MN1','LF_MN2','LF_MN3',\
                            'LH_PSN','LH_VRN_Hip','LH_VRN_Knee','LH_MN1','LH_MN2','LH_MN3'
                           ]
    columnsName_commands=['c1','c2','c3','c4','c5','c6', 'c7','c8','c9','c10','c11','c12']


    columnsName_joints = columnsName_jointPositions + columnsName_jointVelocities + columnsName_jointCurrents + columnsName_jointVoltages + columnsName_POSEs + columnsName_GRFs
    
    #CPG
    cpg_data=loadData(fileName_CPGs,columnsName_CPGs,folder_name)    
    cpg_data=cpg_data.values

    #commands
    command_data=loadData(fileName_commands,columnsName_commands,folder_name)    
    command_data=command_data.values

    #ANC stability value
    module_data=loadData(fileName_modules,columnsName_modules,folder_name)    
    module_data=module_data.values

    #parameter
    parameter_data=loadData(fileName_parameters,columnsName_parameters,folder_name)    
    parameter_data=parameter_data.values

    #joint sensory data
    jointsensory_data=loadData(fileName_joints,columnsName_joints,folder_name)    
    grf_data=jointsensory_data[columnsName_GRFs].values
    pose_data=jointsensory_data[columnsName_POSEs].values
    position_data=jointsensory_data[columnsName_jointPositions].values
    velocity_data=jointsensory_data[columnsName_jointVelocities].values
    current_data=jointsensory_data[columnsName_jointCurrents].values
    voltage_data=jointsensory_data[columnsName_jointVoltages].values


    #2) postprecessing 
    read_rows=min([4000000,jointsensory_data.shape[0], cpg_data.shape[0], command_data.shape[0], parameter_data.shape[0], module_data.shape[0]])
    if end_point>read_rows:
        print(termcolor.colored("Warning:end_point out the data bound, please use a small one","yellow"))
    time = np.linspace(int(start_point/freq),int(end_point/freq),end_point-start_point)
    #time = np.linspace(0,int(end_point/freq)-int(start_point/freq),end_point-start_point)
    return cpg_data[start_point:end_point,:], command_data[start_point:end_point,:], module_data[start_point:end_point,:], parameter_data[start_point:end_point,:], grf_data[start_point:end_point,:], pose_data[start_point:end_point,:], position_data[start_point:end_point,:],velocity_data[start_point:end_point,:],current_data[start_point:end_point,:],voltage_data[start_point:end_point,:], time

def stsubplot(fig,position,number,gs):
    axprops = dict(xticks=[], yticks=[])
    width_p=position.x1-position.x0; height_p=(position.y1-position.y0)/number
    left_p=position.x0;bottom_p=position.y1-height_p;
    ax=[]
    for idx in range(number):
        ax.append(fig.add_axes([left_p,bottom_p-idx*height_p,width_p,height_p], **axprops))
        #ax.append(brokenaxes(xlims=((76, 116), (146, 160)), hspace=.05, despine=True,fig=fig,subplot_spec=gs))
        ax[-1].set_xticks([])
        ax[-1].set_xticklabels(labels=[])
    return ax

def grf_diagram(fig,axs,gs,grf_data,time):
    '''
    plot ground reaction forces of four legs in curves
    '''
    position=axs.get_position()
    axs.set_yticklabels(labels=[])
    axs.set_yticks([])
    axs.set_xticks([t for t in np.arange(time[0],time[-1]+0.1,2,dtype='int')])
    axs.set_xticklabels(labels=[str(t) for t in np.arange(round(time[0]),round(time[-1])+0.1,2,dtype='int')],fontweight='light')
    axs.set_title("Ground reaction force",loc="left",pad=2)

    ax=stsubplot(fig,position,4,gs)
    LegName=['RF','RH', 'LF', 'LH']
    barprops = dict(aspect='auto', cmap=plt.cm.binary, interpolation='nearest',vmin=0.0,vmax=1.0)
    for idx in range(4):
        ax[idx].set_yticks([0.1*(idx+1)])
        ax[idx].plot(grf_data[:,idx])
        ax[idx].set_ylabel(LegName[idx])
        ax[idx].set_yticklabels(labels=[0.0,0.5,1.0])
        ax[idx].set_yticks([0.0,0.5,1.0])
        ax[idx].set_ylim([-0.1,1.1])
        ax[idx].set_xticks([])
        ax[idx].set_xticklabels(labels=[])
        ax[idx].grid(which='both',axis='x',color='k',linestyle=':')
        ax[idx].grid(which='both',axis='y',color='k',linestyle=':')

def gait_diagram(fig,axs,gs,gait_data):
    '''
    plot gait diagram using while and black block to indicate swing and stance phase
    '''
    position=axs.get_position()
    axs.set_yticklabels(labels=[])
    axs.set_yticks([])
    axs.set_xticks([])
    axs.set_xticklabels(labels=[])
    #axs.set_title("Gait",loc="left",pad=2)

    ax=stsubplot(fig,position,4,gs)
    xx=[]
    LegName=['RF','RH', 'LF', 'LH']
    barprops = dict(aspect='auto', cmap=plt.cm.binary, interpolation='nearest',vmin=0.0,vmax=1.0)
    for idx in range(4):
        ax[idx].set_yticks([0.1*(idx+1)])
        xx.append(np.where(gait_data[:,idx]>0.2*max(gait_data[:,idx]),1.0,0.0))
        ax[idx].imshow(xx[idx].reshape((1,-1)),**barprops)
        ax[idx].set_ylabel(LegName[idx])
        ax[idx].set_yticklabels(labels=[])

def lowPassFilter(data,gamma):
    '''
    #filter 1
    filterData=gamma*data+(1.0-gamma)*np.append(data[-1],data[0:-1])
    return filterData
    '''
    '''
    #filter 2
    filterData=[]
    for idx, value in enumerate(data):
    filterData.append(sum(data[0:idx])/(idx+1))
    return np.array(filterData)

    '''
    #filter 3
    filterData=[]
    setpoint=20
    for idx, value in enumerate(data):
        if(idx<setpoint):
            count=idx+1
            filterData.append(sum(data[0:idx])/(count))
        else:
            count=setpoint
            filterData.append(sum(data[idx-count:idx])/(count))

    return np.array(filterData)

def EnergyCost(U,I,Fre):
    '''
    U is also means joint toruqe
    I is also means joint velocity
    '''
    if ((type(U) is np.ndarray) and (type(I) is np.ndarray)):
        E=sum(sum(np.fabs(U)*np.fabs(I)*1/Fre))
    else:
        print("input data type is wrong, please use numpy array")
    return E

def COG_distribution(grf_data):
    '''
    division should have a large value, it indicates the foot on the ground.
    '''
    f_front=grf_data[:,0]+grf_data[:,2]
    f_hind=grf_data[:,1]+grf_data[:,3]
    sum_f=np.column_stack([f_front,f_hind])
    #sum_f=sum_f[sum_f[:,0]>0.1] # the front legs shoulb be on stance phase
    #sum_f=sum_f[sum_f[:,1]>0.1] # the hind legs shoulb be on stance phase
    if(len(sum_f)==0):
        print("robot fail down or no stance phase during the period")
        print("simulation is wrong, please redo this simulation")
        gamma=[0]
    else:
        gamma=sum_f[:,0]/sum_f[:,1]
    # set the gamma to zero when robot is fixed in the air
    temp=pd.DataFrame(np.column_stack([sum_f,gamma]),columns=['front','hind','gamma'])
    temp.loc[temp['hind']<0.015,'gamma']=0.0
    gamma=temp['gamma'].to_numpy().reshape((-1,1))
    if(len(grf_data)!=len(gamma)):
        print("COG distribution remove the no stance data")
    return gamma

def Average_COG_distribution(grf_data):
    '''
    calculate the average value of the gamma of during the robot walking
    '''
    data=COG_distribution(grf_data)
    return np.mean(data)

def gait(data):
    ''' Calculating the gait information including touch states and duty factor'''
    # binary the GRF value 
    threshold = 0.1*max(data[:,0])
    state=np.zeros(data.shape,int)
    for i in range(data.shape[1]):
        for j in range(data.shape[0]):
            if data[j,i] < threshold:
                state[j,i] = 0
            else:
                state[j,i]=1
    
    # get gait info, count the touch and lift number steps
    gait_info=[]
    beta=[]
    state=np.vstack([state,abs(state[-1,:]-1)])
    for i in range(state.shape[1]): #each leg
        count_stance=0;
        count_swing=0;
        number_stance=0
        number_swing=0
        duty_info = {}
                
        for j in range(state.shape[0]-1): #every count
            if state[j,i] ==1:# stance 
                count_stance+=1
            else:#swing
                count_swing+=1

            if (state[j,i]==0) and (state[j+1,i]==1):
                duty_info[str(number_swing)+ "swing"]= count_swing
                count_swing=0
                number_swing+=1
            if (state[j,i]==1) and (state[j+1,i]==0):
                duty_info[str(number_stance) + "stance"]= count_stance
                count_stance=0
                number_stance+=1
            
        gait_info.append(duty_info)
    # calculate the duty factors of all legs
    for i in range(len(gait_info)): # each leg
        beta_singleleg=[]
        for j in range(int(len(gait_info[i])/2)): # each step, ignore the first stance or swing
            if (gait_info[i].__contains__(str(j)+'stance') and  gait_info[i].__contains__(str(j)+'swing')):
                beta_singleleg.append(gait_info[i][str(j)+"stance"]/(gait_info[i][str(j)+"stance"] + gait_info[i][str(j) + "swing"]))
            elif (gait_info[i].__contains__(str(j)+'stance') and  (not gait_info[i].__contains__(str(j)+'swing'))):
                beta_singleleg.append(1.0)
            elif ((not gait_info[i].__contains__(str(j)+'stance')) and  gait_info[i].__contains__(str(j)+'swing')):
                beta_singleleg.append(0.0)
        
        # remove the max and min beta of each legs during the whole locomotion
        if(beta_singleleg!=[]):
            beta_singleleg.remove(max(beta_singleleg))
        if(beta_singleleg!=[]):
            beta_singleleg.remove(min(beta_singleleg))

        beta.append(beta_singleleg)

    return state, beta

def AvgerageGaitBeta(beta):
    '''
    Calculate the average duty factors of every legs within a walking period.
    '''
    average_beta=[]
    for i in range(len(beta)):
        average_beta.append(np.mean(beta[i]))

    return average_beta

def Animate_phase_transition(cpg_data):
    """
    Matplotlib Animation Example

    author: Jake Vanderplas
    email: vanderplas@astro.washington.edu
    website: http://jakevdp.github.com
    license: BSD
    Please feel free to use and modify this, but keep the above information. Thanks!
    """


    # First set up the figure, the axis, and the plot element we want to animate
    figsize=(7.1244,7.1244)
    fig = plt.figure(figsize=figsize)
    ax = plt.axes(xlim=(-1.2, 1.2), ylim=(-1.2, 1.2))
    ax.set_xlabel(r'$O_{1}$')
    ax.set_ylabel(r'$O_{2}$')
    ax.set_title(r'Phase diagram')
    line1, = ax.plot([], [], 'r-',lw=1)
    line2, = ax.plot([], [], 'g-',lw=1)
    line3, = ax.plot([], [], 'b-',lw=1)
    line4, = ax.plot([], [], 'y-',lw=1)

    point1, = ax.plot([], [], 'ro-',lw=1,markersize=6)
    point2, = ax.plot([], [], 'go-',lw=1,markersize=6)
    point3, = ax.plot([], [], 'bo-',lw=1,markersize=6)
    point4, = ax.plot([], [], 'yo-',lw=1,markersize=6)
    ax.grid(which='both',axis='x',color='k',linestyle=':')
    ax.grid(which='both',axis='y',color='k',linestyle=':')
    ax.legend((point1,point2,point3,point4),['RF','RH','LF','LH'],ncol=4)
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
    energy_text = ax.text(0.02, 0.90, '', transform=ax.transAxes)
    line_length=60
    ax.text(-0.45,0.2,r'$a_{i}(t)=\sum_{j=1}^2 w_{ij}*o_{i}(t-1)+b_{i}+f_{i},i=1,2$')
    ax.text(-0.45,0.0,r'$o_{i}(t)=\tanh(a_{1,2})$')
    #ax.text(-0.45,-0.2,r'$f_{1}=-\gamma*GRF*cos(o_{1}(t-1))$')
    #ax.text(-0.45,-0.3,r'$f_{2}=-\gamma*GRF*sin(o_{2}(t-1))$')
    ax.text(-0.45,-0.2,r'$f_{1}=(1-a_{1}(t))*Dirac$')
    ax.text(-0.45,-0.3,r'$f_{2}=(-a_{2}(t))*Dirac$')
    ax.text(-0.45,-0.45,r'$Dirac = 1, GRF > 0.2; 0, otherwise $')

    # initialization function: plot the background of each frame
    def init():
        line1.set_data([], [])
        line2.set_data([], [])
        line3.set_data([], [])
        line4.set_data([], [])

        point1.set_data([], [])
        point2.set_data([], [])
        point3.set_data([], [])
        point4.set_data([], [])

        time_text.set_text('')
        energy_text.set_text('')
        return line1, line2, line3, line4, point1, point2, point3, point4, time_text, energy_text

    # animation function.  This is called sequentially
    def animate(i):
        index=i%(cpg_data.shape[0]-line_length)
        a_start=index; a_end=index+line_length;

        line1.set_data(cpg_data[a_start:a_end,0], cpg_data[a_start:a_end,1])
        point1.set_data(cpg_data[a_end,0], cpg_data[a_end,1])

        line2.set_data(cpg_data[a_start:a_end,2], cpg_data[a_start:a_end,3])
        point2.set_data(cpg_data[a_end,2], cpg_data[a_end,3])

        line3.set_data(cpg_data[a_start:a_end,4], cpg_data[a_start:a_end,5])
        point3.set_data(cpg_data[a_end,4], cpg_data[a_end,5])

        line4.set_data(cpg_data[a_start:a_end,6], cpg_data[a_start:a_end,7])
        point4.set_data(cpg_data[a_end,6], cpg_data[a_end,7])

        time_text.set_text('Time = %.1f [s]' % (index/60.0))
        angle1=math.atan2(cpg_data[a_end,1],cpg_data[a_end,0])-math.atan2(cpg_data[a_end,3],cpg_data[a_end,2])
        if angle1<0.0:
            angle1+=2*np.pi
        energy_text.set_text(r'$\Theta_{1,2}$ = %.2f' % (angle1))
        return line1, point1 ,line2, point2, line3, point3, line4, point4, time_text, energy_text

    # call the animator.  blit=True means only re-draw the parts that have changed.
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=(cpg_data.shape[0]-line_length), interval=50, blit=True)

    # save the animation as an mp4.  This requires ffmpeg or mencoder to be
    # installed.  The extra_args ensure that the x264 codec is used, so that
    # the video can be embedded in html5.  You may need to adjust this for
    # your system: for more information, see
    # http://matplotlib.sourceforge.net/api/animation_api.html

    #anim.save('non-continuous modulation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])
    plt.show()

def plot_phase_transition_animation(data_file_dic,start_point=90,end_point=1200,freq=60.0,experiment_classes=['0.0'],trail_id=0):
    ''' 
    This is for plot the phase diff transition that is shown by a small mive
    @param: data_file_dic, the folder of the data files, this path includes a log file which list all folders of the experiment data for display
    @param: start_point, the start point (time) of all the data
    @param: end_point, the end point (time) of all the data
    @param: freq, the sample frequency of the data 
    @param: experiment_classes, the conditions/cases/experiment_classes of the experimental data
    @param: trail_id, it indicates which experiment among a inclination/situation/case experiments 
    @return: show and save a data figure.
    '''
    # 1) read data
    datas_files_categories, categories=load_data_log(data_file_dic)

    cpg={}

    for class_name, files_name in datas_files_categories: #class_name is a files_name class_names
        cpg[class_name]=[]  #files_name is the table of the files_name class_name
        if class_name in experiment_classes:
            print(class_name)
            for idx in files_name.index:
                folder_class_name= data_file_dic + files_name['file_name'][idx]
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_class_name)
                # 2)  data process
                print(folder_class_name)
                cpg[class_name].append(cpg_data)

    #3) plot
    Animate_phase_transition(cpg[experiment_classes[0]][trail_id])
    
def PhaseAnalysis(data_file_dic,start_point=90,end_point=1200,freq=60.0,experiment_classes=['0.0'],trail_id=0):
    # 1) read data
    datas_files_categories, categories =load_data_log(data_file_dic)

    cpg={}
    current={}
    position={}

    for class_name, files_name in datas_files_categories: #class_name is a files_name class_names
        cpg[class_name]=[]  #files_name is the table of the files_name class_name
        current[class_name]=[]
        position[class_name]=[]
        print(class_name)
        for idx in files_name.index:
            folder_class_name= data_file_dic + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_class_name)
            # 2)  data process
            print(folder_class_name)
            cpg[class_name].append(cpg_data)
            current[class_name].append(current_data)
            position[class_name].append(position_data)

    #3) plot
    font_legend = {'family' : 'Arial',
                   'weight' : 'light',
                   'size'   : 10,
                   'style'  :'italic'
                  }
    font_label = {'family' : 'Arial',
                  'weight' : 'light',
                  'size'   : 12,
                  'style'  :'normal'
                 }

    font_title = {'family' : 'Arial',
                  'weight' : 'light',
                  'size'   : 12,
                  'style'  :'normal'
                 }

    figsize=(5.1,7.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.095,left=0.15,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:2,0]))
    axs.append(fig.add_subplot(gs1[2:3,0]))
    axs.append(fig.add_subplot(gs1[3:4,0]))
    axs.append(fig.add_subplot(gs1[4:5,0]))
    axs.append(fig.add_subplot(gs1[5:6,0]))

    #3.1) plot 

    idx=0
    axs[idx].plot(time,-1.0*pose_data[:,1],'b')
    #axs[idx].plot(time,joint_data[run_id].iloc[:,4],'b')
    axs[idx].legend([r'Pitch'], loc='upper left',prop=font_legend)
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].axis([time[0],time[-1],-0.15,0.35],'tight')
    axs[idx].set_xticklabels(labels=[])
    yticks=[-.15,0.0,.15,0.35]
    axs[idx].set_yticks(yticks)
    axs[idx].set_yticklabels(labels=[str(ytick) for ytick in yticks],fontweight='light')
    #axs[idx].set_yticklabels(labels=['-1.0','0.0','1.0'],fontweight='light')
    axs[idx].set_ylabel('Pitch [rad]',font_label)
    axs[idx].set_xticks([t for t in np.arange(time[0],time[-1],10,dtype='int')])
    #axs[idx].set_xticklabels(labels=[str(t) for t in np.arange(round(time[0]),round(time[-1]),10,dtype='int')],fontweight='light')
    #axs[idx].set_title("CPG outputs of the right front leg",font2)



    idx=1
    # plot the gait diagram
    #bax = brokenaxes(xlims=((76, 116), (146, 160)), hspace=.05, despine=False)
    #axs[idx]=bax


    #axs[idx].plot(time,current_data.iloc[start_point:end_point,26]/1000.0,'r')
    axs[idx].plot(time,lowPassFilter(current_data[:,2],0.1)/1000,'b')
    axs[idx].plot(time,lowPassFilter(position_data[:,2],0.1)/5.0,'r')
    axs[idx].legend([r'RF'], loc='upper left',prop=font_legend)
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].axis([time[0],time[-1],-0.1,0.51],'tight')
    axs[idx].set_xticklabels(labels=[])
    yticks=[-.1,0.0,0.25,0.5]
    axs[idx].set_yticks(yticks)
    axs[idx].set_yticklabels(labels=[str(ytick) for ytick in yticks],fontweight='light')
    axs[idx].set_ylabel('Knee joint\ncurrent [A]',font_label)
    axs[idx].set_xticks([t for t in np.arange(time[0],time[-1]+0.1,5,dtype='int')])
    #axs[idx].set_xticklabels(labels=[str(t) for t in np.arange(round(time[0]),round(time[-1]),10,dtype='int')],fontweight='light')
    #axs[idx].set_title("Adaptive control input term of the right front leg")

    idx=idx+1
    axs[idx].plot(time,lowPassFilter(current_data[:,5],0.1)/1000,'b')
    axs[idx].plot(time,lowPassFilter(position_data[:,5],0.1)/5.0,'r')
    axs[idx].legend([r'RH'], loc='upper left',prop=font_legend)
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].axis([time[0],time[-1],-0.1,0.51],'tight')
    axs[idx].set_xticklabels(labels=[])
    yticks=[-.1,0.0,0.25,0.5]
    axs[idx].set_yticks(yticks)
    axs[idx].set_yticklabels(labels=[str(ytick) for ytick in yticks],fontweight='light')
    axs[idx].set_ylabel('Knee joint\ncurrent [A]',font_label)
    #axs[idx].set_title("CPG outputs of the right front leg",font2)
    axs[idx].set_xticks([t for t in np.arange(time[0],time[-1]+0.1,5,dtype='int')])
    #axs[idx].set_xticklabels(labels=[str(t) for t in np.arange(round(time[0]),round(time[-1]),10,dtype='int')],fontweight='light')

    idx=idx+1
    axs[idx].plot(time,-1.0*lowPassFilter(current_data[:,8],0.1)/1000,'b')
    axs[idx].plot(time,lowPassFilter(position_data[:,8],0.1)/5.0,'r')
    axs[idx].legend([r'LF'], loc='upper left',prop=font_legend)
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].axis([time[0],time[-1],-0.1,0.51],'tight')
    yticks=[-.1,0.0,0.25,0.5]
    axs[idx].set_yticks(yticks)
    axs[idx].set_yticklabels(labels=[str(ytick) for ytick in yticks],fontweight='light')
    axs[idx].set_xticklabels(labels=[])
    axs[idx].set_ylabel('Knee joint\ncurrent [A]',font_label)
    #axs[idx].set_title("CPG outputs of the right front leg",font2)
    #axs[idx].set_xlabel('Time [s]',font_label)
    axs[idx].set_xticks([t for t in np.arange(time[0],time[-1]+0.1,5,dtype='int')])
    #axs[idx].set_xticklabels(labels=[str(t) for t in np.arange(round(time[0]),round(time[-1]),10,dtype='int')],fontweight='light')
    #axs[idx].set_title("Adaptive control input term of the right front leg")

    idx=idx+1
    axs[idx].plot(time,-1.0*lowPassFilter(current_data[:,11],0.1)/1000,'b')
    axs[idx].plot(time,lowPassFilter(position_data[:,11],0.1)/5.0,'r')
    axs[idx].legend([r'LH'], loc='upper left',prop=font_legend)
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].axis([time[0],time[-1],-0.1,0.51],'tight')
    yticks=[-.1,0.0,0.25,0.5]
    axs[idx].set_yticks(yticks)
    axs[idx].set_yticklabels(labels=[str(ytick) for ytick in yticks],fontweight='light')
    axs[idx].set_ylabel('Knee joint\ncurrent [A]',font_label)
    #axs[idx].set_title("CPG outputs of the right front leg",font2)
    axs[idx].set_xlabel('Time [s]',font_label)
    axs[idx].set_xticks([t for t in np.arange(time[0],time[-1]+0.1,5,dtype='int')])
    axs[idx].set_xticklabels(labels=[str(t) for t in np.arange(round(time[0]),round(time[-1])+0.1,5,dtype='int')],fontweight='light')



    #plt.savefig('/media/suntao/DATA/Research/P3_workspace/Figures/FigPhase/FigPhase_source222_position.svg')
    plt.show()


    fig = plt.figure()
    ax = plt.axes(projection="3d")

    ax.plot3D(time,cpg_data[:,0],cpg_data[:,1],'gray')
    ax.scatter3D(time,cpg_data[:,0],cpg_data[:,1],cmap='green')

    ax.plot3D(time,cpg_data[:,2],cpg_data[:,3],'gray')
    ax.scatter3D(time,cpg_data[:,2],cpg_data[:,3],cmap='blue')


    ax.plot3D(time,cpg_data[:,4],cpg_data[:,5],'gray')
    ax.scatter3D(time,cpg_data[:,4],cpg_data[:,5],cmap='red')


    ax.plot3D(time,cpg_data[:,6],cpg_data[:,7],'gray')
    ax.scatter3D(time,cpg_data[:,6],cpg_data[:,7],'+',cmap='yellow')
    #if cpg_data[:,1]==
    #if cpg_data[:,1]==
    ax.set_xlabel('Time[s]',font_label)
    ax.set_ylabel(r'$O_{1}$',font_label)
    ax.set_zlabel(r'$O_{2}$',font_label)
    ax.grid(which='both',axis='x',color='k',linestyle=':')
    ax.grid(which='both',axis='y',color='k',linestyle=':')
    ax.grid(which='both',axis='z',color='k',linestyle=':')


    fig2=plt.figure()
    ax2=fig2.add_subplot(1,1,1)
    ax2.plot(cpg_data[:,0],cpg_data[:,1],'r')
    ax2.plot(cpg_data[:,2],cpg_data[:,3],'g')
    ax2.plot(cpg_data[:,4],cpg_data[:,5],'b')
    ax2.plot(cpg_data[:,6],cpg_data[:,7],'y')
    ax2.plot(time,cpg_data[:,0],'r')
    ax2.plot(time,cpg_data[:,2],'g')
    ax2.plot(time,cpg_data[:,4],'b')
    ax2.plot(time,cpg_data[:,6],'y')
    ax2.grid(which='both',axis='x',color='k',linestyle=':')
    ax2.grid(which='both',axis='y',color='k',linestyle=':')
    ax2.set_xlabel(r'$O_{1}$',font_label)
    ax2.set_ylabel(r'$O_{2}$',font_label)

    fig3=plt.figure()
    ax31=fig3.add_subplot(4,1,1)
    ax31.plot(time, grf_data[:,0],'r')
    ax32=fig3.add_subplot(4,1,2)
    ax32.plot(time, grf_data[:,1],'r')
    ax33=fig3.add_subplot(4,1,3)
    ax33.plot(time, grf_data[:,2],'r')
    ax34=fig3.add_subplot(4,1,4)
    ax34.plot(time, grf_data[:,3],'r')

    plt.show()

def Phase_Gait(data_file_dic,start_point=90,end_point=1200,freq=60.0,experiment_classes=['0.0'],trail_id=0):
    ''' 
    This is for experiment two, for the first figure with one trail on inclination
    @param: data_file_dic, the folder of the data files, this path includes a log file which list all folders of the experiment data for display
    @param: start_point, the start point (time) of all the data
    @param: end_point, the end point (time) of all the data
    @param: freq, the sample frequency of the data 
    @param: experiment_classes, the conditions/cases/experiment_classes of the experimental data
    @param: trail_id, it indicates which experiment among a inclination/situation/case experiments 
    @return: show and save a data figure.
    '''
    # 1) read data
    datas_files_categories, categories=load_data_log(data_file_dic)

    gamma={}
    beta={}
    gait_diagram_data={}
    pitch={}
    pose={}
    jmc={}
    cpg={}
    noise={}

    for class_name, files_name in datas_files_categories: #class_name is a files_name class_names
        gamma[class_name]=[]  #files_name is the table of the files_name class_name
        gait_diagram_data[class_name]=[]
        beta[class_name]=[]
        pose[class_name]=[]
        jmc[class_name]=[]
        cpg[class_name]=[]
        noise[class_name]=[]
        print(class_name)
        for idx in files_name.index:
            folder_class_name= data_file_dic + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_class_name)
            # 2)  data process
            print(folder_class_name)
            gamma[class_name].append(COG_distribution(grf_data))

            gait_diagram_data_temp, beta_temp=gait(grf_data)
            gait_diagram_data[class_name].append(gait_diagram_data_temp); beta[class_name].append(beta_temp)

            pose[class_name].append(pose_data)
            jmc[class_name].append(command_data)
            cpg[class_name].append(cpg_data)
            noise[class_name].append(module_data)
            
            temp_1=min([len(bb) for bb in beta_temp]) #minimum steps of all legs
            beta_temp2=np.array([beta_temp[0][:temp_1],beta_temp[1][:temp_1],beta_temp[2][:temp_1],beta_temp[3][0:temp_1]]) # transfer to np array
            if(beta_temp2 !=[]):
                print("Coordination:",1.0/max(np.std(beta_temp2, axis=0)))
            else:
                print("Coordination:",0.0)

            print("Stability:",1.0/np.std(pose_data[:,0],axis=0))
            print("Displacemment:",np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,5]-pose_data[0,5],2))) #Displacement on slopes 
    #3) plot
    figsize=(6.2,3.0)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(2,len(experiment_classes))#13
    gs1.update(hspace=0.12,top=0.95,bottom=0.2,left=0.12,right=0.98)
    axs=[]
    for idx in range(len(experiment_classes)):# how many columns, depends on the experiment_classes
        axs.append(fig.add_subplot(gs1[0:1,idx]))
        axs.append(fig.add_subplot(gs1[1:2,idx]))
    
    #3.1) plot 

    for idx, inclination in enumerate(experiment_classes):


        axs[0].set_ylabel(u'Phase diff. [rad]')
        phi=calculate_phase_diff(cpg[inclination][trail_id],time)
        axs[3*idx+0].plot(phi['time'],phi['phi_12'],color=(77/255,133/255,189/255))
        axs[3*idx+0].plot(phi['time'],phi['phi_13'],color=(247/255,144/255,61/255))
        axs[3*idx+0].plot(phi['time'],phi['phi_14'],color=(89/255,169/255,90/255))
        axs[3*idx+0].legend([u'$\phi_{12}$',u'$\phi_{13}$',u'$\phi_{14}$'])
        axs[3*idx+0].grid(which='both',axis='x',color='k',linestyle=':')
        axs[3*idx+0].grid(which='both',axis='y',color='k',linestyle=':')
        axs[3*idx+0].set_yticks([0.0,1.5,3.0])
        axs[3*idx+0].set_xticklabels([])
        axs[3*idx+0].set(xlim=[min(time),max(time)])

        axs[1].set_ylabel(r'Gait')
        gait_diagram(fig,axs[3*idx+1],gs1,gait_diagram_data[inclination][trail_id])
        axs[3*idx+1].set_xlabel(u'Time [s]')
        xticks=np.arange(int(min(time)),int(max(time))+1,2)
        axs[3*idx+1].set_xticks(xticks)
        axs[3*idx+1].set_xticklabels([str(xtick) for xtick in xticks])
        axs[1].yaxis.set_label_coords(-0.07,.5)
        axs[3*idx+1].set(xlim=[min(time),max(time)])

    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'experiment2_1.svg'
    plt.savefig(figPath)

    plt.show()

def Phase_Gait_ForNoiseFeedback(data_file_dic,start_point=90,end_point=1200,freq=60.0,experiment_classes=['0.0'],trail_id=0):
    ''' 
    This is for experiment two, for the first figure with one trail on inclination
    @param: data_file_dic, the folder of the data files, this path includes a log file which list all folders of the experiment data for display
    @param: start_point, the start point (time) of all the data
    @param: end_point, the end point (time) of all the data
    @param: freq, the sample frequency of the data 
    @param: experiment_classes, the conditions/cases/experiment_classes of the experimental data
    @param: trail_id, it indicates which experiment among a inclination/situation/case experiments 
    @return: show and save a data figure.
    '''
    # 1) read data
    datas_files_categories, categories=load_data_log(data_file_dic)

    gamma={}
    beta={}
    gait_diagram_data={}
    pitch={}
    pose={}
    jmc={}
    cpg={}
    noise={}

    pdb.set_trace()
    for class_name, files_name in datas_files_categories[datas_files_categories['experiment_classes']==experiment_classes[0]]: #class_name is a files_name class_names
        gamma[class_name]=[]  #files_name is the table of the files_name class_name
        gait_diagram_data[class_name]=[]
        beta[class_name]=[]
        pose[class_name]=[]
        jmc[class_name]=[]
        cpg[class_name]=[]
        noise[class_name]=[]
        print(class_name)
        for idx in files_name.index:
            folder_class_name = data_file_dic + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_class_name)
            # 2)  data process
            print(folder_class_name)
            gamma[class_name].append(COG_distribution(grf_data-module_data[:,1:]))

            gait_diagram_data_temp, beta_temp=gait(grf_data-module_data[:,1:])
            gait_diagram_data[class_name].append(gait_diagram_data_temp); beta[class_name].append(beta_temp)

            pose[class_name].append(pose_data)
            jmc[class_name].append(command_data)
            cpg[class_name].append(cpg_data)
            noise[class_name].append(module_data)
            
            temp_1=min([len(bb) for bb in beta_temp]) #minimum steps of all legs
            beta_temp2=np.array([beta_temp[0][:temp_1],beta_temp[1][:temp_1],beta_temp[2][:temp_1],beta_temp[3][0:temp_1]]) # transfer to np array
            if(beta_temp2 !=[]):
                print("Coordination:",1.0/max(np.std(beta_temp2, axis=0)))
            else:
                print("Coordination:",0.0)

            print("Stability:",1.0/np.std(pose_data[:,0],axis=0))
            print("Displacemment:",np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,5]-pose_data[0,5],2))) #Displacement on slopes 
    #3) plot
    figsize=(6.2,3.0)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(2,len(experiment_classes))#13
    gs1.update(hspace=0.12,top=0.95,bottom=0.2,left=0.12,right=0.98)
    axs=[]
    for idx in range(len(experiment_classes)):# how many columns, depends on the experiment_classes
        axs.append(fig.add_subplot(gs1[0:1,idx]))
        axs.append(fig.add_subplot(gs1[1:2,idx]))
    
    #3.1) plot 

    for idx, inclination in enumerate(experiment_classes):
        axs[0].set_ylabel(u'Phase diff. [rad]')
        phi=calculate_phase_diff(cpg[inclination][trail_id],time)
        axs[3*idx+0].plot(phi['time'],phi['phi_12'],color=(77/255,133/255,189/255))
        axs[3*idx+0].plot(phi['time'],phi['phi_13'],color=(247/255,144/255,61/255))
        axs[3*idx+0].plot(phi['time'],phi['phi_14'],color=(89/255,169/255,90/255))
        axs[3*idx+0].legend([u'$\phi_{12}$',u'$\phi_{13}$',u'$\phi_{14}$'])
        axs[3*idx+0].grid(which='both',axis='x',color='k',linestyle=':')
        axs[3*idx+0].grid(which='both',axis='y',color='k',linestyle=':')
        axs[3*idx+0].set_yticks([0.0,1.5,3.0])
        axs[3*idx+0].set_xticklabels([])
        axs[3*idx+0].set(xlim=[min(time),max(time)])

        axs[1].set_ylabel(r'Gait')
        gait_diagram(fig,axs[3*idx+1],gs1,gait_diagram_data[inclination][trail_id])
        axs[3*idx+1].set_xlabel(u'Time [s]')
        xticks=np.arange(int(min(time)),int(max(time))+1,2)
        axs[3*idx+1].set_xticks(xticks)
        axs[3*idx+1].set_xticklabels([str(xtick) for xtick in xticks])
        axs[1].yaxis.set_label_coords(-0.07,.5)
        axs[3*idx+1].set(xlim=[min(time),max(time)])

    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'experiment2_1.svg'
    plt.savefig(figPath)

    plt.show()

def neural_preprocessing(data):
    '''
    This is use a recurrent neural network to preprocessing the data,
    it works like a filter
    '''
    new_data=[]
    w_i=20
    w_r=7.2
    bias=-6.0
    new_d_old =0.0
    for d in data:
        new_a=w_i*d+w_r*new_d_old + bias
        new_d=1.0/(1.0+math.exp(-new_a))
        new_data.append(new_d)
        new_d_old=new_d
    return np.array(new_data)

def forceForwardmodel(data):
    '''
    This is a forward model, it use a joint command (hip joint) to 
    map an expected ground reaction force
    '''
    new_data=[]
    alpha = 1.0
    gamma = 0.99
    d_old=data[0]
    out_old=0.0
    for d in data:
        if d < d_old:
            G=1.0
        else:
            G=0.0
        out= alpha*(gamma*G + (1-gamma)*out_old)
        d_old=d
        out_old=out
        new_data.append(out)

    return np.array(new_data)

def touch_difference(joint_cmd, actual_grf):
    '''
    Compare the diff between the expected grf and actual grf, where expected grf is calculated by the hip jointmovoemnt commands

    '''

    assert(joint_cmd.shape[1]==4)
    assert(actual_grf.shape[1]==4)

    new_expected_grf = np.zeros(joint_cmd.shape)
    new_actual_grf = np.zeros(actual_grf.shape)
    joint_cmd_middle_position=[]

    #
    for idx in range(4):
        joint_cmd_middle_position.append((np.amax(joint_cmd[:,idx])+np.amin(joint_cmd[:,idx]))/2.0)
        new_expected_grf[:,idx] = forceForwardmodel(joint_cmd[:,idx])
        new_actual_grf[:,idx] = neural_preprocessing(actual_grf[:,idx])
    # pre process again
    threshold=0.2
    new_expected_grf = new_expected_grf > threshold
    new_actual_grf = new_actual_grf > threshold
    #
    move_stage = joint_cmd > joint_cmd_middle_position

    # transfer the GRF into bit , to get stance and swing phase
    new_actual_grf=new_actual_grf.astype(np.int)
    new_expected_grf=new_expected_grf.astype(np.int)
    # calculate the difference between the expected and actual swing/stance
    diff = new_actual_grf-new_expected_grf

    Te1=(diff*move_stage==1)
    Te3=(diff*move_stage==-1)
    Te2=(diff*(~move_stage)==1)
    Te4=(diff*(~move_stage)==-1)
    pdb.set_trace()
    return [new_expected_grf, new_actual_grf, diff, Te1, Te2, Te3, Te4]

def getTouchData(data_file_dic,start_point=900,end_point=1200,freq=60,experiment_classes=['0.0']):
    '''
    calculating touch momemnt
    '''
    # 1) read data
    datas_files_categories, categories=load_data_log(data_file_dic)
    Te={}
    Te1={}
    Te2={}
    Te3={}
    Te4={}
    for class_name, files_name in datas_files_categories: #class_name is a files_name class_names
        Te[class_name] =[]
        Te1[class_name]=[]  #inclination is the table of the inclination name
        Te2[class_name]=[]
        Te3[class_name]=[]
        Te4[class_name]=[]
        print(class_name)
        for idx in files_name.index:
            folder_class_name= data_file_dic + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_class_name)
            # 2)  data process
            print(folder_class_name)
            Te_temp=touch_difference(cpg_data[:,[0,2,4,6]], grf_data)
            Te1[class_name].append(sum(Te_temp[3])/freq)
            Te2[class_name].append(sum(Te_temp[4])/freq)
            Te3[class_name].append(sum(Te_temp[5])/freq)
            Te4[class_name].append(sum(Te_temp[6])/freq)
            Te[class_name].append([Te_temp,command_data])

    return Te, Te1, Te2,Te3, Te4

def plot_comparasion_of_expected_actual_grf(Te, leg_id,ax=None):
    jmc=Te[1]
    Te=Te[0]
    axs=[]
    if ax==None:
        figsize=(7.1,6.1244)
        fig = plt.figure(figsize=figsize,constrained_layout=False)
        gs1=gridspec.GridSpec(6,1)#13
        gs1.update(hspace=0.18,top=0.95,bottom=0.095,left=0.15,right=0.98)
        axs.append(fig.add_subplot(gs1[0:6,0]))
    else:
        axs.append(ax)

    time=np.linspace(0,len(Te[0])/60,len(Te[0]))
    axs[0].plot(time,Te[3][:,leg_id],'r*')
    axs[0].plot(time,Te[4][:,leg_id],'ro')
    axs[0].plot(time,Te[5][:,leg_id],'b*')
    axs[0].plot(time,Te[6][:,leg_id],'bo')
    #axs[0].plot(Te[2][:,leg_id],'k:')

    axs[0].plot(time,0.5*Te[0][:,leg_id],'b-.')
    axs[0].plot(time,0.5*Te[1][:,leg_id],'r-.')
    #axs[0].plot(time,0.5*jmc[:,3*leg_id+1],'g-.')
    axs[0].legend(['Te1','Te2', 'Te3', 'Te4','Expected GRF','Actual GRF'],ncol=3,loc='center',bbox_to_anchor=(0.5,0.8))
    axs[0].grid(which='both',axis='x',color='k',linestyle=':')
    axs[0].grid(which='both',axis='y',color='k',linestyle=':')
    axs[0].set_xlabel('Time [s]')
    ticks=np.arange(int(max(time)))
    axs[0].set_xticks(ticks)
    axs[0].set_xticklabels([str(tick) for tick in ticks])

def plot_comparasion_expected_actual_grf_all_leg(data_file_dic,start_point=600,end_point=1200,freq=60,experiment_classes=['0.0']):
    '''
    compare expected and actual ground reaction force

    '''
    Te, Te1, Te2,Te3,Te4 = getTouchData(data_file_dic,start_point,end_point,freq,experiment_classes)

    figsize=(9.1,11.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(8,len(experiment_classes))#13
    gs1.update(hspace=0.24,top=0.95,bottom=0.07,left=0.1,right=0.98)
    axs=[]
    for idx in range(len(experiment_classes)):# how many columns, depends on the experiment_classes
        axs.append(fig.add_subplot(gs1[0:2,idx]))
        axs.append(fig.add_subplot(gs1[2:4,idx]))
        axs.append(fig.add_subplot(gs1[4:6,idx]))
        axs.append(fig.add_subplot(gs1[6:8,idx]))

    for idx,inclination in enumerate(experiment_classes):
        pdb.set_trace()
        plot_comparasion_of_expected_actual_grf(Te[inclination][0],leg_id=0,ax=axs[4*idx])
        plot_comparasion_of_expected_actual_grf(Te[inclination][0],leg_id=1,ax=axs[4*idx+1])
        plot_comparasion_of_expected_actual_grf(Te[inclination][0],leg_id=2,ax=axs[4*idx+2])
        plot_comparasion_of_expected_actual_grf(Te[inclination][0],leg_id=3,ax=axs[4*idx+3])
    plt.show()

def calculate_phase_diff(CPGs_output,time):
    '''
    calculating phase difference bewteen  C12, C13, C14
    @param: CPGs_output, numpy darray n*8
    @return phi, DataFrame N*4, [time, phi_12, phi_13, phi_14]

    '''
    phi=pd.DataFrame(columns=['time','phi_12','phi_13','phi_14'])
    C1=CPGs_output[:,0:2]
    C2=CPGs_output[:,2:4]
    C3=CPGs_output[:,4:6]
    C4=CPGs_output[:,6:8]

    # phi_12
    temp1=np.sum(C1*C2,axis=1)
    temp2=np.sqrt(np.sum(C1**2,axis=1))*np.sqrt(np.sum(C2**2,axis=1))
    cos=temp1/temp2
    cos = np.clip(cos, -1, 1) # set the cos in range [-1,1]
    phi_12=np.arccos(cos)

    # phi_13
    temp1=np.sum(C1*C3,axis=1)
    temp2=np.sqrt(np.sum(C1**2,axis=1))*np.sqrt(np.sum(C3**2,axis=1))
    cos=temp1/temp2
    cos = np.clip(cos, -1, 1) # set the cos in range [-1,1]
    phi_13=np.arccos(cos)

    # phi_14
    temp1=np.sum(C1*C4,axis=1)
    temp2=np.sqrt(np.sum(C1**2,axis=1))*np.sqrt(np.sum(C4**2,axis=1))
    cos=temp1/temp2
    cos = np.clip(cos, -1, 1) # set the cos in range [-1,1]
    phi_14=np.arccos(cos)

    data=np.concatenate((time.reshape((-1,1)),phi_12.reshape((-1,1)),phi_13.reshape((-1,1)),phi_14.reshape((-1,1))),axis=1)
    data=pd.DataFrame(data,columns=['time','phi_12','phi_13','phi_14'])
    phi=pd.concat([phi,data])

    return phi

def phase_diff_stability(cpg_data,time):
    '''
    Calculation the stability of the phase diff

    '''
    phi = calculate_phase_diff(cpg_data,time)
    filter_width=50# the roll_out width
    phi_stability=[]
    for idx in range(phi.shape[0]):
        if idx>=filter_width:
            temp= filter_width 
        else:
            temp=idx
            
        std_phi=np.std(phi.loc[idx-temp:idx])
        phi_stability.append(sum(std_phi[1:]))


    return phi_stability

def plot_phase_diff(data_file_dic,start_point=90,end_point=1200,freq=60.0,experiment_classes=['0.0'],trail_id=0):
    ''' 
    This is for plot the phase diff by a plot curve
    @param: data_file_dic, the folder of the data files, this path includes a log file which list all folders of the experiment data for display
    @param: start_point, the start point (time) of all the data
    @param: end_point, the end point (time) of all the data
    @param: freq, the sample frequency of the data 
    @param: experiment_classes, the conditions/cases/experiment_classes of the experimental data
    @param: trail_id, it indicates which experiment among a inclination/situation/case experiments 
    @return: show and save a data figure.
    '''
    # 1) read data
    datas_files_categories, categories=load_data_log(data_file_dic)

    cpg={}

    for class_name, files_name in datas_files_categories: #class_name is a files_name class_names
        cpg[class_name]=[]  #files_name is the table of the files_name class_name
        if class_name in experiment_classes:
            print(class_name)
            for idx in files_name.index:
                folder_class_name= data_file_dic + files_name['file_name'][idx]
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_class_name)
        # 2)  data process
                print(folder_class_name)
                cpg[class_name].append(cpg_data)


    # 2) calculate the phase angles
    phi=pd.DataFrame(columns=['time','phi_12','phi_13','phi_14'])
    for idx in range(len(cpg[experiment_classes[0]])):
        trail_id=idx
        phi=pd.concat([phi,calculate_phase_diff(cpg[experiment_classes[0]][trail_id],time)])

    #3) plot
    figsize=(5.5,7.)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(9,len(experiment_classes))#13
    gs1.update(hspace=0.13,top=0.95,bottom=0.1,left=0.11,right=0.98)
    axs=[]
    for idx in range(len(experiment_classes)):# how many columns, depends on the experiment_classes
        axs.append(fig.add_subplot(gs1[0:9,idx]))


    sns.lineplot(x='time',y='phi_12',data=phi,ax=axs[0])
    sns.lineplot(x='time',y='phi_13',data=phi,ax=axs[0])
    sns.lineplot(x='time',y='phi_14',data=phi,ax=axs[0])
    axs[0].legend(['$\phi_{12}$','$\phi_{13}$','$\phi_{14}$'])

    #pdb.set_trace()
    #plt.plot(phi_12)
    #plt.plot(phi_13)
    #plt.plot(phi_14)
    plt.show()

def plot_actual_grf_all_leg(data_file_dic,start_point=600,end_point=1200,freq=60,experiment_classes=['0'], trail_id=0):
    '''
    Comparing all legs' actual ground reaction forces

    '''

    # 1) read data
    datas_files_categories, categories=load_data_log(data_file_dic)
    grf={}
    for class_name, files_name in datas_files_categories: #class_name is a files_name class_names
        if class_name in experiment_classes:
            print(class_name)
            grf[class_name]=[]
            for idx in files_name.index:
                folder_class_name= data_file_dic + files_name['file_name'][idx]
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_class_name)
                # 2)  data process
                grf[class_name].append(grf_data)
                print(folder_class_name)
    
    # 2) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(8,len(experiment_classes))#13
    gs1.update(hspace=0.24,top=0.95,bottom=0.07,left=0.1,right=0.99)
    axs=[]
    for idx in range(len(experiment_classes)):# how many columns, depends on the experiment_classes
        axs.append(fig.add_subplot(gs1[0:8,idx]))

    for idx,inclination in enumerate(experiment_classes):
        axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
        axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
        grf_diagram(fig,axs[idx],gs1, grf[inclination][idx],time)
    plt.show()

def GeneralDisplay(data_file_dic,start_point=90,end_point=1200,freq=60.0,experiment_classes=['0.0'],trail_id=0):
    ''' 
    This is for experiment two, for the first figure with one trail on inclination
    @param: data_file_dic, the folder of the data files, this path includes a log file which list all folders of the experiment data for display
    @param: start_point, the start point (time) of all the data
    @param: end_point, the end point (time) of all the data
    @param: freq, the sample frequency of the data 
    @param: experiment_classes, the conditions/cases/experiment_classes of the experimental data
    @param: trail_id, it indicates which experiment among a inclination/situation/case experiments 
    @return: show and save a data figure.
    '''
    # 1) read data
    datas_files_categories, categories=load_data_log(data_file_dic)

    gamma={}
    beta={}
    gait_diagram_data={}
    pitch={}
    pose={}
    jmc={}
    jmp={}
    jmv={}
    jmf={}
    cpg={}
    noise={}

    for class_name, files_name in datas_files_categories: #class_name is a files_name class_names
        gamma[class_name]=[]  #files_name is the table of the files_name class_name
        gait_diagram_data[class_name]=[]
        beta[class_name]=[]
        pose[class_name]=[]
        jmc[class_name]=[]
        jmp[class_name]=[]
        jmv[class_name]=[]
        jmf[class_name]=[]
        cpg[class_name]=[]
        noise[class_name]=[]
        if class_name in experiment_classes:
            print(class_name)
            for idx in files_name.index:
                folder_class_name= data_file_dic + files_name['file_name'][idx]
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_class_name)
                # 2)  data process
                print(folder_class_name)
                gamma[class_name].append(COG_distribution(grf_data))
                gait_diagram_data_temp, beta_temp = gait(grf_data)
                gait_diagram_data[class_name].append(gait_diagram_data_temp); beta[class_name].append(beta_temp)
                pose[class_name].append(pose_data)
                jmc[class_name].append(command_data)
                jmp[class_name].append(position_data)
                jmf[class_name].append(current_data)
                cpg[class_name].append(cpg_data)
                noise[class_name].append(module_data)
                temp_1=min([len(bb) for bb in beta_temp]) #minimum steps of all legs
                beta_temp2=np.array([beta_temp[0][:temp_1],beta_temp[1][:temp_1],beta_temp[2][:temp_1],beta_temp[3][0:temp_1]]) # transfer to np array
                if(beta_temp2 !=[]):
                    print("Coordination:",1.0/max(np.std(beta_temp2, axis=0)))
                else:
                    print("Coordination:",0.0)

                print("Stability:", 1.0/np.std(pose_data[:,0],axis=0) + 1.0/np.std(pose_data[:,1], axis=0))
                print("Displacemment:",np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,4]-pose_data[0,4],2))) #Displacement on slopes 
                print("Displacemment:",np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,4]-pose_data[0,4],2))) #Displacement on slopes 

                velocity_data=(position_data[1:,:]-position_data[0:-1,:])*freq
                initial_velocity=[0,0,0, 0,0,0, 0,0,0, 0,0,0]
                velocity_data=np.vstack([initial_velocity,velocity_data])
                jmv[class_name].append(velocity_data)
                print("EnergyCost:", EnergyCost(velocity_data,current_data,freq))
                #pdb.set_trace()

            
    #3) plot
    figsize=(8.2,6.5)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,len(experiment_classes))#13
    gs1.update(hspace=0.12,top=0.95,bottom=0.09,left=0.12,right=0.98)
    axs=[]
    for idx in range(len(experiment_classes)):# how many columns, depends on the experiment_classes
        axs.append(fig.add_subplot(gs1[0:1,idx]))
        axs.append(fig.add_subplot(gs1[1:2,idx]))
        axs.append(fig.add_subplot(gs1[2:3,idx]))
        axs.append(fig.add_subplot(gs1[3:4,idx]))
        axs.append(fig.add_subplot(gs1[4:5,idx]))
        axs.append(fig.add_subplot(gs1[5:6,idx]))
    
    #3.1) plot 
    situations={'0':'Normal', '1':'Carring payload', '2':'Malfunction leg', '3':'Noisy feedback','0.9':'0.9'}
    
    experiment_category=experiment_classes[0]# The first category of the input parameters (arg)
    idx=0
    axs[idx].plot(time,cpg[experiment_category][trail_id][:,1], color=(46/255.0, 77/255.0, 129/255.0))
    axs[idx].plot(time,cpg[experiment_category][trail_id][:,3], color=(0/255.0, 198/255.0, 156/255.0))
    axs[idx].plot(time,cpg[experiment_category][trail_id][:,5], color=(255/255.0, 1/255.0, 118/255.0))
    axs[idx].plot(time,cpg[experiment_category][trail_id][:,7], color=(225/255.0, 213/255.0, 98/255.0))
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_ylabel(u'CPGs')
    axs[idx].set_yticks([-1.0,0.0,1.0])
    axs[idx].legend(['RF','RH','LF', 'LH'],ncol=4)
    axs[idx].set_xticklabels([])
    axs[idx].set_title(data_file_dic[79:-1]+": " + situations[experiment_classes[0]] +" "+str(trail_id))
    axs[idx].set(xlim=[min(time),max(time)])

    idx=1
    axs[idx].set_ylabel(u'Atti. [deg]')
    axs[idx].plot(time,pose[experiment_category][trail_id][:,0]*-57.3,color=(129/255.0,184/255.0,223/255.0))
    axs[idx].plot(time,pose[experiment_category][trail_id][:,1]*-57.3,color=(254/255.0,129/255.0,125/255.0))
    axs[idx].plot(time,pose[experiment_category][trail_id][:,2]*-57.3,color=(86/255.0,169/255.0,90/255.0))
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_yticks([-5.0,0.0,5.0])
    axs[idx].legend(['Roll','Pitch','Yaw'],loc='upper left')
    axs[idx].set_xticklabels([])
    axs[idx].set(xlim=[min(time),max(time)])


    idx=2
    axs[idx].set_ylabel(u'Disp. [m]')
    displacement_x = pose[experiment_category][trail_id][:,3] #Displacement on slopes 
    displacement_y = pose[experiment_category][trail_id][:,4] #Displacement on slopes 
    axs[idx].plot(time,displacement_x,'r')
    axs[idx].plot(time,displacement_y,'b')
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].legend(['X-axis','Y-axis'],loc='upper left')
    axs[idx].set_xticklabels([])
    axs[idx].set(xlim=[min(time),max(time)])

    idx=3
    axs[idx].set_ylabel(u'Phase diff. [rad]')
    phi=calculate_phase_diff(cpg[experiment_category][trail_id],time)
    axs[idx].plot(phi['time'],phi['phi_12'],color=(77/255,133/255,189/255))
    axs[idx].plot(phi['time'],phi['phi_13'],color=(247/255,144/255,61/255))
    axs[idx].plot(phi['time'],phi['phi_14'],color=(89/255,169/255,90/255))
    axs[idx].legend([u'$\phi_{12}$',u'$\phi_{13}$',u'$\phi_{14}$'])
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_yticks([0.0,1.5,3.0])
    axs[idx].set_xticklabels([])
    axs[idx].set(xlim=[min(time),max(time)])
#
#
#    idx=4
#    axs[idx].set_ylabel(u'Noise [rad]')
#    axs[idx].plot(time,noise[experiment_category][trail_id][:,1], 'r')
#    axs[idx].plot(time,noise[experiment_category][trail_id][:,2], 'g')
#    axs[idx].plot(time,noise[experiment_category][trail_id][:,3], 'y')
#    axs[idx].plot(time,noise[experiment_category][trail_id][:,4], 'y')
#    axs[idx].legend(['N1','N2','N3','N4'])
#    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
#    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
#    axs[idx].set_yticks([-0.3, 0.0, 0.3])
#    axs[idx].set_xticklabels([])
#    axs[idx].set(xlim=[min(time),max(time)])
#

    idx=4
    axs[idx].set_ylabel(u'Joint poistion and 1000*velocity [rad]')
    axs[idx].plot(time,jmf[experiment_category][trail_id][:,1], 'r')
    axs[idx].plot(time,jmv[experiment_category][trail_id][:,1]*1000, 'g')
    axs[idx].legend(['N1','N2'])
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    #axs[idx].set_yticks([-0.3, 0.0, 0.3])
    axs[idx].set_xticklabels([])
    axs[idx].set(xlim=[min(time),max(time)])

    idx=5
    axs[idx].set_ylabel(r'Gait')
    gait_diagram(fig,axs[idx],gs1,gait_diagram_data[experiment_category][trail_id])
    axs[idx].set_xlabel(u'Time [s]')
    xticks=np.arange(int(min(time)),int(max(time))+1,2)
    axs[idx].set_xticklabels([str(xtick) for xtick in xticks])
    axs[idx].set_xticks(xticks)
    axs[idx].yaxis.set_label_coords(-0.09,.5)
    axs[idx].set(xlim=[min(time),max(time)])

    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'general_display.svg'
    plt.savefig(figPath)

    plt.show()

def GeneralDisplay_All(data_file_dic,start_point=90,end_point=1200,freq=60.0,experiment_classes=['0.0'],trail_id=0):
    ''' 
    This is for experiment two, for the first figure with one trail on inclination
    @param: data_file_dic, the folder of the data files, this path includes a log file which list all folders of the experiment data for display
    @param: start_point, the start point (time) of all the data
    @param: end_point, the end point (time) of all the data
    @param: freq, the sample frequency of the data 
    @param: experiment_classes, the conditions/cases/experiment_classes of the experimental data
    @param: trail_id, it indicates which experiment among a inclination/situation/case experiments 
    @return: show and save a data figure.
    '''
    # 1) read data
    datas_files_categories, categories=load_data_log(data_file_dic)

    gamma={}
    beta={}
    gait_diagram_data={}
    pitch={}
    pose={}
    jmc={}
    jmp={}
    jmv={}
    jmf={}
    grf={}
    cpg={}
    noise={}

    for class_name, files_name in datas_files_categories: #class_name is a files_name class_names
        gamma[class_name]=[]  #files_name is the table of the files_name class_name
        gait_diagram_data[class_name]=[]
        beta[class_name]=[]
        pose[class_name]=[]
        jmc[class_name]=[]
        jmp[class_name]=[]
        jmv[class_name]=[]
        jmf[class_name]=[]
        grf[class_name]=[]
        cpg[class_name]=[]
        noise[class_name]=[]
        if class_name in experiment_classes:
            print(class_name)
            for idx in files_name.index:
                folder_class_name= data_file_dic + files_name['file_name'][idx]
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_class_name)
                # 2)  data process
                print(folder_class_name)
                gamma[class_name].append(COG_distribution(grf_data))
                gait_diagram_data_temp, beta_temp = gait(grf_data)
                gait_diagram_data[class_name].append(gait_diagram_data_temp); beta[class_name].append(beta_temp)
                pose[class_name].append(pose_data)
                jmc[class_name].append(command_data)
                jmp[class_name].append(position_data)
                jmf[class_name].append(current_data)
                grf[class_name].append(grf_data)
                cpg[class_name].append(cpg_data)
                noise[class_name].append(module_data)
                temp_1=min([len(bb) for bb in beta_temp]) #minimum steps of all legs
                beta_temp2=np.array([beta_temp[0][:temp_1],beta_temp[1][:temp_1],beta_temp[2][:temp_1],beta_temp[3][0:temp_1]]) # transfer to np array
                if(beta_temp2 !=[]):
                    print("Coordination:",1.0/max(np.std(beta_temp2, axis=0)))
                else:
                    print("Coordination:",0.0)

                print("Stability:", 1.0/np.std(pose_data[:,0],axis=0) + 1.0/np.std(pose_data[:,1], axis=0))
                displacemment=np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,4]-pose_data[0,4],2)) #Displacement
                print("Displacemment:",displacemment) #Displacement

                distance=0
                for step_index in range(pose_data.shape[0]-1):
                    distance+=np.sqrt(pow(pose_data[step_index+1,3]-pose_data[step_index,3],2)+pow(pose_data[step_index+1,4]-pose_data[step_index,4],2))
                print("Distance:",distance) #Distance 

                velocity_data=(position_data[1:,:]-position_data[0:-1,:])*freq
                initial_velocity=[0,0,0, 0,0,0, 0,0,0, 0,0,0]
                velocity_data=np.vstack([initial_velocity,velocity_data])
                jmv[class_name].append(velocity_data)
                print("EnergyCost:", EnergyCost(velocity_data,current_data,freq))
                print("COT:", EnergyCost(velocity_data,current_data,freq)/(2.5*9.8*displacemment))

                grf_stance = grf_data > 0.06# GRF is bigger than 0.06, we see the robot starts to interact weith the ground
                grf_stance_index=np.where(grf_stance.sum(axis=1)==4)# Find the drop on ground moment
                phi_stability=phase_diff_stability(cpg_data[grf_stance_index[0][0]:,:],time[grf_stance_index[0][0]:])     
                phi_stability_threshold=0.7# empirically set
                for idx, value in enumerate(phi_stability): #which step 
                    if idx>=len(phi_stability)-1: # Not converge happen
                        convergenTime=len(phi_stability)/freq
                        break
                    if (value > phi_stability_threshold) and (phi_stability[idx+1] < phi_stability_threshold):# meet convergence condition
                        convergenTime=idx/freq
                        break
                print("Convergence time:", convergenTime)


    #3) plot
    figsize=(8.2,9)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(23,len(experiment_classes))#13
    gs1.update(hspace=0.14,top=0.97,bottom=0.06,left=0.1,right=0.98)
    axs=[]
    for idx in range(len(experiment_classes)):# how many columns, depends on the experiment_classes
        axs.append(fig.add_subplot(gs1[0:3,idx]))
        axs.append(fig.add_subplot(gs1[3:6,idx]))
        axs.append(fig.add_subplot(gs1[6:9,idx]))
        axs.append(fig.add_subplot(gs1[9:12,idx]))
        axs.append(fig.add_subplot(gs1[12:15,idx]))
        axs.append(fig.add_subplot(gs1[15:18,idx]))
        axs.append(fig.add_subplot(gs1[18:21,idx]))
        axs.append(fig.add_subplot(gs1[21:23,idx]))

    #3.1) plot 
    situations={'0':'Normal', '1':'Carring payload', '2':'Malfunction leg', '3':'Noisy feedback'}
    
    c4_1color=(46/255.0, 77/255.0, 129/255.0)
    c4_2color=(0/255.0, 198/255.0, 156/255.0)
    c4_3color=(255/255.0, 1/255.0, 118/255.0)
    c4_4color=(225/255.0, 213/255.0, 98/255.0)
    experiment_category=experiment_classes[0]# The first category of the input parameters (arg)
    if not situations.__contains__(experiment_category):
        situations[experiment_category]=experiment_category

    idx=0
    pdb.set_trace()
    axs[idx].plot(time,cpg[experiment_category][trail_id][:,1], color=c4_1color)
    axs[idx].plot(time,cpg[experiment_category][trail_id][:,3], color=c4_2color)
    axs[idx].plot(time,cpg[experiment_category][trail_id][:,5], color=c4_3color)
    axs[idx].plot(time,cpg[experiment_category][trail_id][:,7], color=c4_4color)
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_ylabel(u'CPGs')
    axs[idx].set_yticks([-1.0,0.0,1.0])
    axs[idx].legend(['RF','RH','LF', 'LH'],ncol=4)
    axs[idx].set_xticklabels([])
    axs[idx].set_title(data_file_dic[79:-1]+": " + situations[experiment_classes[0]] +" "+str(trail_id))
    axs[idx].set(xlim=[min(time),max(time)])


    idx=1
    axs[idx].set_ylabel(u'Phase diff. [rad]')
    phi=calculate_phase_diff(cpg[experiment_category][trail_id],time)
    phi_stability=phase_diff_stability(cpg[experiment_category][trail_id],time); 
    axs[idx].plot(phi['time'],phi['phi_12'],color=(77/255,133/255,189/255))
    axs[idx].plot(phi['time'],phi['phi_13'],color=(247/255,144/255,61/255))
    axs[idx].plot(phi['time'],phi['phi_14'],color=(89/255,169/255,90/255))
    axs[idx].plot(phi['time'],phi_stability,color='k')
    axs[idx].legend([u'$\phi_{12}$',u'$\phi_{13}$',u'$\phi_{14}$',u'$\phi_{std}$'],ncol=2)
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_yticks([0.0,0.7,1.5,2.1,3.0])
    axs[idx].set_xticklabels([])
    axs[idx].set(xlim=[min(time),max(time)])

    idx=2
    axs[idx].set_ylabel(u'Torque [Nm]')
    axs[idx].plot(time,jmf[experiment_category][trail_id][:,0], color=(129/255.0,184/255.0,223/255.0) )
    axs[idx].plot(time,jmf[experiment_category][trail_id][:,2],  color=(254/255.0,129/255.0,125/255.0))
    axs[idx].legend(['RF hip','RF knee'])
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    #axs[idx].set_yticks([-0.3, 0.0, 0.3])
    axs[idx].set_xticklabels([])
    axs[idx].set(xlim=[min(time),max(time)])


    idx=3
    axs[idx].set_ylabel(u'Atti. [deg]')
    axs[idx].plot(time,pose[experiment_category][trail_id][:,0]*-57.3,color=(129/255.0,184/255.0,223/255.0))
    axs[idx].plot(time,pose[experiment_category][trail_id][:,1]*-57.3,color=(254/255.0,129/255.0,125/255.0))
    #axs[idx].plot(time,pose[experiment_category][trail_id][:,2]*-57.3,color=(86/255.0,169/255.0,90/255.0))
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_yticks([-5.0,0.0,5.0])
    axs[idx].legend(['Roll','Pitch'],loc='upper left')
    axs[idx].set_xticklabels([])
    axs[idx].set(xlim=[min(time),max(time)])


    idx=4
    axs[idx].set_ylabel(u'Disp. [m]')
    displacement_x = pose[experiment_category][trail_id][:,3]  -  pose[experiment_category][trail_id][0,3] #Displacement along x axis
    displacement_y = pose[experiment_category][trail_id][:,4]  -  pose[experiment_category][trail_id][0,4] #Displacement along y axis
    axs[idx].plot(time,displacement_x, color=(129/255.0,184/255.0,223/255.0))
    axs[idx].plot(time,displacement_y, color=(254/255.0,129/255.0,125/255.0))
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].legend(['X-axis','Y-axis'],loc='upper left')
    axs[idx].set_xticklabels([])
    axs[idx].set(xlim=[min(time),max(time)])



    idx=5
    axs[idx].set_ylabel(u'GRFs')
    if situations[experiment_classes[0]] == "Noisy feedback":
        grf_feedback_rf = grf[experiment_category][trail_id][:,0] + noise[experiment_category][trail_id][:,1]
        grf_feedback_rh = grf[experiment_category][trail_id][:,1] + noise[experiment_category][trail_id][:,2]
    else:
        grf_feedback_rf = grf[experiment_category][trail_id][:,0]
        grf_feedback_rh = grf[experiment_category][trail_id][:,1]
    
    #if  data_file_dic[79:-1] == "PhaseModulation":
    axs[idx].plot(time,grf_feedback_rf, color=c4_1color)
    axs[idx].plot(time,grf_feedback_rh, color=c4_2color)
    axs[idx].legend(['RF','RH'])

    if  data_file_dic[79:-1] == "PhaseReset":
        axs[idx].plot(time,NP(grf_feedback_rf), color=c4_1color)
        axs[idx].plot(time,NP(grf_feedback_rh), color=c4_2color)
        axs[idx].plot(time,0.2*np.ones(len(time)),'-.k') # Force threshold line, here it is 0.2, details can be see in synapticplasticityCPG.cpp
        axs[idx].legend(['Filtered RF','Filtered RH','Reset threshold'], ncol=2)
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    #axs[idx].set_yticks([-0.3, 0.0, 0.3])
    axs[idx].set_xticklabels([])
    axs[idx].set(xlim=[min(time),max(time)])


    idx=6
    axs[idx].set_ylabel(u'GRFs')
    if situations[experiment_classes[0]] == "Noisy feedback":
        grf_feedback_lf = grf[experiment_category][trail_id][:,2] + noise[experiment_category][trail_id][:,3]
        grf_feedback_lh = grf[experiment_category][trail_id][:,3] + noise[experiment_category][trail_id][:,4]
    else:
        grf_feedback_lf = grf[experiment_category][trail_id][:,2]
        grf_feedback_lh = grf[experiment_category][trail_id][:,3]
    
    #if  data_file_dic[79:-1] == "PhaseModulation":
    axs[idx].plot(time,grf_feedback_lf, color=c4_3color)
    axs[idx].plot(time,grf_feedback_lh, color=c4_4color)
    axs[idx].legend(['LF','LH'])

    if  data_file_dic[79:-1] == "PhaseReset":
        axs[idx].plot(time,NP(grf_feedback_lf), color=c4_3color)
        axs[idx].plot(time,NP(grf_feedback_lh), color=c4_4color)
        axs[idx].plot(time,0.2*np.ones(len(time)),'-.k') # Force threshold line, here it is 0.2, details can be see in synapticplasticityCPG.cpp
        axs[idx].legend(['Filtered LF','Filtered LH','Reset threshold'], ncol=2)
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    #axs[idx].set_yticks([-0.3, 0.0, 0.3])
    axs[idx].set_xticklabels([])
    axs[idx].set(xlim=[min(time),max(time)])


    idx=7
    axs[idx].set_ylabel(r'Gait')
    gait_diagram(fig,axs[idx],gs1,gait_diagram_data[experiment_category][trail_id])
    axs[idx].set_xlabel(u'Time [s]')
    xticks=np.arange(int(min(time)),int(max(time))+1,2)
    axs[idx].set_xticklabels([str(xtick) for xtick in xticks])
    axs[idx].set_xticks(xticks)
    axs[idx].yaxis.set_label_coords(-0.05,.5)
    axs[idx].set(xlim=[min(time),max(time)])

    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'general_display.svg'
    plt.savefig(figPath)

    plt.show()

def plot_runningSuccess_statistic(data_file_dic,start_point=10,end_point=400,freq=60,experiment_classes=['0.0']):
    '''
    Statistical of running success
    

    '''
    # 1) read data
    #1.1) read  local data of phase modulation
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)
    pose_phaseModulation={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        pose_phaseModulation[class_name] =[]
        print(class_name)
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            stability_temp= 1.0/np.std(pose_data[:,0],axis=0) + 1.0/np.std(pose_data[:,1],axis=0) #+ 1.0/np.std(pose_data[:,2]) +1.0/np.std(pose_data[:,5])
            pose_phaseModulation[class_name].append(stability_temp)
            print(pose_phaseModulation[class_name][-1])

    #1.2) read local data of phase reset
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories =load_data_log(data_file_dic_phaseReset)
    pose_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        pose_phaseReset[class_name] =[]
        print(class_name)
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            stability_temp= 1.0/np.std(pose_data[:,0],axis=0) + 1.0/np.std(pose_data[:,1],axis=0) #+ 1.0/np.std(pose_data[:,2]) + 1.0/np.std(pose_data[:,5])
            pose_phaseReset[class_name].append(stability_temp)
            print(pose_phaseReset[class_name][-1])

            
    #2) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 

    idx=0
    axs[idx].bar(ind-0.5*width,[len(pose_phaseModulation[ll]) for ll in labels], width,label=r'Phase modulation')
    axs[idx].bar(ind+0.5*width,[len(pose_phaseReset[ll]) for ll in labels],width,label=r'Phase reset')
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    axs[idx].set(ylim=[0,10])
    axs[idx].legend(loc='center right')
    axs[idx].set_ylabel(r'Success [count]')
    axs[idx].set_xlabel(r'Situations')
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])

    #axs[idx].set_title('Quadruped robot Walking on a slope using CPGs-based control with COG reflexes')
    
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'runningSuccess.svg'
    plt.savefig(figPath)
    plt.show()


def percentage_plot_runningSuccess_statistic(data_file_dic,start_point=10,end_point=400,freq=60,experiment_classes=['0.0']):
    '''
    Statistical of running success
    

    '''
    # 1) read data
    #1.1) read  local data of phase modulation
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)
    pose_phaseModulation={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        pose_phaseModulation[class_name] =[]
        print(class_name)
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            stability_temp= 1.0/np.std(pose_data[:,0],axis=0) + 1.0/np.std(pose_data[:,1],axis=0) #+ 1.0/np.std(pose_data[:,2]) +1.0/np.std(pose_data[:,5])
            pose_phaseModulation[class_name].append(stability_temp)
            print(pose_phaseModulation[class_name][-1])

    #1.2) read local data of phase reset
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories =load_data_log(data_file_dic_phaseReset)
    pose_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        pose_phaseReset[class_name] =[]
        print(class_name)
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            stability_temp= 1.0/np.std(pose_data[:,0],axis=0) + 1.0/np.std(pose_data[:,1],axis=0) #+ 1.0/np.std(pose_data[:,2]) + 1.0/np.std(pose_data[:,5])
            pose_phaseReset[class_name].append(stability_temp)
            print(pose_phaseReset[class_name][-1])

            
    #2) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 

    idx=0
    colors = ['lightblue', 'lightgreen']
    axs[idx].bar(ind-0.5*width,[len(pose_phaseModulation[ll])/10.0*100 for ll in labels], width,label=r'Phase modulation', color=colors[0])
    axs[idx].bar(ind+0.5*width,[len(pose_phaseReset[ll])/10.0*100 for ll in labels],width,label=r'Phase reset',color=colors[1])
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[0,10])
    axs[idx].legend(loc='center right')
    axs[idx].set_ylabel(r'Success rate[%]')
    axs[idx].set_xlabel(r'Situations')
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])

    #axs[idx].set_title('Quadruped robot Walking on a slope using CPGs-based control with COG reflexes')
    
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'runningSuccess.svg'
    plt.savefig(figPath)
    plt.show()

def plot_stability_statistic(data_file_dic,start_point=10,end_point=400,freq=60,experiment_classes=['0.0']):
    '''
    Stability of statistic

    '''
    # 1) read data
    #1.1) read loacal data of phase modulation
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)
    pose_phaseModulation={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        if class_name in categories:
            print(class_name)
            pose_phaseModulation[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                stability_temp= 1.0/np.std(pose_data[:,0],axis=0) + 1.0/np.std(pose_data[:,1],axis=0) #+ 1.0/np.std(pose_data[:,2]) +1.0/np.std(pose_data[:,5])
                pose_phaseModulation[class_name].append(stability_temp)
                print(pose_phaseModulation[class_name][-1])

    #1.2) read loacal data of phase reset
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories =load_data_log(data_file_dic_phaseReset)
    pose_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        if class_name in categories:
            print(class_name)
            pose_phaseReset[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                stability_temp= 1.0/np.std(pose_data[:,0],axis=0) + 1.0/np.std(pose_data[:,1],axis=0) #+ 1.0/np.std(pose_data[:,2]) + 1.0/np.std(pose_data[:,5])
                pose_phaseReset[class_name].append(stability_temp)
                print(pose_phaseReset[class_name][-1])


    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    angular_phaseReset_mean, angular_phaseReset_std=[],[]
    angular_phaseModulation_mean, angular_phaseModulation_std=[],[]
    for i in labels: #inclination
        angular_phaseReset_mean.append(np.mean(pose_phaseReset[i]))
        angular_phaseReset_std.append(np.std(pose_phaseReset[i]))

        angular_phaseModulation_mean.append(np.mean(pose_phaseModulation[i]))
        angular_phaseModulation_std.append(np.std(pose_phaseModulation[i]))

    idx=0
    axs[idx].bar(ind-0.5*width,angular_phaseModulation_mean, width, yerr=angular_phaseModulation_std,label=r'Phase modulation')
    axs[idx].bar(ind+0.5*width,angular_phaseReset_mean,width,yerr=angular_phaseReset_std,label=r'Phase reset')
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend()
    axs[idx].set_ylabel(r'Stability')
    axs[idx].set_xlabel(r'Situations')

    # save plot
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'stabilityStatistic.svg'
    plt.savefig(figPath)
    plt.show()

def plot_coordination_statistic(data_file_dic,start_point=60,end_point=900,freq=60.0,experiment_classes=['0.0']):
    '''
    @description: this is for experiment two, plot coordination statistic
    @param: data_file_dic, the folder of the data files, this path includes a log file which list all folders of the experiment data for display
    @param: start_point, the start point (time) of all the data
    @param: end_point, the end point (time) of all the data
    @param: freq, the sample frequency of the data 
    @param: experiment_classes, the conditions/cases/experiment_classes of the experimental data
    @return: show and save a data figure.

    '''
    #1) load data from file
    
    #1.1) local data of phase modualtion
    data_file_dic_phaseModulation = data_file_dic + "PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)

    coordination_phaseModulation={}

    for class_name, files_name in datas_files_categories: #name is a inclination names
        coordination_phaseModulation[class_name]=[]  #inclination is the table of the inclination name
        print(class_name)
        for idx in files_name.index:
            folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            print(folder_name)
            gait_diagram_data, beta=gait(grf_data)
            temp_1=min([len(bb) for bb in beta]) #minimum steps of all legs
            beta=np.array([beta[0][:temp_1],beta[1][:temp_1],beta[2][:temp_1],beta[3][0:temp_1]]) # transfer to np array
            
            if(beta !=[]):
                coordination_phaseModulation[class_name].append(1.0/max(np.std(beta, axis=0)))# 
            else:
                coordination_phaseModulation[class_name].append(0.0)

            print(coordination_phaseModulation[class_name][-1])
    
    #1.2) local data of phase reset
    data_file_dic_phaseReset = data_file_dic + "PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)
    
    coordination_phaseReset={}

    for class_name, files_name in datas_files_categories: #name is a inclination names
        coordination_phaseReset[class_name]=[]  #inclination is the table of the inclination name
        print(class_name)
        for idx in files_name.index:
            folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            print(folder_name)
            gait_diagram_data, beta=gait(grf_data)
            temp_1=min([len(bb) for bb in beta]) #minimum steps of all legs
            beta=np.array([beta[0][:temp_1],beta[1][:temp_1],beta[2][:temp_1],beta[3][0:temp_1]]) # transfer to np array
            if(beta !=[]):
                coordination_phaseReset[class_name].append(1.0/max(np.std(beta, axis=0)))# 
            else:
                coordination_phaseReset[class_name].append(0.0)
            print(coordination_phaseReset[class_name][-1])


    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    coordinationPhaseModulation_mean,coordinationPhaseModulation_std=[],[]
    coordinationPhaseReset_mean,coordinationPhaseReset_std=[],[]
    for i in labels:
        coordinationPhaseModulation_mean.append(np.mean(coordination_phaseModulation[i]))
        coordinationPhaseModulation_std.append(np.std(coordination_phaseModulation[i]))
        coordinationPhaseReset_mean.append(np.mean(coordination_phaseReset[i]))
        coordinationPhaseReset_std.append(np.std(coordination_phaseReset[i]))

    idx=0
    axs[idx].bar(ind-0.5*width,coordinationPhaseModulation_mean, width, yerr=coordinationPhaseModulation_std,label=r'Phase modulation')
    axs[idx].bar(ind+0.5*width,coordinationPhaseReset_mean,width,yerr=coordinationPhaseReset_std,label=r'Phase reset')
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend()
    axs[idx].set_ylabel(r'Coordination')
    axs[idx].set_xlabel(r'Situations')

    #axs[idx].set_title('Quadruped robot Walking on a slope using CPGs-based control with COG reflexes')
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'coordinationStatistic.svg'
    plt.savefig(figPath)
    plt.show()

def plot_COT_statistic(data_file_dic,start_point=60,end_point=900,freq=60.0,experiment_classes=['0.0']):
    '''
    @description: this is for comparative investigation, plot cost of transport statistic
    @param: data_file_dic, the folder of the data files, this path includes a log file which list all folders of the experiment data for display
    @param: start_point, the start point (time) of all the data
    @param: end_point, the end point (time) of all the data
    @param: freq, the sample frequency of the data 
    @param: experiment_classes, the conditions/cases/experiment_classes of the experimental data
    @return: show and save a data figure.

    '''
    #1) load data from file
    
    #1.1) local COG reflex data
    data_file_dic_phaseModulation = data_file_dic + "PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)

    COT_phaseModulation={}

    for class_name, files_name in datas_files_categories: #name is a inclination names
        COT_phaseModulation[class_name]=[]  #inclination is the table of the inclination name
        print(class_name)
        for idx in files_name.index:
            folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            print(folder_name)
            velocity_data=(position_data[1:,:]-position_data[0:-1,:])*freq
            initial_velocity=[0,0,0, 0,0,0, 0,0,0, 0,0,0]
            velocity_data=np.vstack([initial_velocity,velocity_data])
            m=2.5;g=9.8; m=2.5;g=9.8; d=np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,4]-pose_data[0,4],2)) #Displacement
            COT=EnergyCost(velocity_data,current_data,freq)/(m*g*d)
            COT_phaseModulation[class_name].append(COT)# 
            print(COT_phaseModulation[class_name][-1])
    
    #1.2) local vestibular reflex data
    data_file_dic_phaseReset = data_file_dic + "PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)
    
    COT_phaseReset={}

    for class_name, files_name in datas_files_categories: #name is a inclination names
        COT_phaseReset[class_name]=[]  #inclination is the table of the inclination name
        print(class_name)
        for idx in files_name.index:
            folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            print(folder_name)
            velocity_data=(position_data[1:,:]-position_data[0:-1,:])*freq
            initial_velocity=[0,0,0, 0,0,0, 0,0,0, 0,0,0]
            velocity_data=np.vstack([initial_velocity,velocity_data])
            m=2.5;g=9.8; d=np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,4]-pose_data[0,4],2)) #Displacement
            COT=EnergyCost(velocity_data,current_data,freq)/(m*g*d)
            COT_phaseReset[class_name].append(COT)# 
            print(COT_phaseReset[class_name][-1])

            
    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    COTPhaseModulation_mean,COTPhaseModulation_std=[],[]
    COTPhaseReset_mean,COTPhaseReset_std=[],[]
    for i in labels:
        COTPhaseModulation_mean.append(np.mean(COT_phaseModulation[i]))
        COTPhaseModulation_std.append(np.std(COT_phaseModulation[i]))
        COTPhaseReset_mean.append(np.mean(COT_phaseReset[i]))
        COTPhaseReset_std.append(np.std(COT_phaseReset[i]))

    idx=0
    axs[idx].bar(ind-0.5*width,COTPhaseModulation_mean, width, yerr=COTPhaseModulation_std,label=r'Phase modulation')
    axs[idx].bar(ind+0.5*width,COTPhaseReset_mean,width,yerr=COTPhaseReset_std,label=r'Phase reset')
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend()
    axs[idx].set_ylabel(r'COT')
    axs[idx].set_xlabel(r'Situations')

    #axs[idx].set_title('Quadruped robot Walking on a slope using CPGs-based control with COG reflexes')
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'COTStatistic.svg'
    plt.savefig(figPath)
    plt.show()

def plot_energyCost_statistic(data_file_dic,start_point=60,end_point=900,freq=60.0,experiment_classes=['0.0']):
    '''
    @description: this is for compative investigation to plot energy cost statistic
    @param: data_file_dic, the folder of the data files, this path includes a log file which list all folders of the experiment data for display
    @param: start_point, the start point (time) of all the data
    @param: end_point, the end point (time) of all the data
    @param: freq, the sample frequency of the data 
    @param: experiment_classes, the conditions/cases/experiment_classes of the experimental data
    @return: show and save a data figure.

    '''
    #1) load data from file
    
    #1.1) local data of phase modulation
    data_file_dic_phaseModulation = data_file_dic + "PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)
    energy_phaseModulation={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        energy_phaseModulation[class_name]=[]  #inclination is the table of the inclination name
        print(class_name)
        for idx in files_name.index:
            folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            print(folder_name)
            velocity_data=(position_data[1:,:]-position_data[0:-1,:])*freq
            initial_velocity=[0,0,0, 0,0,0, 0,0,0, 0,0,0]
            velocity_data=np.vstack([initial_velocity,velocity_data])
            energy=EnergyCost(velocity_data,current_data,freq)
            energy_phaseModulation[class_name].append(energy)# 
            print(energy_phaseModulation[class_name][-1])
    
    #1.2) local data of phase reset
    data_file_dic_phaseReset = data_file_dic + "PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)
    energy_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        energy_phaseReset[class_name]=[]  #inclination is the table of the inclination name
        print(class_name)
        for idx in files_name.index:
            folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            print(folder_name)
            velocity_data=(position_data[1:,:]-position_data[0:-1,:])*freq
            initial_velocity=[0,0,0, 0,0,0, 0,0,0, 0,0,0]
            velocity_data=np.vstack([initial_velocity,velocity_data])
            energy=EnergyCost(velocity_data,current_data,freq)
            energy_phaseReset[class_name].append(energy)# 
            print(energy_phaseReset[class_name][-1])


    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    energyPhaseModulation_mean,energyPhaseModulation_std=[],[]
    energyPhaseReset_mean,energyPhaseReset_std=[],[]
    for i in labels:
        energyPhaseModulation_mean.append(np.mean(energy_phaseModulation[i]))
        energyPhaseModulation_std.append(np.std(energy_phaseModulation[i]))
        energyPhaseReset_mean.append(np.mean(energy_phaseReset[i]))
        energyPhaseReset_std.append(np.std(energy_phaseReset[i]))

    idx=0
    axs[idx].bar(ind-0.5*width,energyPhaseModulation_mean, width, yerr=energyPhaseModulation_std,label=r'Phase modulation')
    axs[idx].bar(ind+0.5*width,energyPhaseReset_mean,width,yerr=energyPhaseReset_std,label=r'Phase reset')
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend()
    axs[idx].set_ylabel(r'Energy')
    axs[idx].set_xlabel(r'Situations')

    #axs[idx].set_title('Quadruped robot Walking on a slope using CPGs-based control with COG reflexes')
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'energyStatistic.svg'
    plt.savefig(figPath)
    plt.show()

def plot_slipping_statistic(data_file_dic,start_point=60,end_point=900,freq=60.0,experiment_classes=['0.0']):
    '''
    @description: this is for experiment two, plot slipping statistic
    @param: data_file_dic, the folder of the data files, this path includes a log file which list all folders of the experiment data for display
    @param: start_point, the start point (time) of all the data
    @param: end_point, the end point (time) of all the data
    @param: freq, the sample frequency of the data 
    @param: experiment_classes, the conditions/cases/experiment_classes of the experimental data
    @return: show and save a data figure.

    '''
    #1) load data from file
    
    #1.1) local COG reflex data
    data_file_dic_phaseModulation = data_file_dic + "PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)
    COT_phaseModulation={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        COT_phaseModulation[class_name]=[]  #inclination is the table of the inclination name
        print(class_name)
        for idx in files_name.index:
            folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            print(folder_name)
            expected_actual_motion_states=touch_difference(cpg_data[:,[0,2,4,6]], grf_data)
            expected_actual_motion_states_equal = expected_actual_motion_states[0]==expected_actual_motion_states[1]

            COT_phaseModulation[class_name].append(COT)# 
            print(COT_phaseModulation[class_name][-1])
    
    #1.2) local vestibular reflex data
    data_file_dic_phaseReset = data_file_dic + "PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)
    
    COT_phaseReset={}

    for class_name, files_name in datas_files_categories: #name is a inclination names
        COT_phaseReset[class_name]=[]  #inclination is the table of the inclination name
        print(class_name)
        for idx in files_name.index:
            folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            print(folder_name)
            expected_actual_motion_states=touch_difference(cpg_data[:,[0,2,4,6]], grf_data)
            expected_actual_motion_states_equal = expected_actual_motion_states[0]==expected_actual_motion_states[1]

            COT_phaseReset[class_name].append(COT)# 
            print(COT_phaseReset[class_name][-1])



    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    COTPhaseModulation_mean,COTPhaseModulation_std=[],[]
    COTPhaseReset_mean,COTPhaseReset_std=[],[]
    for i in labels:
        COTPhaseModulation_mean.append(np.mean(COT_phaseModulation[i]))
        COTPhaseModulation_std.append(np.std(COT_phaseModulation[i]))
        COTPhaseReset_mean.append(np.mean(COT_phaseReset[i]))
        COTPhaseReset_std.append(np.std(COT_phaseReset[i]))

    idx=0
    axs[idx].bar(ind-0.5*width,COTPhaseModulation_mean, width, yerr=COTPhaseModulation_std,label=r'Phase modulation')
    axs[idx].bar(ind+0.5*width,COTPhaseReset_mean,width,yerr=COTPhaseReset_std,label=r'Phase reset')
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend()
    axs[idx].set_ylabel(r'COT')
    axs[idx].set_xlabel(r'Situations')

    #axs[idx].set_title('Quadruped robot Walking on a slope using CPGs-based control with COG reflexes')
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'COTStatistic.svg'
    plt.savefig(figPath)
    plt.show()

def plot_distance_statistic(data_file_dic,start_point=10,end_point=400,freq=60,experiment_classes=['0.0']):
    '''
    Plot distance statistic, it calculates all movement, oscillation of the body during locomotion, it cannot express the transporyability of the locomotion
    

    '''
    # 1) read data
    # 1.1) read Phase reset data
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)

    pose_phaseModulation={}

    for class_name, files_name in datas_files_categories: #name is a inclination names
        pose_phaseModulation[class_name] =[]
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            d=0
            for step_index in range(pose_data.shape[0]-1):
                d+=np.sqrt(pow(pose_data[step_index+1,3]-pose_data[step_index,3],2)+pow(pose_data[step_index+1,4]-pose_data[step_index,4],2))
            pose_phaseModulation[class_name].append(d) #Displacement on slopes 
            print(pose_phaseModulation[class_name][-1])

    #1.2) read continuous phase modulation data
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)

    pose_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        pose_phaseReset[class_name] =[]
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            d=0
            for step_index in range(pose_data.shape[0]-1):
                d+=np.sqrt(pow(pose_data[step_index+1,3]-pose_data[step_index,3],2)+pow(pose_data[step_index+1,4]-pose_data[step_index,4],2))
            pose_phaseReset[class_name].append(d) #Displacement on slopes 
            print(pose_phaseReset[class_name][-1])


    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    disp_phaseReset_mean, disp_phaseReset_std=[],[]
    disp_phaseModulation_mean, disp_phaseModulation_std=[],[]
    for i in labels: #inclination
        disp_phaseReset_mean.append(np.mean(pose_phaseReset[i]))
        disp_phaseReset_std.append(np.std(pose_phaseReset[i]))

        disp_phaseModulation_mean.append(np.mean(pose_phaseModulation[i]))
        disp_phaseModulation_std.append(np.std(pose_phaseModulation[i]))

    idx=0
    axs[idx].bar(ind-0.5*width,disp_phaseModulation_mean, width, yerr=disp_phaseModulation_std,label=r'Phase modulation')
    axs[idx].bar(ind+0.5*width,disp_phaseReset_mean,width,yerr=disp_phaseReset_std,label=r'Phase reset')
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend()
    axs[idx].set_ylabel(r'Distance [m]')
    axs[idx].set_xlabel(r'Situations')

    #axs[idx].set_title('Phase reset')
    
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'distance.svg'
    plt.savefig(figPath)
    plt.show()

def plot_displacement_statistic(data_file_dic,start_point=10,end_point=400,freq=60,experiment_classes=['0.0']):
    '''
    plot displacement statistic, it can indicates the actual traverability of the locomotion
    

    '''
    # 1) read data
    # 1.1) read Phase reset data
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)

    pose_phaseModulation={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        pose_phaseModulation[class_name] =[]
        print(class_name)
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            disp=np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,4]-pose_data[0,4],2))#Displacement
            pose_phaseModulation[class_name].append(disp) #Displacement on slopes 
            print(pose_phaseModulation[class_name][-1])
            
    #1.2) read continuous phase modulation data
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)

    pose_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        pose_phaseReset[class_name] =[]
        print(class_name)
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            disp=np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,4]-pose_data[0,4],2))#Displacement
            pose_phaseReset[class_name].append(disp) #Displacement on slopes 
            print(pose_phaseReset[class_name][-1])


    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    disp_phaseReset_mean, disp_phaseReset_std=[],[]
    disp_phaseModulation_mean, disp_phaseModulation_std=[],[]
    for i in labels: #inclination
        disp_phaseReset_mean.append(np.mean(pose_phaseReset[i]))
        disp_phaseReset_std.append(np.std(pose_phaseReset[i]))

        disp_phaseModulation_mean.append(np.mean(pose_phaseModulation[i]))
        disp_phaseModulation_std.append(np.std(pose_phaseModulation[i]))

    idx=0
    axs[idx].bar(ind-0.5*width,disp_phaseModulation_mean, width, yerr=disp_phaseModulation_std,label=r'Phase modulation')
    axs[idx].bar(ind+0.5*width,disp_phaseReset_mean,width,yerr=disp_phaseReset_std,label=r'Phase reset')
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend()
    axs[idx].set_ylabel(r'Displacement [m]')
    axs[idx].set_xlabel(r'Situations')

    #axs[idx].set_title('Phase reset')
    
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'displacement.svg'
    plt.savefig(figPath)
    plt.show()

def touch_convergence_moment_identification(grf_data,cpg_data,time):
    '''
    Identify the touch and phase convergence moment
    '''
    grf_stance = grf_data > 0.06# GRF is bigger than 0.06, we see the robot starts to interact weith the ground
    grf_stance_index=np.where(grf_stance.sum(axis=1)==4)# Find the drop on ground moment
    phi_stability=phase_diff_stability(cpg_data[grf_stance_index[0][0]:,:],time[grf_stance_index[0][0]:])     
    phi_stability_threshold=0.7# empirically set
    for idx, value in enumerate(phi_stability):
        if value > phi_stability_threshold and phi_stability[idx+1] < phi_stability_threshold:
            break

    return grf_stance_index[0][0], idx+1, phi_stability

def phase_formTime_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['0']):
    '''
    Plot convergence time statistic, it can indicates the actual traverability of the locomotion

    '''
    # 1) read data
    # 1.1) read Phase reset data
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)
    phi_phaseModulation={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        if class_name in categories:
            print(class_name)
            phi_phaseModulation[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                grf_stance = grf_data > 0.06# GRF is bigger than 0.06, we see the robot starts to interact weith the ground
                grf_stance_index=np.where(grf_stance.sum(axis=1)==4)# Find the drop on ground moment
                phi_stability=phase_diff_stability(cpg_data[grf_stance_index[0][0]:,:],time[grf_stance_index[0][0]:])     
                phi_stability_threshold=0.7# empirically set
                for idx, value in enumerate(phi_stability):
                    if idx>=len(phi_stability)-1: # Not converge
                        convergenTime=len(phi_stability)/freq
                        break
                    if value > phi_stability_threshold and phi_stability[idx+1] < phi_stability_threshold:
                        convergenTime=idx/freq
                        break
                phi_phaseModulation[class_name].append(convergenTime) #Displacement on slopes 
                print(phi_phaseModulation[class_name][-1])
                print("Convergence idx", idx)

    #1.2) read continuous phase modulation data
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)
    phi_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        if class_name in categories:
            print(class_name)
            phi_phaseReset[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                grf_stance = grf_data > 0.06# GRF is bigger than 0.06, we see the robot starts to interact weith the ground
                grf_stance_index=np.where(grf_stance.sum(axis=1)==4)# Find the drop on ground moment
                phi_stability=phase_diff_stability(cpg_data[grf_stance_index[0][0]:,:],time[grf_stance_index[0][0]:])     
                phi_stability_threshold=0.7# empirically set
                for idx, value in enumerate(phi_stability):
                    if idx>=len(phi_stability)-1: # Not converge
                        convergenTime=len(phi_stability)/freq
                        break
                    if (value > phi_stability_threshold) and (phi_stability[idx+1] < phi_stability_threshold):
                        convergenTime=idx/freq
                        break
                phi_phaseReset[class_name].append(convergenTime) #Displacement on slopes 
                print(phi_phaseReset[class_name][-1])
                print("Convergence idx", idx)


    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    phi_phaseReset_mean, phi_phaseReset_std=[],[]
    phi_phaseModulation_mean, phi_phaseModulation_std=[],[]
    for i in labels: #inclination
        phi_phaseReset_mean.append(np.mean(phi_phaseReset[i]))
        phi_phaseReset_std.append(np.std(phi_phaseReset[i]))

        phi_phaseModulation_mean.append(np.mean(phi_phaseModulation[i]))
        phi_phaseModulation_std.append(np.std(phi_phaseModulation[i]))

    idx=0
    axs[idx].bar(ind-0.5*width,phi_phaseModulation_mean, width, yerr=phi_phaseModulation_std,label=r'Phase modulation')
    axs[idx].bar(ind+0.5*width,phi_phaseReset_mean,width,yerr=phi_phaseReset_std,label=r'Phase reset')
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend()
    axs[idx].set_ylabel(r'Phase convergence time [s]')
    axs[idx].set_xlabel(r'Situations')

    #axs[idx].set_title('Phase reset')
    
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'phase_convergence_time.svg'
    plt.savefig(figPath)
    plt.show()

def phase_stability_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['0']):
    '''
    Plot formed phase stability statistic, it can indicates the actual traverability of the locomotion

    '''
    # 1) read data

    # 1.1) read Phase reset data
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)

    phi_phaseModulation={}
    
    for class_name, files_name in datas_files_categories: #name is a experiment class names
        if class_name in categories:
            print(class_name)
            phi_phaseModulation[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                touch_idx, convergence_idx, phi_stability =touch_convergence_moment_identification(grf_data,cpg_data,time)
                formedphase_stability=np.mean(phi_stability[convergence_idx:])
                phi_phaseModulation[class_name].append(1.0/formedphase_stability) #phase stability of the formed phase diff, inverse of the std
                print(phi_phaseModulation[class_name][-1])

    #1.2) read continuous phase modulation data
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)

    phi_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a experiment class names
        if class_name in categories:
            print(class_name)
            phi_phaseReset[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                touch_idx, convergence_idx, phi_stability =touch_convergence_moment_identification(grf_data,cpg_data,time)
                formedphase_stability=np.mean(phi_stability[convergence_idx:])
                phi_phaseReset[class_name].append(1.0/formedphase_stability) #phase stability of the formed phase diff, inverse of the std
                print(phi_phaseReset[class_name][-1])

    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    phi_phaseReset_mean, phi_phaseReset_std=[],[]
    phi_phaseModulation_mean, phi_phaseModulation_std=[],[]
    for i in labels: #inclination
        phi_phaseReset_mean.append(np.mean(phi_phaseReset[i]))
        phi_phaseReset_std.append(np.std(phi_phaseReset[i]))

        phi_phaseModulation_mean.append(np.mean(phi_phaseModulation[i]))
        phi_phaseModulation_std.append(np.std(phi_phaseModulation[i]))

    idx=0
    axs[idx].bar(ind-0.5*width,phi_phaseModulation_mean, width, yerr=phi_phaseModulation_std,label=r'Phase modulation')
    axs[idx].bar(ind+0.5*width,phi_phaseReset_mean,width,yerr=phi_phaseReset_std,label=r'Phase reset')
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend()
    axs[idx].set_ylabel(r'Phase stability')
    axs[idx].set_xlabel(r'Situations')

    #axs[idx].set_title('Phase reset')
    
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'Phase_stability.svg'
    plt.savefig(figPath)
    plt.show()

'''  Parameters analysis '''

def phaseModulation_parameter_investigation_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['0']):
    '''
    Plot convergence time of different parameter statistic, it can indicates the actual traverability of the locomotion

    '''
    # 1) read data
    # 1.1) read Phase reset data
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)
    phi_phaseModulation={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        print(class_name)
        phi_phaseModulation[class_name] =[]
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            grf_stance = grf_data > 0.06# GRF is bigger than 0.06, we see the robot starts to interact weith the ground
            grf_stance_index=np.where(grf_stance.sum(axis=1)==4)# Find the drop on ground moment
            phi_stability=phase_diff_stability(cpg_data[grf_stance_index[0][0]:,:],time[grf_stance_index[0][0]:])     
            phi_stability_threshold=0.7# empirically set
            for idx, value in enumerate(phi_stability):
                if idx>=len(phi_stability)-1: # Not converge
                    convergenTime=len(phi_stability)/freq
                    break
                if value > phi_stability_threshold and phi_stability[idx+1] < phi_stability_threshold:
                    convergenTime=idx/freq
                    break
            phi_phaseModulation[class_name].append(convergenTime) #Displacement on slopes 
            print(phi_phaseModulation[class_name][-1])
            print("Convergence idx", idx)


    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95, bottom=0.14, left=0.12, right=0.88)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([float(ll) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    phi_phaseModulation_mean, phi_phaseModulation_std=[],[]
    for i in labels: 
        phi_phaseModulation_mean.append(np.mean(phi_phaseModulation[i]))
        phi_phaseModulation_std.append(np.std(phi_phaseModulation[i]))

    idx=0
    color= 'tab:green'
    #axs[idx].bar(ind-0.5*width,phi_phaseModulation_mean, width, yerr=phi_phaseModulation_std,label=r'Phase modulation')
    axs[idx].errorbar(ind,phi_phaseModulation_mean, yerr=phi_phaseModulation_std, fmt='-o', color=color)
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    axs[idx].set_xticklabels([round(float(ll)*4,2) for ll in labels])
    axs[idx].set_ylabel(r'Phase convergence time [s]', color=color)
    axs[idx].set_xlabel(r'Gain [$\frac{1}{mg}$]')
    axs[idx].tick_params(axis='y', labelcolor=color)

    success_rate= [100*(ll<25) for ll in phi_phaseModulation_mean]
    ax2 = axs[idx].twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Success rate [%]', color=color)  # we already handled the x-label with ax1
    ax2.plot(ind, success_rate,'-h', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'phaseModulation_parameter_convergence_time.svg'
    plt.savefig(figPath)
    plt.show()

def phaseReset_parameter_investigation_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['0']):
    '''
    Plot convergence time of different parameter statistic, it can indicates the actual traverability of the locomotion

    '''
    # 1) read data
    # 1.1) read Phase reset data
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)
    phi_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        if class_name in experiment_classes:
            print(class_name)
            phi_phaseReset[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                grf_stance = grf_data > 0.06# GRF is bigger than 0.06, we see the robot starts to interact weith the ground
                grf_stance_index=np.where(grf_stance.sum(axis=1)==4)# Find the drop on ground moment
                phi_stability=phase_diff_stability(cpg_data[grf_stance_index[0][0]:,:],time[grf_stance_index[0][0]:])     
                phi_stability_threshold=0.7# empirically set
                for idx, value in enumerate(phi_stability):
                    if idx>=len(phi_stability)-2: # Not converge
                        convergenTime=len(phi_stability)/freq
                        break
                    if (value > phi_stability_threshold) and (phi_stability[idx+1] < phi_stability_threshold):
                        convergenTime=idx/freq
                        break
                phi_phaseReset[class_name].append(convergenTime) #Displacement on slopes 
                print(phi_phaseReset[class_name][-1])
                print("Convergence idx", idx)


    #3) plot

    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95, bottom=0.14, left=0.12, right=0.88)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    if len(experiment_classes) > 1:
        labels=[str(ll) for ll in sorted([float(ll) for ll in experiment_classes])]
    else:
        labels=[str(ll) for ll in sorted([float(ll) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 


    phi_phaseReset_mean, phi_phaseReset_std=[],[]
    for i in labels: 
        phi_phaseReset_mean.append(np.mean(phi_phaseReset[i]))
        phi_phaseReset_std.append(np.std(phi_phaseReset[i]))

    idx=0
    color= 'tab:green'
    axs[idx].errorbar(ind,phi_phaseReset_mean, yerr=phi_phaseReset_std, fmt='-o', color=color)
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_ylabel(r'Phase convergence time [s]', color=color)
    #axs[idx].set_ylim(-5,45)
    axs[idx].set_yticks([0,5,10,15,20,25,30])
    axs[idx].set_xticks(ind)
    axs[idx].set_xticklabels([round(float(ll)/0.55,2) for ll in labels])
    axs[idx].set_xlabel(r'Ratio of threshold ($\frac{4F_T}{mg})$')
    axs[idx].tick_params(axis='y', labelcolor=color)


    success_rate=[]
    for i in labels: 
        success_count= np.array(phi_phaseReset[i]) < 20.0
        success_rate.append(sum(success_count)/10.0*100)
    ax2 = axs[idx].twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Success rate [%]', color=color)  # we already handled the x-label with ax1
    ax2.plot(ind, success_rate,'-h', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    #ax2.set_ylim(-10,110)
    ax2.set_yticks([0, 20,40, 60, 80, 100])

    
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'phaseReset_parameter_convergence_time.svg'
    plt.savefig(figPath)
    plt.show()

''' The follwwing functions depict the box plot of the statistic data   '''
def percentage_plot_runningSuccess_statistic_2(data_file_dic,start_point=10,end_point=400,freq=60,experiment_classes=['0.0']):
    '''
    Statistical of running success
    

    '''
    # 1) read data
    #1.1) read  local data of phase modulation
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)
    pose_phaseModulation={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        pose_phaseModulation[class_name] =[]
        print(class_name)
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            stability_temp= 1.0/np.std(pose_data[:,0],axis=0) + 1.0/np.std(pose_data[:,1],axis=0) #+ 1.0/np.std(pose_data[:,2]) +1.0/np.std(pose_data[:,5])
            pose_phaseModulation[class_name].append(stability_temp)
            print(pose_phaseModulation[class_name][-1])

    #1.2) read local data of phase reset
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories =load_data_log(data_file_dic_phaseReset)
    pose_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        pose_phaseReset[class_name] =[]
        print(class_name)
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            stability_temp= 1.0/np.std(pose_data[:,0],axis=0) + 1.0/np.std(pose_data[:,1],axis=0) #+ 1.0/np.std(pose_data[:,2]) + 1.0/np.std(pose_data[:,5])
            pose_phaseReset[class_name].append(stability_temp)
            print(pose_phaseReset[class_name][-1])

            
    #2) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 

    idx=0
    colors = ['lightblue', 'lightgreen']
    axs[idx].bar(ind-0.5*width,[len(pose_phaseModulation[ll])/10.0*100 for ll in labels], width,label=r'Phase modulation', color=colors[0])
    axs[idx].bar(ind+0.5*width,[len(pose_phaseReset[ll])/10.0*100 for ll in labels],width,label=r'Phase reset',color=colors[1])
    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[0,10])
    axs[idx].legend(loc='center right')
    axs[idx].set_ylabel(r'Success rate[%]')
    axs[idx].set_xlabel(r'Situations')
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])

    #axs[idx].set_title('Quadruped robot Walking on a slope using CPGs-based control with COG reflexes')
    
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'runningSuccess.svg'
    plt.savefig(figPath)
    plt.show()

def boxplot_phase_formTime_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['0']):
    '''
    Plot convergence time statistic, it can indicates the actual traverability of the locomotion

    '''
    # 1) read data
    # 1.1) read Phase reset data
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)
    phi_phaseModulation={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        if class_name in categories:
            print(class_name)
            phi_phaseModulation[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                grf_stance = grf_data > 0.06# GRF is bigger than 0.06, we see the robot starts to interact weith the ground
                grf_stance_index=np.where(grf_stance.sum(axis=1)==4)# Find the drop on ground moment
                phi_stability=phase_diff_stability(cpg_data[grf_stance_index[0][0]:,:],time[grf_stance_index[0][0]:])     
                phi_stability_threshold=0.7# empirically set
                for idx, value in enumerate(phi_stability):
                    if idx>=len(phi_stability)-1: # Not converge
                        convergenTime=len(phi_stability)/freq
                        break
                    if value > phi_stability_threshold and phi_stability[idx+1] < phi_stability_threshold:
                        convergenTime=idx/freq
                        break
                phi_phaseModulation[class_name].append(convergenTime) #Displacement on slopes 
                print(phi_phaseModulation[class_name][-1])
                print("Convergence idx", idx)

    #1.2) read phase reset data
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)
    phi_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        if class_name in categories:
            print(class_name)
            phi_phaseReset[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                grf_stance = grf_data > 0.06# GRF is bigger than 0.06, we see the robot starts to interact weith the ground
                grf_stance_index=np.where(grf_stance.sum(axis=1)==4)# Find the drop on ground moment
                phi_stability=phase_diff_stability(cpg_data[grf_stance_index[0][0]:,:],time[grf_stance_index[0][0]:])     
                phi_stability_threshold=0.7# empirically set
                for idx, value in enumerate(phi_stability):
                    if idx>=len(phi_stability)-1: # Not converge
                        convergenTime=len(phi_stability)/freq
                        break
                    if (value > phi_stability_threshold) and (phi_stability[idx+1] < phi_stability_threshold):
                        convergenTime=idx/freq
                        break
                phi_phaseReset[class_name].append(convergenTime) #Displacement on slopes 
                print(phi_phaseReset[class_name][-1])
                print("Convergence idx", idx)


    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))

    #3.1) plot 
    phi_phaseModulation_values=[]
    phi_phaseReset_values=[]
    for i in labels: #inclination
        phi_phaseModulation_values.append(phi_phaseModulation[i])
        phi_phaseReset_values.append(phi_phaseReset[i])

    idx=0
    boxwidth=0.2
    box1=axs[idx].boxplot(phi_phaseModulation_values,widths=boxwidth, positions=ind-boxwidth/2,vert=True,patch_artist=True)
    box2=axs[idx].boxplot(phi_phaseReset_values,widths=boxwidth, positions=ind+boxwidth/2,vert=True,patch_artist=True)

       # fill with colors
    colors = ['lightblue', 'lightgreen']
    for bplot, color in zip((box1, box2),colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)

    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticks(ind)
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend([box1['boxes'][0], box2['boxes'][0]],['Phase modulation','Phase reset'])
    axs[idx].set_ylabel(r'Phase convergence time [s]')
    axs[idx].set_xlabel(r'Situations')

    #axs[idx].set_title('Phase reset')
    
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'phase_convergence_time.svg'
    plt.savefig(figPath)
    plt.show()

def boxplot_phase_stability_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['0']):
    '''
    Plot formed phase stability statistic, it can indicates the actual traverability of the locomotion

    '''
    # 1) read data

    # 1.1) read Phase reset data
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)

    phi_phaseModulation={}
    
    for class_name, files_name in datas_files_categories: #name is a experiment class names
        if class_name in categories:
            print(class_name)
            phi_phaseModulation[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                touch_idx, convergence_idx, phi_stability =touch_convergence_moment_identification(grf_data,cpg_data,time)
                formedphase_stability=np.mean(phi_stability[convergence_idx:])
                phi_phaseModulation[class_name].append(1.0/formedphase_stability) #phase stability of the formed phase diff, inverse of the std
                print(phi_phaseModulation[class_name][-1])

    #1.2) read continuous phase modulation data
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)

    phi_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a experiment class names
        if class_name in categories:
            print(class_name)
            phi_phaseReset[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                touch_idx, convergence_idx, phi_stability =touch_convergence_moment_identification(grf_data,cpg_data,time)
                formedphase_stability=np.mean(phi_stability[convergence_idx:])
                phi_phaseReset[class_name].append(1.0/formedphase_stability) #phase stability of the formed phase diff, inverse of the std
                print(phi_phaseReset[class_name][-1])

    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))

    #3.1) plot 
    phi_phaseModulation_values=[]
    phi_phaseReset_values=[]
    for i in labels: #inclination
        phi_phaseModulation_values.append(phi_phaseModulation[i])
        phi_phaseReset_values.append(phi_phaseReset[i])

    idx=0
    boxwidth=0.2
    box1=axs[idx].boxplot(phi_phaseModulation_values,widths=boxwidth, positions=ind-boxwidth/2,vert=True,patch_artist=True)
    box2=axs[idx].boxplot(phi_phaseReset_values,widths=boxwidth, positions=ind+boxwidth/2,vert=True,patch_artist=True)

    # fill with colors
    colors = ['lightblue', 'lightgreen']
    for bplot, color in zip((box1, box2),colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)

    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].legend([box1['boxes'][0], box2['boxes'][0]],['Phase modulation','Phase reset'])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].set_ylabel(r'Phase stability')
    axs[idx].set_xlabel(r'Situations')

    #axs[idx].set_title('Phase reset')
    
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'Phase_stability.svg'
    plt.savefig(figPath)
    plt.show()

def boxplot_displacement_statistic(data_file_dic,start_point=10,end_point=400,freq=60,experiment_classes=['0.0']):
    '''
    plot displacement statistic, it can indicates the actual traverability of the locomotion
    

    '''
    # 1) read data
    # 1.1) read Phase reset data
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)

    pose_phaseModulation={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        pose_phaseModulation[class_name] =[]
        print(class_name)
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            disp=np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,4]-pose_data[0,4],2))#Displacement
            pose_phaseModulation[class_name].append(disp) #Displacement on slopes 
            print(pose_phaseModulation[class_name][-1])
            
    #1.2) read continuous phase modulation data
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)

    pose_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        pose_phaseReset[class_name] =[]
        print(class_name)
        for idx in files_name.index: # how many time experiments one inclination
            folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
            print(folder_name)
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            disp=np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,4]-pose_data[0,4],2))#Displacement
            pose_phaseReset[class_name].append(disp) #Displacement on slopes 
            print(pose_phaseReset[class_name][-1])


    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    disp_phaseReset_values=[]
    disp_phaseModulation_values=[]
    for i in labels: #inclination
        disp_phaseReset_values.append(pose_phaseReset[i])
        disp_phaseModulation_values.append(pose_phaseModulation[i])

    idx=0
    boxwidth=0.2
    box1=axs[idx].boxplot(disp_phaseModulation_values,widths=boxwidth, positions=ind-boxwidth/2,vert=True,patch_artist=True)
    box2=axs[idx].boxplot(disp_phaseReset_values,widths=boxwidth, positions=ind+boxwidth/2,vert=True,patch_artist=True)

    # fill with colors
    colors = ['lightblue', 'lightgreen']
    for bplot, color in zip((box1, box2),colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)


    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend([box1['boxes'][0], box2['boxes'][0]],['Phase modulation','Phase reset'])
    axs[idx].set_ylabel(r'Displacement [m]')
    axs[idx].set_xlabel(r'Situations')

    #axs[idx].set_title('Phase reset')
    
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'displacement.svg'
    plt.savefig(figPath)
    plt.show()

def boxplot_stability_statistic(data_file_dic,start_point=10,end_point=400,freq=60,experiment_classes=['0.0']):
    '''
    Stability of statistic

    '''
    # 1) read data
    #1.1) read loacal data of phase modulation
    data_file_dic_phaseModulation=data_file_dic+"PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)
    pose_phaseModulation={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        if class_name in categories:
            print(class_name)
            pose_phaseModulation[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                stability_temp= 1.0/np.std(pose_data[:,0],axis=0) + 1.0/np.std(pose_data[:,1],axis=0) #+ 1.0/np.std(pose_data[:,2]) +1.0/np.std(pose_data[:,5])
                pose_phaseModulation[class_name].append(stability_temp)
                print(pose_phaseModulation[class_name][-1])

    #1.2) read loacal data of phase reset
    data_file_dic_phaseReset=data_file_dic+"PhaseReset/"
    datas_files_categories, categories =load_data_log(data_file_dic_phaseReset)
    pose_phaseReset={}
    for class_name, files_name in datas_files_categories: #name is a inclination names
        if class_name in categories:
            print(class_name)
            pose_phaseReset[class_name] =[]
            for idx in files_name.index: # how many time experiments one inclination
                folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
                print(folder_name)
                cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
                # 2)  data process
                stability_temp= 1.0/np.std(pose_data[:,0],axis=0) + 1.0/np.std(pose_data[:,1],axis=0) #+ 1.0/np.std(pose_data[:,2]) + 1.0/np.std(pose_data[:,5])
                pose_phaseReset[class_name].append(stability_temp)
                print(pose_phaseReset[class_name][-1])


    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    stability_phaseReset_values, stability_phaseModulation_values=[],[]
    for i in labels: #inclination
        stability_phaseReset_values.append(pose_phaseReset[i])
        stability_phaseModulation_values.append(pose_phaseModulation[i])


    idx=0
    boxwidth=0.2
    box1=axs[idx].boxplot(stability_phaseModulation_values,widths=boxwidth, positions=ind-boxwidth/2,vert=True,patch_artist=True)
    box2=axs[idx].boxplot(stability_phaseReset_values,widths=boxwidth, positions=ind+boxwidth/2,vert=True,patch_artist=True)

    # fill with colors
    colors = ['lightblue', 'lightgreen']
    for bplot, color in zip((box1, box2),colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)


    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend([box1['boxes'][0], box2['boxes'][0]],['Phase modulation','Phase reset'])
    axs[idx].set_ylabel(r'Stability')
    axs[idx].set_xlabel(r'Situations')

    # save plot
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'stabilityStatistic.svg'
    plt.savefig(figPath)
    plt.show()

def boxplot_COT_statistic(data_file_dic,start_point=60,end_point=900,freq=60.0,experiment_classes=['0.0']):
    '''
    @description: this is for comparative investigation, plot cost of transport statistic
    @param: data_file_dic, the folder of the data files, this path includes a log file which list all folders of the experiment data for display
    @param: start_point, the start point (time) of all the data
    @param: end_point, the end point (time) of all the data
    @param: freq, the sample frequency of the data 
    @param: experiment_classes, the conditions/cases/experiment_classes of the experimental data
    @return: show and save a data figure.

    '''
    #1) load data from file
    
    #1.1) local COG reflex data
    data_file_dic_phaseModulation = data_file_dic + "PhaseModulation/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseModulation)

    COT_phaseModulation={}

    for class_name, files_name in datas_files_categories: #name is a inclination names
        COT_phaseModulation[class_name]=[]  #inclination is the table of the inclination name
        print(class_name)
        for idx in files_name.index:
            folder_name= data_file_dic_phaseModulation + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            print(folder_name)
            velocity_data=(position_data[1:,:]-position_data[0:-1,:])*freq
            initial_velocity=[0,0,0, 0,0,0, 0,0,0, 0,0,0]
            velocity_data=np.vstack([initial_velocity,velocity_data])
            m=2.5;g=9.8; m=2.5;g=9.8; d=np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,4]-pose_data[0,4],2)) #Displacement
            COT=EnergyCost(velocity_data,current_data,freq)/(m*g*d)
            COT_phaseModulation[class_name].append(COT)# 
            print(COT_phaseModulation[class_name][-1])
    
    #1.2) local vestibular reflex data
    data_file_dic_phaseReset = data_file_dic + "PhaseReset/"
    datas_files_categories, categories=load_data_log(data_file_dic_phaseReset)
    
    COT_phaseReset={}

    for class_name, files_name in datas_files_categories: #name is a inclination names
        COT_phaseReset[class_name]=[]  #inclination is the table of the inclination name
        print(class_name)
        for idx in files_name.index:
            folder_name= data_file_dic_phaseReset + files_name['file_name'][idx]
            cpg_data, command_data, module_data, parameter_data, grf_data, pose_data, position_data, velocity_data, current_data,voltage_data, time = read_data(freq,start_point,end_point,folder_name)
            # 2)  data process
            print(folder_name)
            velocity_data=(position_data[1:,:]-position_data[0:-1,:])*freq
            initial_velocity=[0,0,0, 0,0,0, 0,0,0, 0,0,0]
            velocity_data=np.vstack([initial_velocity,velocity_data])
            m=2.5;g=9.8; d=np.sqrt(pow(pose_data[-1,3]-pose_data[0,3],2)+pow(pose_data[-1,4]-pose_data[0,4],2)) #Displacement
            COT=EnergyCost(velocity_data,current_data,freq)/(m*g*d)
            COT_phaseReset[class_name].append(COT)# 
            print(COT_phaseReset[class_name][-1])

            
    #3) plot
    figsize=(5.1,4.1244)
    fig = plt.figure(figsize=figsize,constrained_layout=False)
    gs1=gridspec.GridSpec(6,1)#13
    gs1.update(hspace=0.18,top=0.95,bottom=0.12,left=0.12,right=0.98)
    axs=[]
    axs.append(fig.add_subplot(gs1[0:6,0]))

    labels=[str(ll) for ll in sorted([ round(float(ll)) for ll in categories])]
    ind= np.arange(len(labels))
    width=0.15

    #3.1) plot 
    COT_phaseModulation_values,COT_phaseReset_values=[],[]
    for i in labels:
        COT_phaseModulation_values.append(COT_phaseModulation[i])
        COT_phaseReset_values.append(COT_phaseReset[i])


    idx=0
    boxwidth=0.2
    box1=axs[idx].boxplot(COT_phaseModulation_values,widths=boxwidth, positions=ind-boxwidth/2,vert=True,patch_artist=True)
    box2=axs[idx].boxplot(COT_phaseReset_values,widths=boxwidth, positions=ind+boxwidth/2,vert=True,patch_artist=True)

    # fill with colors
    colors = ['lightblue', 'lightgreen']
    for bplot, color in zip((box1, box2),colors):
        for patch in bplot['boxes']:
            patch.set_facecolor(color)


    axs[idx].grid(which='both',axis='x',color='k',linestyle=':')
    axs[idx].grid(which='both',axis='y',color='k',linestyle=':')
    axs[idx].set_xticks(ind)
    #axs[idx].set_yticks([0,0.1,0.2,0.3])
    #axs[idx].set(ylim=[-0.01,0.3])
    axs[idx].set_xticklabels(['Normal', 'Carring payload', 'Malfunction leg', 'Noisy feedback' ])
    axs[idx].legend([box1['boxes'][0], box2['boxes'][0]],['Phase modulation','Phase reset'])
    axs[idx].set_ylabel(r'COT')
    axs[idx].set_xlabel(r'Situations')

    #axs[idx].set_title('Quadruped robot Walking on a slope using CPGs-based control with COG reflexes')
    # save figure
    folder_fig = data_file_dic + 'data_visulization/'
    if not os.path.exists(folder_fig):
        os.makedirs(folder_fig)
    figPath= folder_fig + str(localtimepkg.strftime("%Y-%m-%d %H:%M:%S", localtimepkg.localtime())) + 'COTStatistic.svg'
    plt.savefig(figPath)
    plt.show()

if __name__=="__main__":

    #test_neuralprocessing()
        
    ''' expected and actuall grf comparison'''
    #data_file_dic= "/home/suntao/workspace/experiment_data/"
    data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/StatisticData/PhaseModulation/"
    #plot_comparasion_expected_actual_grf_all_leg(data_file_dic,start_point=1,end_point=1000,freq=60.0,experiment_classes=['0'])

    '''   The routines are called'''
    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/PhaseTransition/Normal/"
    #PhaseAnalysis(data_file_dic, start_point=960, end_point=1560, freq=60.0, experiment_classes = ['-0.2'], trail_id=0)#1440-2160

    #plot_phase_transition_animation(data_file_dic,start_point=90,end_point=1200,freq=60.0,experiment_classes=['3'],trail_id=0)
    #plot_phase_diff(data_file_dic,start_point=240,end_point=2000,freq=60.0,experiment_classes=['0'],trail_id=0)

    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/StatisticData/PhaseModulation/"
    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/StatisticData/PhaseReset/"
    #plot_actual_grf_all_leg(data_file_dic, start_point=100, end_point=2000, freq=60.0, experiment_classes=['3'], trail_id=0)
    ''' Display phase diff among CPGs and the gait diagram'''
    #Phase_Gait(data_file_dic,start_point=240+60,end_point=721+360+60,freq=60.0,experiment_classes=['0'],trail_id=0)

    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/PhaseReset/Normal/SingleExperiment/"
    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/PhaseReset/Normal/"
    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/PhaseReset/AbnormalLeg/"
    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/PhaseReset/Payload/"
    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/PhaseReset/NoiseFeedback/"

    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/PhaseTransition/Normal/"
    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/PhaseTransition/AbnormalLeg/"
    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/PhaseTransition/Payload/"
    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/PhaseTransition/NoiseFeedback/"
    data_file_dic= "/home/suntao/workspace/experiment_data/"

    ''' The experiment one '''
    #GeneralDisplay(data_file_dic,start_point=240,end_point=721+240,freq=60.0,experiment_classes=['-0.2'],trail_id=0)

    ''' Display the general data of the convergence process '''
    data_file_dic= "/home/suntao/workspace/experiment_data/"
    #plot_actual_grf_all_leg(data_file_dic, start_point=0, end_point=2100, freq=60.0, experiment_classes=['0.9'], trail_id=1)
    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/StatisticData/PhaseReset/"
    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/StatisticData/PhaseModulation/"
    #data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/StatisticData/ParametersInvestigation/PhaseReset/"
    GeneralDisplay_All(data_file_dic,start_point=200,end_point=1200+900,freq=60.0,experiment_classes=['0.004'],trail_id=0)

    data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/StatisticData/"
    #plot_runningSuccess_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['0.0'])
    #plot_coordination_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['-0.2'])
    #plot_distance_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['0'])
    #plot_energyCost_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['-0.2'])
    #plot_COT_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['-0.2'])
    #plot_displacement_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['0'])
    #plot_stability_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['-0.2'])
    #phase_formTime_statistic(data_file_dic,start_point=0,end_point=1200+900,freq=60,experiment_classes=['0'])
    #phase_stability_statistic(data_file_dic,start_point=0,end_point=1200+900,freq=60,experiment_classes=['0'])

    #percentage_plot_runningSuccess_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['0.0'])
    #boxplot_phase_formTime_statistic(data_file_dic,start_point=0,end_point=1200+900,freq=60,experiment_classes=['0'])
    #boxplot_phase_stability_statistic(data_file_dic,start_point=0,end_point=1200+900,freq=60,experiment_classes=['0'])
    #boxplot_displacement_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['0'])
    #boxplot_stability_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['-0.2'])
    #boxplot_COT_statistic(data_file_dic,start_point=1200,end_point=1200+900,freq=60,experiment_classes=['-0.2'])

    data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/StatisticData/ParametersInvestigation/"
    #data_file_dic= "/home/suntao/workspace/experiment_data/"
    #phaseModulation_parameter_investigation_statistic(data_file_dic,start_point=0,end_point=1200+900,freq=60,experiment_classes=['0'])

    data_file_dic= "/media/suntao/DATA/Research/P3_workspace/Figures/experiment_data/StatisticData/ParametersInvestigation/"
    #data_file_dic= "/home/suntao/workspace/experiment_data/"
    #phaseReset_parameter_investigation_statistic(data_file_dic,start_point=0,end_point=1200+900,freq=60,experiment_classes=['0.0','0.05','0.15','0.25','0.35','0.45','0.5','0.55'])
