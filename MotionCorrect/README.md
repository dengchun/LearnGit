# MotionCorrection.py

# BVH局部优化算法
##### 李小川 李嘉鑫 邓春雨

### 算法描述
BVH局部优化算法，通过指数平滑等方法独立优化BVH文件动作序列的指定关节，并以一定的采样频率进行抽帧处理

### 算法目标
1. 粗略过滤掉某些关节明显可见的抖动  √
2. 粗略过滤旋转异常
3. 抽帧处理

### 算法输入
1. BVH文件路径
2. 关节名称
3. 目标存储路径

### 算法输出
null

### 迭代记录
1. 初次提交，实现指数平滑方法、低通滤波方法。表现较差，需要确定原因，暂时使用置零替代。（2021.4.11）

### 调用方式
`python MotionCorrection.py -i [input_bvh_file_dir] -o [out_bvh_file_dir] --names [RightElbow LeftElbow ......] -f [frequency of down sampling]`
  
  
   

   
