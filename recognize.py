# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pytesseract
import glob
import cv2
import random
import re
import os
from random import randint

import s3_bucket

extra_symbols = r"\»|\<|\>|\)|\(|\d+|\?|\-|\.|\,|\!|\/|\;|\:|\:-|\_|\—|\n|\|"

def get_cropped_word(postfix, points, orig):
    (xmin, xmax, ymin) = points

    file_name = 'cropped %s (%s).png' % postfix
    path = './cropped/' + file_name

    (xmin, xmax) = (0 if xmin-7 < 0 else xmin-7, xmax+10)
    (ymin, ymax) = (0 if ymin-32 < 0 else ymin-32, ymin+7)

    cropped = orig[ymin:ymax, xmin:xmax]
    print('cropping by: ymin: %s, ymax: %s, xmin: %s, xmax: %s' % (ymin, ymax, xmin, xmax))

    return (path, file_name, cropped)

def crop_words_on_line(y_line_df, line_idx, orig):
    sorted_line_df = y_line_df.sort_values(by=['x1'])

    points_on_line = []
    (xmin, xmax, ymin) = (0, 0, 0)

    for i, row in sorted_line_df.iterrows():
        (x, y) = (row["x1"], row["y1"])

        if (xmin == 0):
            (xmin, xmax, ymin) = (x, x, y)
        elif (x > xmax):
            if (abs(xmax - x) < 100):
                xmax = x
            else:
                points_on_line.append((xmin, xmax, ymin))
                xmin = x
                xmax = x
                ymin = y
    points_on_line.append((xmin, xmax, ymin))

    return [get_cropped_word((line_idx, idx), points, orig) for idx, points in enumerate(points_on_line)]

def get_words_on_photo(path, file_id): 
    testImagePath = path

    orig = cv2.imread(testImagePath)
    gray = cv2.imread(testImagePath)

    #lower_blue = np.array([100,10,10])
    #upper_blue = np.array([150,255,255])
    lower_blue = np.array([90,0,0])
    upper_blue = np.array([170,255,255])
    hsv = cv2.cvtColor(gray, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    cv2.imwrite('mask.jpg',mask)

    print('mask of the photo created')

    blue_hough_lines = cv2.HoughLinesP(cv2.Canny(mask,50,150), 1, np.pi/180, 0, maxLineGap=150)

    a,b,c = blue_hough_lines.shape

    # collect hough lines under word to df
    df = pd.DataFrame(columns=['x1','y1','x2','y2'])
    for i in range(a):
        df.loc[i] = [
            blue_hough_lines[i][0][0],
            blue_hough_lines[i][0][1],
            blue_hough_lines[i][0][2],
            blue_hough_lines[i][0][3]
        ]

    # group lines by height
    y_arrange_values = np.arange(60, 3500, 40)
    sorted_df = df.sort_values(by=['y1', 'y2'])
    grouped_df = sorted_df.groupby([pd.cut(sorted_df["y1"], y_arrange_values)])

    words = []
    for idx, group in enumerate(grouped_df):
        key,item = group      
        cv2.line(gray, (0, key.left), (3000, key.right), (0,0,255), 3, cv2.LINE_AA)

        if item.empty or len(item) < 30:
            continue

        y_line_df = pd.DataFrame(columns=['x1','y1','x2','y2'])
        color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))

        # underline word with different colors
        for line_idx, line in enumerate(item.values):
            x1,y1,x2,y2 = line
            y_line_df.loc[line_idx] = [x1,y1,x2,y2]
            cv2.line(gray, (x1, y1), (x2, y2), color, 3, cv2.LINE_AA)
        
        # find words in y line by continuous x values
        cropped_files = crop_words_on_line(y_line_df, idx, orig)

        # write cropped words in files
        for (croppedFilePath, file_name, cropped) in cropped_files:
            cv2.imwrite(croppedFilePath, cropped)
            stat_info = os.stat(croppedFilePath);

            # recognize cropped words
            if (stat_info.st_size > 0):
                # debug cropped files
                s3_bucket.upload_file(croppedFilePath, file_id + file_name)

                word = pytesseract.image_to_string(cropped)
                print("pytesseract result for: ", croppedFilePath, " - ", word)
                words.append(re.sub(extra_symbols, "", word).strip())

    cv2.imwrite('houghlines5.jpg', gray)

    # debug source file
    s3_bucket.upload_file(path, 'file %s.png' % (file_id))
    s3_bucket.upload_file('./mask.jpg', 'mask %s.png' % (file_id))
    s3_bucket.upload_file('./houghlines5.jpg', 'houghlines5 %s.png' % (file_id))

    return words