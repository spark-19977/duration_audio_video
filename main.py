import os
from pathlib import Path
import shutil

import mutagen.mp3
from moviepy.editor import VideoFileClip

AUDIO_DIR = Path('./audio')
VIDEO_DIR = Path('./otpt')
RESULT_DIR = Path('./sort')
if not os.path.exists(RESULT_DIR):
    os.mkdir(RESULT_DIR)


class Audio:
    def __init__(self, file):
        name, ext = file.split('.')
        self.name = name
        self.name_int = int(name)
        self.ext = ext

        self.duration = self.get_audio_duration(AUDIO_DIR / file)
        self.result_dst = RESULT_DIR / f'{name}.mp4'

    def __str__(self):
        return f'{self.name}.{self.ext}'

    def get_audio_duration(self, file):
        audio_duration = mutagen.mp3.MP3(file)
        return audio_duration.info.length


class Video:
    def __init__(self, file):
        name, ext = file.split('.')
        first_name, second_name = name.split('-')
        self.first_name = first_name
        self.first_name_int = int(first_name)
        self.second_name = second_name
        self.second_name_int = int(second_name)
        self.ext = ext
        self.path = VIDEO_DIR / file

        self.duration = self.get_video_duration(self.path)

    def __str__(self):
        return f'{self.first_name}-{self.second_name}.{self.ext}'

    def get_video_duration(self, file):
        clip = VideoFileClip(f'{file}')
        duration = clip.duration
        clip.close()
        return duration


def infinite_generator(video_ls: list):
    result = {video.first_name_int for video in video_ls}
    result = sorted(result)
    while True:
        for i in result:
            yield i

def find_closest_video_file(audio_file, video_files, numbers):
    if not video_files:
        raise ValueError('Video files ended')

    extracted_video_files = [*filter(lambda x: x.first_name_int == audio_file.name_int, video_files)]
    while not extracted_video_files:
        number = next(numbers)
        extracted_video_files = [*filter(lambda x: x.first_name_int == number, video_files)]
    extracted_video_files.sort(key=lambda x: (abs(x.duration-audio_file.duration), x.second_name_int))
    # print(audio_file.duration, [i.duration for i in extracted_video_files])
    return extracted_video_files[0]

def main():
    audio_files = []
    for file in os.listdir(AUDIO_DIR):
        try:
            audio_files.append(Audio(file))
        except Exception as err:
            print(err)
    audio_files.sort(key=lambda x: x.name_int)

    video_files = []
    for file in os.listdir(VIDEO_DIR):
        try:
            video_files.append(Video(file))
        except Exception as err:
            print(err)
    numbers = infinite_generator(video_files)

    for audio_file in audio_files:
        result = find_closest_video_file(audio_file, video_files, numbers)
        video_files.remove(result)
        shutil.move(result.path, audio_file.result_dst)
        print(f'copied from {result.path} to {audio_file.result_dst}')


if __name__ == '__main__':
    main()
