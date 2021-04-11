"""
@author:  Lijiaxin 
@contact: octo
"""
#输出BVH文件头的顺序结果


import os
import sys
def PrintHvhNode():
    if len(sys.argv) < 1:    
        sys.exit("python error")  
    param_input_file_dir = sys.argv[1]
    node_list=[]
    node_append_channel=[]
    f=open(param_input_file_dir)    #your path!
    for line in f:
        words=line.split()
        for word in words:
            if(word=='ROOT'):
                node_list.append(words[1])
            if(word=='JOINT'):
                node_list.append(words[1])
    f.close()
    index_node=0
    f=open(param_input_file_dir)    #your path!
    for line in f:
        words=line.split()
        for word in words:
            if(word=='CHANNELS'):
                for i in range(2,2+int(words[1])):
                    node_append_channel.append(node_list[index_node]+'-'+words[i])
                index_node+=1

    f.close()
    print(node_append_channel)



#PrintHvhNode('D:/11.bvh')
if __name__ == '__main__':
    PrintHvhNode()


