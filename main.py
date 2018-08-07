from pydub.silence import split_on_silence
from pydub import AudioSegment
import os
import multiprocessing as mp


def process(name):
    (filepath, tmpfilename) = os.path.split(name)
    (filename, extension) = os.path.splitext(tmpfilename)
    sound = AudioSegment.from_mp3(name)
    chunks = split_on_silence(sound, min_silence_len=700, silence_thresh=-70)
    i = 0
    silence = AudioSegment.silent(duration=5000)
    new = AudioSegment.empty()
    for chunk in chunks:
        new += chunk + silence
    new.export(os.path.join(filepath, filename + "_new.mp3"), format='mp3')


if __name__ == '__main__':
    dir = '/Users/zachary/Documents/资料/资料/英语/雅思王听力真题语料库/Chapter 5 吞音连读混合训练语料库/02 横向测试'
    files = os.listdir(dir)
    for i in range(len(files)):
        files[i] = os.path.join(dir, files[i])

    pool = mp.Pool()
    pool.map(process, files)

