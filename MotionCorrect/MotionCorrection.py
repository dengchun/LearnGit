# -*- encoding: utf-8 -*-
'''
@File    :   MotionCorrection.py
@Time    :   2021/04/11 18:24:48
@Author  :   Xiaochuan LI  Chunyu Deng Jiaxin Li
@Version :   1.0
@Contact :   lixiaochuan@buua.edu.cn
@License :   (C)Copyright 2020-2021, Lixiaochuan-BUAA-vrlab
@Desc    :   None
'''








import numpy as np
import os
import pandas as pd
from scipy import signal
import linecache
import re
import argparse

def BVHtoDataFrame(filename):               #将BVH数据解析成DataFrame，将节点的角度和名称对应起来
    node_list=[]
    node_append_channel=[]

    f=open(filename)    #your path!

    for line in f:
        words=line.split()
        for word in words:
            if(word=='ROOT'):
                node_list.append(words[1])
            if(word=='JOINT'):
                node_list.append(words[1])
            
    
    f.close()

    index_node=0

    f=open(filename)    #your path!
    for line in f:
        words=line.split()
        for word in words:
            if(word=='CHANNELS'):
                for i in range(2,2+int(words[1])):
                    node_append_channel.append(node_list[index_node]+'-'+words[i])
                index_node+=1

    f.close()

    f = open(filename)
    flag = 0
    count = 0
    number_line_final = []
    for line in f:
        eachline = line.split()
        if(eachline[0] == 'Frame'):
            flag = 1
            continue
        if(flag):
            count += 1
            number_line = map(float, eachline)
            number_line = list(number_line)
            if(count!=1):
                number_line_final = np.vstack((number_line_final,number_line))
            else:
                number_line_final = number_line
    df = pd.DataFrame(data = number_line_final, columns=node_append_channel)

    return df

def BVHtoCSV(filename,targetname):              #将已经解析好的DataFrame存到csv文件中
    df = BVHtoDataFrame(filename)
    df.to_csv(targetname+".csv")

def JointAllAngle(filename,jointname,axis):     #获得BVH文件中某一结点的某一方向的全部角度值         
    df = BVHtoDataFrame(filename)               #axis   0代表x轴，1代表y轴，2代表z轴
    if(axis==0):
        column_name = jointname+'-Xrotation'
    elif(axis==1):
        column_name = jointname+'-Yrotation'
    elif(axis==2):
        column_name = jointname+'-Zrotation'
    else:
        print('axis error')
        return
    res = df[column_name].values
    return res

def mergeTxt(file1, file2):                     #将file2连接的file1文件的末尾
    f1 = open(file1, 'a+', encoding='utf-8')
    with open(file2, 'r', encoding='utf-8') as f2:
        f1.write('\n')
        for i in f2:
            f1.write(i)

def SaveBvhHead(input_filename):                #将BVH文件的数据结构部分提取出来
    
    with open(input_filename) as f:       #修改的目标文件位置
        num_total = len(f.readlines())
        num_total = int(num_total) 
    f.close()
    f=open(input_filename)    #your path!
    for line in f:
        words=line.split()
        for word in words:
            if(word=='Frames:'):
                num_frames=int(words[1])          #提取frame  
    f.close()
    Num_before_End=num_total-num_frames+1
    res_line=[]
    
    for line_frame2 in range(0,Num_before_End-1):
        the_line_frame2 = linecache.getline(input_filename, line_frame2)
        res_line.append(the_line_frame2)

    #干掉最后一行的换行符
    the_line_finall= linecache.getline(input_filename, Num_before_End-1)
    words1=the_line_finall.split()

    line_F=""
    for word2 in words1:
        line_F+=word2
        line_F+=' '
        
    res_line.append(line_F)
    
    fileObject = open('process.bvh', 'w')
    for ip2 in res_line:
        fileObject.write(ip2)
    fileObject.close()

def exponentialSmoothing(filename,jointname,axis):
    res = JointAllAngle(filename, jointname,axis)
    final = []
    for num in res:
        num = 0.0001*np.random.rand()
        final.append(num)
    df = BVHtoDataFrame(filename)
    if(axis==0):
        df[jointname+'-Xrotation'] = final
    elif(axis==1):
        df[jointname+'-Yrotation'] = final
    elif(axis==2):
        df[jointname+'-Zrotation'] = final
    else:
        print('axis error')
        return
    df.to_csv('result.csv')
    np.savetxt(r'process_tail.bvh', df.values, fmt='%f')
    SaveBvhHead(filename)
    mergeTxt('process.bvh', 'process_tail.bvh')
    os.remove('process_tail.bvh')

def downSmpling(oripath, trgPath, t=12):
    """对bvh文件等距下采样，实现抽帧的效果

    Args:
        oripath (str): bvh源文件路径
        trgPath (str): bvh目标文件路径
        t (int, optional): 采样率. Defaults to 12.
    """
    ptn = re.compile("Frame Time: (.*)")
    f_ptn = re.compile("Frames: (.*)")
    flag = False
    count = 0
    with open(oripath, "r") as fin:
        with open(trgPath, "w") as fout:
            lines = fin.readlines()
            for line in lines:
                res = f_ptn.match(line)
                if res:
                    f = str(int(res.group(1)) // t)
                    fout.write("Frames: {}\n".format(f))
                    continue
                res = ptn.match(line)
                if res:
                    time = str(float(res.group(1)) * t)
                    fout.write("Frame Time: {}\n".format(time))
                    flag = True
                else:
                    if flag:
                        if count % t == 0:
                            fout.write(line)
                        count += 1
                    else:
                        fout.write(line)

def MotionCorrection(oripath,trgPath,jointname,t):
    """
    对指定关节的动作进行滤波（去抖动）
    对bvh文件等距下采样，实现抽帧的效果

    Args:
        oripath (str): bvh源文件路径
        trgPath (str): bvh目标文件路径
        jointname (list): bvh文件中希望更改的节点名的列表
        t (int, optional): 采样率. Defaults to 12.
    """
    i = 0
    for name in jointname:
        i+=1
        if(i==1):
            exponentialSmoothing(oripath, name, 0)
        else:
            exponentialSmoothing('process.bvh', name, 0)

    downSmpling('process.bvh', trgPath)

#脚本内功能测试
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input", required=True,
	    help="path to input BVH file")
    ap.add_argument("-o", "--output", required=True,
	    help="path to output BVH file")
    ap.add_argument('--names', nargs='+',
        help="nodes need to fix")
    ap.add_argument("-f", "--frequency", required=True,type=int,
	    help="frequency of downsampling")
    args = vars(ap.parse_args())

    MotionCorrection(args["input"], args["output"], args["names"], args["frequency"])
