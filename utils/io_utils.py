import argparse
import sys

annFile = './Projects/testHard/tinyYolo.ann'
newFile = './newAnn.ann'


#oldRes = (1920, 1080)
#newRes = (960, 540)

def print_progress(i, n, prefix='', suffix='', decimals=3, bar_length=100):
    format_str = "{0:." + str(decimals) + "f}"
    percents = format_str.format(100 * (i / float(n)))
    filled_length = int(round(bar_length * i / float(n)))
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    sys.stdout.flush()





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--prediction_folder', type=str, default='data/preds/raw', help='path to raw predictions')
    parser.add_argument('-i', '--image_folder', type=str, default='data/images', help='path to images')
    parser.add_argument('-l', '--label_folder', type=str, default='data/labels', help='path to labels')
    parser.add_argument('-c', '--classes', nargs='+' , default='', help='list of classes, the elements are expected to be ordered by the class_id')

    args = parser.parse_args()
