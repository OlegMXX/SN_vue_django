# -*- coding: utf-8 -*-

import django
import os
import sys

from collections import Counter

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wey_backend.settings")
django.setup()

from post.models import Post, Trend


def extract_hashtags(text):
    hashtag_list = []

    for word in text.split():
        if word[0] == '#':
            hashtag_list.append(word[1:])

    if hashtag_list:
        return hashtag_list
    else:
        return None


def collect_hashtags(posts):
    trends = []
    for post in posts:
        trends_per_post = extract_hashtags(post.body)
        if trends_per_post:
            for hashtag in trends_per_post:
                trends.append(hashtag)
    return trends


# delete old trends:
for trend in Trend.objects.all():
    trend.delete()

posts = Post.objects.all()
trends = collect_hashtags(posts)

trends_counter = Counter(trends).most_common(10)

for trend in trends_counter:
    Trend.objects.create(hashtag=trend[0], occurrences=trend[1])