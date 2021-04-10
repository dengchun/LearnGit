

"""
@author:  Lijiaxin Guoshuai
@contact: octo

"""




import os
import linecache
import sys

def main():
    if len(sys.argv) < 3: 
          sys.exit("python error")  
    param_input_file_dir = sys.argv[1] #第二个参数  输入文件得路径
    param_output_file_dir = sys.argv[2] #第三个参数 输出文件得路径
    param_ratio=sys.argv[3]             #第四个参数 放大得倍率
    param_ratio=int(param_ratio)
    lines=[]         #初次遍历文件的内容
    replace=[]       #提取 OFFSET后面的数字并且*100后
    poss=[]          #提取文件中OFFSET前面的空格数量
    i=0
    num_frames=0    #提取文件中的帧数  保存到这个变量
    num_total=0        #文件的总共的行数  后面的帧数的开始位置即是  总行数 减去 帧数  加上 1
    Origin_line=0      #帧数的初始行
    with open(param_input_file_dir) as f:       #修改的目标文件位置
        num_total = len(f.readlines())
        num_total = int(num_total)
    f.close()
    f=open(param_input_file_dir)    #your path!
    for line in f:
        words=line.split()
        for word in words:
            if(word=='OFFSET'):
                for i in range(1,4):
                    replace.append(float(words[i])*param_ratio)
                pos=line.find('O')
                poss.append(pos)
            if(word=='Frames:'):
                num_frames=int(words[1])          #提取frame
            #print(replace)
        lines.append(line)

  
    f.close()
    replace_str=[]
    for n in range(0,len(replace)):
        s="{:.6f}".format(replace[n])
        replace_str.append(s)
    lines_new=[]
    for n_line in range(0,len(poss)):
        line_new=""
        for n_k in range(0,poss[n_line]):
            line_new+=" "
        line_new+="OFFSET "
        line_new+=replace_str[n_line*3+0]
        line_new+=" "
        line_new+=replace_str[n_line*3+1]
        line_new+=" "
        line_new+=replace_str[n_line*3+2]
        line_new+="\n"
        lines_new.append(line_new)
        
    lines1=[]  #后面的输出到txt文件的lis


    n_replace_indes=0
    f=open(param_input_file_dir)    #your path!
    for line in f:
        words=line.split()
        for word in words:
            if(word=='OFFSET'):
                line=lines_new[n_replace_indes]
                n_replace_indes+=1
       # print(line)
        lines1.append(line)
    f.close()
    fileObject = open(param_output_file_dir, 'w')
    for ip in lines1:
	    fileObject.write(ip)
    fileObject.close()
    Origin_line=num_total-num_frames+1           #帧数前三列需要乘100的初始行数

    Num3100_Frame=[]                     #提取frame每行的前三个数字 乘以100

    Replace_Num3100_Frame=[]            #将提取到的数据格式化保存
    for line_frame in range(Origin_line,num_total+1):
        the_line_frame = linecache.getline(param_input_file_dir, line_frame)
        words_frame=the_line_frame.split()
        for i in range(0,3):
            Num3100_Frame.append(float(words_frame[i])*param_ratio)
    for i in range(0,len(Num3100_Frame)):
        s="{:.6f}".format(Num3100_Frame[i])
        Replace_Num3100_Frame.append(s)
    line_after_frame=[]

    frame_index=0
    for line_frame2 in range(0,num_total+1):
        the_line_frame2 = linecache.getline(param_output_file_dir, line_frame2)
        if(line_frame2>=Origin_line):
            frame_words=the_line_frame2.split()
            the_line_frame2_replace=""
            for j in range(0,3):
                the_line_frame2_replace+=Replace_Num3100_Frame[frame_index*3+j]
                the_line_frame2_replace+=" "
            for w in range(3,len(frame_words)):
                the_line_frame2_replace+=frame_words[w]
                the_line_frame2_replace+=" "
            the_line_frame2_replace+="\n"
            the_line_frame2=the_line_frame2_replace
            frame_index+=1
        


        line_after_frame.append(the_line_frame2)
        fileObject = open(param_output_file_dir, 'w')
    for ip2 in line_after_frame:
	    fileObject.write(ip2)
    fileObject.close()

if __name__ == '__main__':
    main()
