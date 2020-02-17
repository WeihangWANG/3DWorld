import os
len = [0,0,7,7,5,4,5,6]
for i in range(2,8):
    if not os.path.exists("ch%s"%i):
        os.mkdir("ch%s"%i)
    for j in range(1,len[i]):
        os.mkdir("ch%s/%s.%s"%(i,i,j))


