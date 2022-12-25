# encode: utf-8
from flask import g, Flask, render_template, request, send_file, redirect, session, jsonify
import os
import re
import sqlite3
import re
import re
import urllib.request
import json

from apscheduler.schedulers.background import BackgroundScheduler
# from pyyoutube import Api

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from py_youtube import Search

app = Flask(__name__)

DATABASE = './database.db'
SCHEDULER_TIMEOUT_MIN=30

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        sSQL = """
DROP TABLE IF EXISTS youtube_search_words;
CREATE TABLE youtube_search_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

DROP TABLE IF EXISTS youtube_found;
CREATE TABLE youtube_found (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    youtube_search_words_id INTEGER NULL,
    youtube_id TEXT NOT NULL,
    url TEXT NULL
);

DROP TABLE IF EXISTS update_queue;
CREATE TABLE update_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at INTEGER NULL,
    started_at INTEGER NULL,
    stopped_at INTEGER NULL,
    update_status INTEGER NULL,
    youtube_search_words_id INTEGER NULL
);

        """
        # with app.open_resource('schema.sql', mode='r') as f:
        #    db.cursor().executescript(f.read())
        db.cursor().executescript(sSQL)
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def fnUpdateQueue():
    with app.app_context():
        aQueue = query_db('SELECT * FROM update_queue WHERE update_status=0')

        if (len(aQueue) == 0):
            print(len(aQueue))
            get_db().execute("UPDATE update_queue SET update_status=0")
            get_db().commit()
        else:
            for oQueueItem in aQueue:
                aRows = query_db('SELECT * FROM youtube_search_words WHERE id = ?', (oQueueItem[5],))
                get_db().execute("DELETE FROM youtube_found WHERE youtube_search_words_id = ?", (aRows[0][0],))
                get_db().commit()

                keywords = aRows[0][1]
                keywords = urllib.request.quote(keywords)

                search_keyword=keywords # .replace(" ", "+")
                html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_keyword)
                limit = 12
                source = html.read().decode('utf8')
                data  = re.findall('{\"videoRenderer\":{\"videoId\":\"(\S{11})\",\"thumbnail\":{\"thumbnails\":\[{\"url\":\"(\S+)\",\"width\":360,\"height\":202},{\"url\":\"(\S+)\",\"width\":720,\"height\":404}\]},\"title\":{\"runs\":\[{\"text\":\"(.+?)\"}\],\"accessibility\":{\"accessibilityData\":{\"label\":\"(.+?)\"}}},\"longBylineText\"',source)[:limit]
                data_ = []
                for i in data:
                        js_data = {"id":"",
                                        "title":"", 
                                        "thumb" : "" ,
                                        "simple_data":""}
                        js_data['id'] = i[0]
                        js_data['title'] = i[3]
                        js_data['thumb'] = i[1],i[2]
                        js_data['simple_data'] = i[4]
                        data_.append(js_data)
                value = json.dumps(data_ )
                videos = json.loads(value)

                for oI in videos:
                    print(oI)
                    get_db().execute("INSERT INTO youtube_found (youtube_search_words_id, youtube_id) VALUES (?, ?)", (aRows[0][0], oI['id']))
                    get_db().commit()
                
                get_db().execute("UPDATE update_queue SET youtube_search_words_id=?, update_status=1", (aRows[0][0],))
                get_db().commit()

sched = BackgroundScheduler(daemon=True)
sched.add_job(fnUpdateQueue,'interval',minutes=SCHEDULER_TIMEOUT_MIN)
sched.start()

@app.route("/queue", methods=['GET', 'POST'])
def queue():
    aQueue = query_db('SELECT * FROM update_queue')

    return render_template('queue.html',
        aQueue=aQueue,
    )

@app.route("/", methods=['GET', 'POST'])
def index():
    if (not os.path.isfile(DATABASE)):
        print("=========================================================")
        print("INIT DB")
        init_db()
        print("=========================================================")
        return redirect("/")

    sBaseURL = request.url

    if "filter-word" in request.args:
        request.args["word"]
    if "add-word" in request.args:
        cur = get_db().cursor()
        cur.execute("INSERT INTO youtube_search_words (name) VALUES (?)", (request.args["word"],))
        sID = cur.lastrowid
        cur.execute("INSERT INTO update_queue (youtube_search_words_id, update_status) VALUES (?, 0)", (sID,))
        get_db().commit()
        fnUpdateQueue()
        redirect("/")
    if "remove-word" in request.args:
        aWords = request.args.getlist("words[]")
        for sWord in aWords:
            aRows = query_db('SELECT * FROM youtube_search_words WHERE name = ?', (sWord,))
            sID = aRows[0][0]
            get_db().execute("DELETE FROM update_queue WHERE youtube_search_words_id = ?", (sID,))
            get_db().execute("DELETE FROM youtube_search_words WHERE name = ?", (sWord,))
        get_db().commit()
        redirect("/")
    if "update-all-word" in request.args:
        get_db().execute("UPDATE update_queue SET update_status=0")
        get_db().commit()
        fnUpdateQueue()
        redirect("/")

    aSearchWords = query_db('SELECT * FROM youtube_search_words')

    dYoutubeWordsLinks = {}
    for oWord in aSearchWords:
        aYoutubeWords = query_db('SELECT * FROM youtube_found WHERE youtube_search_words_id=?', (oWord[0],))
        dYoutubeWordsLinks[oWord[1]] = aYoutubeWords

    # for i in range(1,100):
    #     dYoutubeWordsLinks[f"Тестовое слово {i}"] = [
    #         (1, 1, "VxYsYreHeLs", "https://www.youtube.com/watch?v=VxYsYreHeLs"),
    #         (2, 1, "VxYsYreHeLs", "https://www.youtube.com/watch?v=VxYsYreHeLs"),
    #         (3, 1, "VxYsYreHeLs", "https://www.youtube.com/watch?v=VxYsYreHeLs"),
    #         (4, 1, "VxYsYreHeLs", "https://www.youtube.com/watch?v=VxYsYreHeLs"),
    #         (5, 1, "VxYsYreHeLs", "https://www.youtube.com/watch?v=VxYsYreHeLs"),
    #         (6, 1, "VxYsYreHeLs", "https://www.youtube.com/watch?v=VxYsYreHeLs"),
    #         (7, 1, "VxYsYreHeLs", "https://www.youtube.com/watch?v=VxYsYreHeLs"),
    #         (8, 1, "VxYsYreHeLs", "https://www.youtube.com/watch?v=VxYsYreHeLs"),
    #     ]
    
    return render_template('index.html',
        sBaseURL=sBaseURL,
        dYoutubeWordsLinks=dYoutubeWordsLinks
    )

