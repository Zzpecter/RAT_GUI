import argparse
import sys

annFile = './Projects/testHard/tinyYolo.ann'
newFile = './newAnn.ann'


#oldRes = (1920, 1080)
#newRes = (960, 540)

def print_progress(i, n, prefix='', suffix='', decimals=3, bar_length=100):

    format_str = "{0:." + str(decimals) + "f}"  # format the % done number string
    percents = format_str.format(100 * (i / float(n)))  # calculate the % done
    filled_length = int(round(bar_length * i / float(n)))  # calculate the filled bar length
    bar = '#' * filled_length + '-' * (bar_length - filled_length)  # generate the bar string
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),  # write out the bar
    sys.stdout.flush()

def save_annotation_to_file(filename, author, len_check, frames_per_second):
    with open(filename, "w") as f:
        f.write(f'author:§{author}§ lenght:§{len_check}§ fps:§{frames_per_second}§\n')

def update_annotation_scale(filename, new_filename, scale=4):
    """
    NOT SURE FOR WHAT THIS IS USED
    :param filename:
    :return:
    """

    with open(filename, "r") as f:
        for line in f[1:]:

            if '.' in line:
                class_id, x1, y1, x2, y2 = line.split(' ')
                bbox = [float(x1)/scale, float(y1)/scale, float(x2)/scale, float(y2)/scale]


                with open(new_filename, "a") as f:
                    f.write(f'{class_id} {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n')
            elif len(line) is 0:
                #eof
                break
            else:
                #frame number lines
                with open(newFile, "a") as f:
                    f.write('{}\n'.format(int(line)))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--prediction_folder', type=str, default='data/preds/raw', help='path to raw predictions')
    parser.add_argument('-i', '--image_folder', type=str, default='data/images', help='path to images')
    parser.add_argument('-l', '--label_folder', type=str, default='data/labels', help='path to labels')
    parser.add_argument('-c', '--classes', nargs='+' , default='', help='list of classes, the elements are expected to be ordered by the class_id')

    args = parser.parse_args()
