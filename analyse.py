#!/usr/local/bin/python3
import os
import pickle

from asciimatics.screen import *
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import multiprocessing as mp


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


if __name__ == '__main__':
    directory = '/Users/zachary/Documents/资料/资料/英语/雅思王听力真题语料库/Chapter 5 吞音连读混合训练语料库/02 横向测试'
    files = os.listdir(directory)
    for i in range(len(files)):
        files[i] = os.path.join(directory, files[i])

    pool = mp.Pool()
    pool.map(process, files)