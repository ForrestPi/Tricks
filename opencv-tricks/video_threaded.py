#!/usr/bin/env python3

'''
Multithreaded video processing minimal sample.
Usage:
   python3 video_threaded.py
   Shows how python threading capabilities can be used
   to organize parallel captured frame processing pipeline
   for smoother playback.
Keyboard shortcuts:
   ESC - exit
'''
from collections import deque
from multiprocessing.pool import ThreadPool

import cv2 as cv

VIDEO_SOURCE = 0


def process_frame(frame):
    # some intensive computation...
    frame = cv.medianBlur(frame, 19)
    return frame


if __name__ == '__main__':
    # Setup.
    cap = cv.VideoCapture(VIDEO_SOURCE)
    thread_num = cv.getNumberOfCPUs()
    pool = ThreadPool(processes=thread_num)
    pending_task = deque()

    while True:
        # Consume the queue.
        while len(pending_task) > 0 and pending_task[0].ready():
            res = pending_task.popleft().get()
            cv.imshow('threaded video', res)

        # Populate the queue.
        if len(pending_task) < thread_num:
            frame_got, frame = cap.read()
            if frame_got:
                task = pool.apply_async(process_frame, (frame.copy(),))
                pending_task.append(task)

        # Show preview.
        if cv.waitKey(1) == 27 or not frame_got:
            break

cv.destroyAllWindows()