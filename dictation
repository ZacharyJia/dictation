#!/usr/local/bin/python3
import os
import pickle
import warnings

warnings.filterwarnings("ignore")

from asciimatics.screen import *
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from pydub.playback import play


not_silence_ranges = None
sound = None
file_name = None


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


def ui(screen):
    global not_silence_ranges
    global sound
    i = 0
    total = len(not_silence_ranges)
    while True:
        screen.print_at(file_name, 0, 0)
        screen.print_at('进度：' + str(i) + "/" + str(total), 0, 1)
        screen.print_at('操作： 空格键->下一句  P->上一句  R->重复本句  Q->退出', 0, screen.height - 1)

        ev = screen.get_key()
        if ev == 32:  #空格
            if i < total:
                start_i, end_i = not_silence_ranges[i]
                i += 1
                play(sound[start_i:end_i])
        if ev in (ord('p'), ord('P')):
            if i > 1:
                i -= 2
                start_i, end_i = not_silence_ranges[i]
                i += 1
                play(sound[start_i:end_i])

        if ev in (ord('r'), ord('R')):
            if i > 0:
                i -= 1
                start_i, end_i = not_silence_ranges[i]
                i += 1
                play(sound[start_i:end_i])

        if ev in (ord('Q'), ord('q')):
            return

        screen.refresh()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage:  dictation.py [filename]')
        exit(0)

    file_name = sys.argv[1]
    process(file_name)
    read_wf(file_name)
    Screen.wrapper(ui)
