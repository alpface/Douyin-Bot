# -*- coding: utf-8 -*-
import sys
import random
import time
from PIL import Image
import wda

if sys.version_info.major != 3:
    print('Please run under Python3')
    exit(1)
try:
    from common import   UnicodeStreamFilter
    from common import apiutil
    from common.compression import resize_image
except Exception as ex:
    print(ex)
    print('请将脚本放在项目根目录中运行')
    print('请检查项目根目录中的 common 文件夹是否存在')
    exit(1)

VERSION = "0.0.1"

# 我申请的 Key，随便用，嘻嘻嘻
# 申请地址 http://ai.qq.com
AppID = '2110553487'
AppKey = 'sQayjEgeUcWscxt3'

DEBUG_SWITCH = True
FACE_PATH = 'face/'

c = wda.Client()
s = c.session()

# 审美标准
BEAUTY_THRESHOLD = 80

# 最小年龄
GIRL_MIN_AGE = 18


def yes_or_no():
    """
    检查是否已经为启动程序做好了准备
    """
    while True:
        yes_or_no = str(input('请确保手机打开了 ADB 并连接了电脑，'
                              '然后打开手机软件，确定开始？[y/n]:'))
        if yes_or_no == 'y':
            break
        elif yes_or_no == 'n':
            print('谢谢使用', end='')
            exit(0)
        else:
            print('请重新输入')


def _random_bias(num):
    """
    random bias
    :param num:
    :return:
    """
    print('num = ', num)
    return random.randint(-num, num)

duration = 1.0
def GetPageSize():
    size = s.window_size()
    x = size.width
    y = size.height
    return (x, y)

def swipe_left():
    size = GetPageSize()
    sx = size[0] * 0.57
    sy = size[1] * 0.75
    ex = size[0] * 0.55
    ey = 0
    s.swipe(sx, sy, -ex, ey, duration)


def swipe_right():
    size = GetPageSize()
    sx = size[0] * 0.43
    sy = size[1] * 0.75
    ex = size[0] * 0.54
    ey = 0
    s.swipe(sx, sy, ex, ey, duration)


def swipe_up():
    '''
    start_x - 滑动开始x轴坐标
    start_y - 滑动开始y轴坐标
    end_x - 滑动结束x轴偏移量
    end_y - 滑动结束y轴偏移量
    :return:
    '''
    size = GetPageSize()
    start_x = size[0] * 0.43
    start_y = size[1] * 0.75
    end_x = 0
    end_y = size[1] * 0.55
    s.swipe(start_x, start_y, end_x, -end_y, duration)


def swipe_down():
    size = GetPageSize()
    sx = size[0] * 0.35
    sy = size[1] * 0.45
    ex = 0
    ey = size[1] * 0.55
    s.swipe(sx, sy, ex, ey, duration)


def follow_user():
    """
    关注用户
    :return:
    """
    # s.tap_hold(config['follow_bottom']['x'] + _random_bias(10), config['follow_bottom']['y'] + _random_bias(10), 0.01)
    # time.sleep(0.5)


def thumbs_up():
    """
    点赞
    :return:
    """
    # s.tap_hold(config['star_bottom']['x'] + _random_bias(10), config['star_bottom']['y'] + _random_bias(10), 0.01)
    # size = GetPageSize()
    # width = size[0]
    # height = size[1]
    # s.double_tap(width / 2, height / 2)
    # time.sleep(0.5)


def next_page():
    """
    翻到下一页
    :return:
    """
    print(s.window_size())
    # s.swipe_up()
    swipe_up()
    # s.swipe(config['center_point']['x'], config['center_point']['y']+config['center_point']['ry'],
    #         config['center_point']['x'], config['center_point']['y'], 0.3)
    # time.sleep(1.5)


def main():
    """
    main
    :return:
    """
    print('程序版本号：{}'.format(VERSION))
    print('激活窗口并按 CONTROL + C 组合键退出')

    while True:

        next_page()

        time.sleep(1)
        c.screenshot('snapshotting.png')
        Image.open('snapshotting.png')
        resize_image('snapshotting.png', 'optimized.png', 1024 * 1024)

        with open('optimized.png', 'rb') as bin_data:
            image_data = bin_data.read()

        ai_obj = apiutil.AiPlat(AppID, AppKey)
        rsp = ai_obj.face_detectface(image_data, 0)

        major_total = 0
        minor_total = 0

        if rsp['ret'] == 0:
            beauty = 0
            for face in rsp['data']['face_list']:
                print(face)
                face_area = (face['x'], face['y'], face['x']+face['width'], face['y']+face['height'])
                print(face_area)
                img = Image.open("optimized.png")
                cropped_img = img.crop(face_area).convert('RGB')
                cropped_img.save(FACE_PATH + face['face_id'] + '.png')
                # 性别判断
                if face['beauty'] > beauty and face['gender'] < 50:
                    beauty = face['beauty']

                if face['age'] > GIRL_MIN_AGE:
                    major_total += 1
                else:
                    minor_total += 1

            # 是个美人儿~关注点赞走一波
            if beauty > BEAUTY_THRESHOLD and major_total > minor_total:
                print('发现漂亮妹子！！！')
                thumbs_up()
                follow_user()

        else:
            print(rsp)
            continue


if __name__ == '__main__':
    try:
        # yes_or_no()
        main()
    except KeyboardInterrupt:
        s.close()
        print('谢谢使用')
        exit(0)
