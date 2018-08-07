#!/usr/local/bin/python3
import os
import pickle
import warnings
import time
import sys

warnings.filterwarnings("ignore")

from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.widgets import Frame, Layout, Text, Button
from asciimatics.exceptions import StopApplication
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from pydub.playback import play


not_silence_ranges = None
sound = None
file_name = None
interval = 0
i = 0


def process(name):
    global sound
    global not_silence_ranges
    (filepath, tmpfilename) = os.path.split(name)
    (filename, extension) = os.path.splitext(tmpfilename)

    if os.path.exists(os.path.join(filepath, filename + '.wf')):
        return
    print("正在分析文件中......")

    sound = AudioSegment.from_mp3(name)
    not_silence_ranges = detect_nonsilent(sound, min_silence_len=700, silence_thresh=-70, seek_step=1)

    with open(os.path.join(filepath, filename + '.wf'), 'wb') as f:
        pickle.dump(not_silence_ranges, f)


def read_wf(name):
    global not_silence_ranges
    global sound
    if not_silence_ranges is not None and sound is not None:
        return
    (filepath, tmpfilename) = os.path.split(name)
    (filename, extension) = os.path.splitext(tmpfilename)
    sound = AudioSegment.from_mp3(name)
    with open(os.path.join(filepath, filename + '.wf'), 'rb') as f:
        not_silence_ranges = pickle.load(f)



class InputFrame(Frame):
    def __init__(self, screen, text, on_ok, on_cancel=None, height=6, weight=50):
        super(InputFrame, self).__init__(screen, height, weight, has_shadow=True, has_border=True)
        self.on_ok = on_ok
        layout = Layout([1])
        self.add_layout(layout)
        layout.add_widget(Text(text, 'data'))
        layout.add_widget(Button("确定", self._btn_ok))
        layout.add_widget(Button('取消', on_cancel if on_cancel is not None else self._btn_cancel))
        self.fix()
            
    def _btn_cancel(self):
        raise StopApplication('')

    def _btn_ok(self):
        self.save()
        data = self.data['data']
        self.on_ok(data)
        raise StopApplication('')


def interval_btn_ok(data):
    global interval
    interval = int(data)


def jump_btn_ok(data):
    global i
    i = int(data)


def ui(screen):
    global not_silence_ranges
    global sound
    global i
    i = 0
    total = len(not_silence_ranges)
    next_play_time = 0
    auto_play = False
    fresh_and_play_immediately = False


    while True:
        screen.print_at(file_name, 0, 0)
        screen.print_at('进度：' + str(i) + "/" + str(total), 0, 1)
        screen.print_at('空格键=下一句  P=上一句  R=重复本句  Q=退出  A=自动播放  S=关闭自动播放  J=跳转播放', 0, screen.height - 1)
        screen.print_at('自动播放：' + ('开启' if auto_play else '关闭')
                + (('    间隔' + str(interval) + 's') if auto_play else ''), 0, 2)

        if fresh_and_play_immediately:
            screen.refresh()
            start_i, end_i = not_silence_ranges[i - 1]
            play(sound[start_i:end_i])
            fresh_and_play_immediately = False

        ev = screen.get_key()
        if ev in (32, Screen.KEY_RIGHT, Screen.KEY_DOWN):  #空格
            if i < total:
                start_i, end_i = not_silence_ranges[i]
                i += 1
                screen.print_at('进度：' + str(i) + "/" + str(total), 0, 1)
                screen.refresh()
                play(sound[start_i:end_i])
        if ev in (ord('p'), ord('P'), Screen.KEY_LEFT, Screen.KEY_UP):
            if i > 1:
                i -= 2
                start_i, end_i = not_silence_ranges[i]
                i += 1
                screen.print_at('进度：' + str(i) + "/" + str(total), 0, 1)
                screen.refresh()
                play(sound[start_i:end_i])

        if ev in (ord('r'), ord('R')):
            if i > 0:
                i -= 1
                start_i, end_i = not_silence_ranges[i]
                i += 1
                play(sound[start_i:end_i])

        if ev in (ord('a'), ord('A')):
            screen.play([Scene([InputFrame(screen, '播放间隔（秒）：', interval_btn_ok)])], repeat=False)
            screen.clear()
            auto_play = True
            next_play_time = time.time() + 1

        if ev in (ord('s'), ord('S')):
            screen.clear()
            auto_play = False
        
        if ev in (ord('Q'), ord('q')):
            return

        if ev in (ord('J'), ord('j')):
            screen.play([Scene([InputFrame(screen, '跳转到第几句：', jump_btn_ok)])], repeat=False)
            screen.clear()
            fresh_and_play_immediately = True

        if auto_play and time.time() >= next_play_time:
            start_i, end_i = not_silence_ranges[i]
            play(sound[start_i:end_i])
            i += 1
            next_play_time = time.time() + interval
        screen.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage:  dictation.py [filename]')
        exit(0)

    file_name = sys.argv[1]
    process(file_name)
    read_wf(file_name)

    Screen.wrapper(ui)
