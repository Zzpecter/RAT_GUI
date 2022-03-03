
annFile = './Projects/testHard/tinyYolo.ann'
newFile = './newAnn.ann'


#oldRes = (1920, 1080)
#newRes = (960, 540)

with open(newFile, "w") as f:
    f.write('author:§tinyYolo§ lenght:§1625§ fps:§d§\n')

with open(annFile, "r") as f:
    for line in f:

        if line[0] is 'a':
            #first line
            pass
        elif line[0] is '0':
            #annotation lines
            items = line.split()
            aBox = [float(items[1])/4, float(items[2])/4, float(items[3])/4, float(items[4])/4]


            with open(newFile, "a") as f:
                f.write('0 {} {} {} {}\n'.format(aBox[0], aBox[1], aBox[2], aBox[3]))
        elif len(line) is 0:
            #eof
            break
        else:
            #frame number lines
            with open(newFile, "a") as f:
                f.write('{}\n'.format(int(line)))