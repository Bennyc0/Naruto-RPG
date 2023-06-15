#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import csv
import time
import copy
import json
from collections import deque

import cv2 as cv
import numpy as np

from static.utils import CvFpsCalc
from static.utils import CvDrawText
from static.utils.model.yolox.yolox_onnx import YoloxONNX

# module used for creating command-line interfaces, allowing you to define and parse command-line arguments and options, making it easier to customize the behavior of your Python scripts from the command line.
# Essentially our conditions and variables
def get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", help='cap width', type=int, default=960)
    parser.add_argument("--height", help='cap height', type=int, default=540)

    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--skip_frame", type=int, default=0)

    parser.add_argument(
        "--model",
        type=str,
        default='static/utils/model/yolox/yolox_nano.onnx',
    )
    parser.add_argument(
        '--input_shape',
        type=str,
        default="416,416",
        help="Specify an input shape for inference.",
    )
    parser.add_argument(
        '--score_th',
        type=float,
        default=0.70,
        help='Class confidence',
    )
    parser.add_argument(
        '--nms_th',
        type=float,
        default=0.45,
        help='NMS IoU threshold',
    )
    parser.add_argument(
        '--nms_score_th',
        type=float,
        default=0.1,
        help='NMS Score threshold',
    )
    parser.add_argument(
        "--with_p6",
        action="store_true",
        help="Whether your model uses p6 in FPN/PAN.",
    )

    parser.add_argument("--sign_interval", type=float, default=3.0)
    parser.add_argument("--jutsu_display_time", type=int, default=3)

    parser.add_argument("--use_display_score", type=bool, default=False)
    parser.add_argument("--erase_bbox", type=bool, default=False)
    parser.add_argument("--use_jutsu_lang_en", type=bool, default=True)

    parser.add_argument("--chattering_check", type=int, default=3)

    parser.add_argument("--use_fullscreen", type=bool, default=False)

    args = parser.parse_args()

    return args


def ninjutsu_init():
    # Argument parsing #################################################################
    args = get_args()

    cap_width = args.width
    cap_height = args.height
    cap_device = args.device

    fps = args.fps
    skip_frame = args.skip_frame

    model_path = args.model
    input_shape = tuple(map(int, args.input_shape.split(',')))
    score_th = args.score_th
    nms_th = args.nms_th
    nms_score_th = args.nms_score_th
    with_p6 = args.with_p6

    sign_interval = args.sign_interval
    jutsu_display_time = args.jutsu_display_time

    use_display_score = args.use_display_score
    erase_bbox = args.erase_bbox
    use_jutsu_lang_en = args.use_jutsu_lang_en

    chattering_check = args.chattering_check

    # camera ready ###############################################################
    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    # model load ############################################################
    yolox = YoloxONNX(
        model_path=model_path,
        input_shape=input_shape,
        class_score_th=score_th,
        nms_th=nms_th,
        nms_score_th=nms_score_th,
        with_p6=with_p6,
        # providers=['CPUExecutionProvider'],
    )

    # FPS measurement module #########################################################
    cvFpsCalc = CvFpsCalc()

    # font loading ##########################################################
    # https://opentype.jp/kouzanmouhitufont.htm
    font_path = 'static/utils/font/衡山毛筆フォント.ttf'

    # label reading ###########################################################
    with open('static/data/labels.json', 'r') as f: 
        labels = json.load(f)
        labels = [row for row in jutsu]

    with open('static/data/jutsu.json', 'r') as f:  
        jutsu = json.load(f)
        jutsu = [row for row in jutsu]


    # Mark display history and detection history ##############################################
    sign_max_display = 18
    sign_max_history = 44
    sign_display_queue = deque(maxlen=sign_max_display)
    sign_history_queue = deque(maxlen=sign_max_history)

    chattering_check_queue = deque(maxlen=chattering_check)
    for index in range(-1, -1 - chattering_check, -1):
        chattering_check_queue.append(index)

    # Language setting for the technical name ###########################################################
    lang_offset = 0
    jutsu_font_size_ratio = sign_max_display
    if use_jutsu_lang_en:
        lang_offset = 1
        jutsu_font_size_ratio = int((sign_max_display / 3) * 4)

    # Other variable initialization #########################################################
    sign_interval_start = 0  # Mark interval start time initialization
    jutsu_index = 0  # index of display name
    jutsu_start_time = 0  # Initialization of the start time of the operation name display
    frame_count = 0  # frame number counter

    while True:
        start_time = time.time()

        # Camera Capture #####################################################
        ret, frame = cap.read()
        if not ret:
            continue
        frame_count += 1
        debug_image = copy.deepcopy(frame)

        if (frame_count % (skip_frame + 1)) != 0:
            continue

        # FPS Measurement ##############################################################
        fps_result = cvFpsCalc.get()

        # Detection enforcement #############################################################
        bboxes, scores, class_ids = yolox.inference(frame)

        # Add history of detections ####################################################
        for _, score, class_id in zip(bboxes, scores, class_ids):
            class_id = int(class_id) + 1

            # Discard results below detection threshold
            if score < score_th:
                continue

            # Marks are considered to be detected when the same mark continues for a specified number of times or more.
            chattering_check_queue.append(class_id)
            if len(set(chattering_check_queue)) != 1:
                continue

            # Register in queue only if the mark is different from the previous one
            if len(sign_display_queue
                   ) == 0 or sign_display_queue[-1] != class_id:
                sign_display_queue.append(class_id)
                sign_history_queue.append(class_id)
                sign_interval_start = time.time()  # Final detection time of mark

        # Clear history when specified time has passed since last mark detection ####################
        if (time.time() - sign_interval_start) > sign_interval:
            sign_display_queue.clear()
            sign_history_queue.clear()

        # conclusion (conclusion) of an artifact #########################################################
        jutsu_index, jutsu_start_time = check_jutsu(
            sign_history_queue,
            labels,
            jutsu,
            jutsu_index,
            jutsu_start_time,
        )

        # key processing ###########################################################
        # We need to change the method of input if we want to include this.
        # key = cv.waitKey(1)
        # if key == 99:  # C: Clear mark history
        #     sign_display_queue.clear()
        #     sign_history_queue.clear()

        # screen reflection #############################################################
        # We can send this into html to be a video src using jinja
        debug_image = draw_debug_image(
            debug_image,
            font_path,
            fps_result,
            labels,
            bboxes,
            scores,
            class_ids,
            score_th,
            erase_bbox,
            use_display_score,
            jutsu,
            sign_display_queue,
            sign_max_display,
            jutsu_display_time,
            jutsu_font_size_ratio,
            lang_offset,
            jutsu_index,
            jutsu_start_time,
        )

        # here cv.imshow( debug_image)
        # FPS adjustment #############################################################
        elapsed_time = time.time() - start_time
        sleep_time = max(0, ((1.0 / fps) - elapsed_time))
        time.sleep(sleep_time)

    cap.release()

def check_jutsu(
    sign_history_queue,
    labels,
    jutsu,
    jutsu_index,
    jutsu_start_time,
):
    # Matching technique name from mark history
    sign_history = ''
    if len(sign_history_queue) > 0:
        for sign_id in sign_history_queue:
            print(labels[sign_id][1])
            sign_history = sign_history + labels[sign_id][1]
            
        for index, signs in enumerate(jutsu):
            if sign_history == ''.join(signs[4:]):
                jutsu_index = index
                jutsu_start_time = time.time()  # Final detection time of the operation
                break

    return jutsu_index, jutsu_start_time


def draw_debug_image(
    debug_image,
    font_path,
    fps_result,
    labels,
    bboxes,
    scores,
    class_ids,
    score_th,
    erase_bbox,
    use_display_score,
    jutsu,
    sign_display_queue,
    sign_max_display,
    jutsu_display_time,
    jutsu_font_size_ratio,
    lang_offset,
    jutsu_index,
    jutsu_start_time,
):
    frame_width, frame_height = debug_image.shape[1], debug_image.shape[0]

    # Bounding box superimposed with "*" mark (when display option is enabled) ###################
    if not erase_bbox:
        for bbox, score, class_id in zip(bboxes, scores, class_ids):
            class_id = int(class_id) + 1

            # Discard bounding boxes below detection threshold
            if score < score_th:
                continue

            x1, y1 = int(bbox[0]), int(bbox[1])
            x2, y2 = int(bbox[2]), int(bbox[3])

            # Bounding box (square to match the long side)
            x_len = x2 - x1
            y_len = y2 - y1
            square_len = x_len if x_len >= y_len else y_len
            square_x1 = int(((x1 + x2) / 2) - (square_len / 2))
            square_y1 = int(((y1 + y2) / 2) - (square_len / 2))
            square_x2 = square_x1 + square_len
            square_y2 = square_y1 + square_len
            cv.rectangle(debug_image, (square_x1, square_y1),
                         (square_x2, square_y2), (255, 255, 255), 4)
            cv.rectangle(debug_image, (square_x1, square_y1),
                         (square_x2, square_y2), (0, 0, 0), 2)

            # Type of mark
            font_size = int(square_len / 2)
            debug_image = CvDrawText.puttext(
                debug_image, labels[class_id][1],
                (square_x2 - font_size, square_y2 - font_size), font_path,
                font_size, (185, 0, 0))

            # Detection score (with display option enabled)
            if use_display_score:
                font_size = int(square_len / 8)
                debug_image = CvDrawText.puttext(
                    debug_image, '{:.3f}'.format(score),
                    (square_x1 + int(font_size / 4),
                     square_y1 + int(font_size / 4)), font_path, font_size,
                    (185, 0, 0))

    # Header creation: FPS #########################################################
    header_image = np.zeros((int(frame_height / 18), frame_width, 3), np.uint8)
    header_image = CvDrawText.puttext(header_image, "FPS:" + str(fps_result),
                                      (5, 0), font_path,
                                      int(frame_height / 20), (255, 255, 255))

    # Footer creation: Mark history, and display of jutsu name ####################################
    footer_image = np.zeros((int(frame_height / 10), frame_width, 3), np.uint8)

    # Mark history string generation
    sign_display = ''
    if len(sign_display_queue) > 0:
        for sign_id in sign_display_queue:
            sign_display = sign_display + labels[sign_id][1]

    # Display of operation name (drawing at specified time)
    if lang_offset == 0:
        separate_string = '・'
    else:
        separate_string = '：'
    if (time.time() - jutsu_start_time) < jutsu_display_time:
        if jutsu[jutsu_index][0] == '':  # If there is no definition of the attribute (e.g., fire fugue)
            jutsu_string = jutsu[jutsu_index][2 + lang_offset]
        else:  # If there is a definition of an attribute (e.g., fire fugue)
            jutsu_string = jutsu[jutsu_index][0 + lang_offset] + \
                separate_string + jutsu[jutsu_index][2 + lang_offset]
        footer_image = CvDrawText.puttext(
            footer_image, jutsu_string, (5, 0), font_path,
            int(frame_width / jutsu_font_size_ratio), (255, 255, 255))
    # graphic display
    else:
        footer_image = CvDrawText.puttext(footer_image, sign_display, (5, 0),
                                          font_path,
                                          int(frame_width / sign_max_display),
                                          (255, 255, 255))

    #  Merge header and footer into debug image  ######################################
    debug_image = cv.vconcat([header_image, debug_image])
    debug_image = cv.vconcat([debug_image, footer_image])

    return debug_image

ninjutsu_init()