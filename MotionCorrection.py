# -*- encoding: utf-8 -*-
"""
@File    :   MotionCorrection.py
@Time    :   2021/04/11 18:24:48
@Author  :   Xiaochuan LI  Chunyu Deng Jiaxin Li
@Version :   1.0
@Contact :   lixiaochuan@buua.edu.cn
@License :   (C)Copyright 2020-2021, Lixiaochuan-BUAA-vrlab
@Desc    :   None
"""


import numpy as np
import os
import pandas as pd
from scipy import signal
import linecache
import re
import argparse
import matplotlib.pyplot as plt


def BVHtoDataFrame(filename):  # 将BVH数据解析成DataFrame，将节点的角度和名称对应起来
    node_list = []
    node_append_channel = []

    f = open(filename)
    namePTN = re.compile("(ROOT|JOINT) (.*)")
    channelPTN = re.compile("CHANNELS \d (.*)")
    matrixPTN = re.compile("([\d|\.|\s|-]{1,})")

    tmpName = ""
    colName = []
    angData = []
    header = ""
    with open(filename, "r") as fin:
        for line in fin.readlines():
            simLine = line.strip()
            if matrixPTN.match(simLine):
                angData.append(list(map(float, simLine.split(" "))))
            else:
                header += line
                if namePTN.match(simLine):
                    tmpName = namePTN.match(simLine).group(2)
                elif channelPTN.match(simLine):
                    channels = channelPTN.match(simLine).group(1).split(" ")
                    colName += ["{}_{}".format(tmpName, x) for x in channels]
                else:
                    continue
    df = pd.DataFrame(data=np.array(angData), columns=colName)
    return df, header


def BVHtoCSV(filename, targetname):  # 将已经解析好的DataFrame存到csv文件中
    df, _ = BVHtoDataFrame(filename)
    df.to_csv(targetname + ".csv")


def exponentialSmoothing(data, alpha=0.8):
    data = data.reshape(data.shape[0], -1)
    S = data.copy()
    S[0] = np.mean(S, axis=0)
    for i in range(1, data.shape[0]):
        S[i] = S[i - 1] * alpha + S[i] * (1 - alpha)
    return S


def lowPassSmoothing(data, deg=8, ratio=0.01):
    data = data.reshape(data.shape[0], -1)
    b, a = signal.butter(deg, ratio, "lowpass")
    for i in range(data.shape[1]):
        data[:, i] = signal.filtfilt(b, a, data[:, i])
    return data


def zerolizeSmoothing(data, factor=0.0001):
    size = data.shape
    randarr = factor * np.random.randn(*size)
    return randarr.reshape(size[0], -1)


def processSmoothing(filename, jointNames, methods="el"):
    channels = ["Xrotation", "Yrotation", "Zrotation"]
    processCols = []
    for jointName in jointNames:
        processCols += ["{}_{}".format(jointName, channel) for channel in channels]
    df, header = BVHtoDataFrame(filename)
    smootherDict = {
        "e": exponentialSmoothing,
        "l": lowPassSmoothing,
        "z": zerolizeSmoothing,
    }
    assert all(
        [method in smootherDict for method in methods]
    ), "Smooth Option Not Valide"
    processedData = df[processCols].values
    for method in methods:
        processedData = smootherDict[method](processedData)
    # anal(ori=df[processCols].values, trg=processedData, title=methods)     # 可视化分析
    df[processCols] = processedData
    dataStr = "\n".join([" ".join(map(str, x)) for x in df.values])
    return header + dataStr


def anal(ori, trg, title="title"):
    plt.figure()
    for i in range(ori.shape[1]):
        plt.subplot(ori.shape[1], 1, i + 1)
        plt.title(title)
        plt.plot(np.arange(ori.shape[0]), ori[:, i], label="ori")
        plt.plot(np.arange(trg.shape[0]), trg[:, i], label="trg")
        plt.legend()
    plt.show()


def downSmpling(bvhStr, trgPath, t=12):
    """对bvh文件等距下采样，实现抽帧的效果

    Args:
        bvhStr (str): bvh源文件字符串
        trgPath (str): bvh目标文件路径
        t (int, optional): 采样率. Defaults to 12.
    """
    ptn = re.compile("Frame Time: (.*)")
    f_ptn = re.compile("Frames: (.*)")
    flag = False
    count = 0
    with open(trgPath, "w") as fout:
        lines = bvhStr.split("\n")
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
                        fout.write(line + "\n")
                    count += 1
                else:
                    fout.write(line + "\n")


def MotionCorrection(oripath, trgPath, jointNames, t=12, methods="el"):
    """
    对指定关节的动作进行滤波（去抖动）
    对bvh文件等距下采样，实现抽帧的效果

    Args:
        oripath (str): bvh源文件路径
        trgPath (str): bvh目标文件路径
        jointNames (list): bvh文件中希望更改的节点名的列表
        t (int, optional): 采样率. Defaults to 12.
        method (str): 优化方法，可选项{e: 指数平滑, l:低通滤波, z:置零}
    """
    correctStr = processSmoothing(oripath, jointNames, methods=methods)
    downSmpling(correctStr, trgPath)


def test():
    MotionCorrection(
        "data/get.bvh", "test_exp_01.bvh", ["RightElbow", "LeftElbow"], methods="e"
    )
    MotionCorrection(
        "data/get.bvh", "test_low_0001_8.bvh", ["RightElbow", "LeftElbow"], methods="l"
    )
    MotionCorrection(
        "data/get.bvh", "test_zero.bvh", ["RightElbow", "LeftElbow"], methods="el"
    )


# 脚本内功能测试
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-i", "--input", required=True, help="path to input BVH file"
    )  # -i bvh源文件路径
    ap.add_argument(
        "-o", "--output", required=True, help="path to output BVH file"
    )  # -o bvh目标文件路径
    ap.add_argument(
        "--names", nargs="+", help="nodes need to fix"
    )  # --names bvh文件希望更改的节点名的列表
    ap.add_argument(
        "-m",
        "--methods",
        required=False,
        default="el",
        help="optimize method",
    )  # -m 优化方法组合，可选项（e/l/z），默认zl
    ap.add_argument(
        "-f", "--frequency", required=True, type=int, help="frequency of downsampling"
    )  # -f 采样频率
    args = vars(ap.parse_args())
    MotionCorrection(
        args["input"],
        args["output"],
        args["names"],
        args["frequency"],
        methods=args["methods"],
    )
