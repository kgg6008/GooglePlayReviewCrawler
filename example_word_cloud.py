#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import pandas as pd
from PIL import Image
import numpy as np
from wordcloud import WordCloud
import platform
from matplotlib import font_manager, rc

mysql = pymysql.connect(host='localhost', port=3306, user='root',
                        passwd='1234', db='google_play_review', charset='utf8mb4')

review = pd.read_sql('select * from Conects', mysql)
get_topic = GetTopic(title_to_tag=True)
get_topic.fit_data(review['review_txt'])
review['keyword'] = review['review_txt'].apply(get_topic.get_tags)
temp = review[review['review_score'] == 5]
word_dict = {}
for word_ls in review['keyword']:
    for word in word_ls:
        try:
            word_dict[word] += 1
        except KeyError:
            word_dict[word] = 1
word_dict1 = {}
for word_ls in temp['keyword']:
    for word in word_ls:
        try:
            word_dict1[word] += 1
        except KeyError:
            word_dict1[word] = 1

word_dict5 = {}
for word_ls in temp['keyword']:
    for word in word_ls:
        try:
            word_dict5[word] += 1
        except KeyError:
            word_dict5[word] = 1

mask = np.array(Image.open('/Users/hh/Downloads/conects_logo.png'))

if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')

wc = WordCloud(font_path='/Library/Fonts/AppleGothic.ttf',
               relative_scaling=0.2,
               background_color='white',
               mask=mask,
               width=1000,
               height=1000
               ).generate_from_frequencies(word_dict)
wc.to_file('/Users/hh/Desktop/word_cloud.png')