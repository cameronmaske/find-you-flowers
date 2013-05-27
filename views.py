from flask import render_template
from restful import jsonify
from collections import Counter
import pickle
import re
import string

from app import app, mongo, redis
from decorator import cached

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/all/')
def all():
    results = list(mongo.db.flower.find())
    return jsonify(**{'results': results})


@app.route('/suggested/')
@cached()
def suggested():
    word_list = []
    flowers = list(mongo.db.flower.find())
    exclude = set(string.punctuation)
    for flower in flowers:
        s = flower['name']
        word_list += ''.join(ch for ch in s if ch not in exclude).split(' ')

    f = open("stop-words.txt", "r")
    stopwords = f.read().split('\n')
    filtered_words = [w.lower() for w in word_list if not w.lower() in stopwords]
    counter = Counter(filtered_words).most_common(200)
    most_common = [c[0] for c in counter]
    return jsonify(**{'results': most_common})

@app.route('/search/<query>')
def search(query):
    query_re = re.compile(query)

    cache = redis.get(query)
    if cache:
        results = pickle.loads(cache)
    else:
        results = list(mongo.db.flower.find(
            {"$or": [
                {"name": query_re},
                {"description": query_re}]}))
        redis.setex(query, (60*60*5), pickle.dumps(results))
    print "Redis: {} Memory".format(redis.info()['used_memory_human'])
    return jsonify(**{'results': results})
