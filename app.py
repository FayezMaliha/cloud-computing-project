from math import e
from flask import Flask,redirect,url_for,render_template,request,flash
from flask_paginate import Pagination,get_page_args
from werkzeug.utils import secure_filename
import mysql.connector
import mysql
import os
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from cache.image_cache import ImageCache
from PIL import Image
import base64
import io

app = Flask(__name__,static_url_path = "/static",static_folder = "static")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app_dir = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(app_dir, 'static/uploads')

db = mysql.connector.connect(user='web', password='qwe@123', database='cloud')
cache = ImageCache()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/onecolumn")
def onecolumn():
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM cache_configuration')
    config = cursor.fetchall()
    cursor.close()
    policy = 0
    capacity = 2
    if(config is not None and len(config) != 0):
        capacity = config[0][0]
        policy = config[0][1]
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM policy_type WHERE id = {policy}')
    policy = cursor.fetchall()[0][1]
    cursor.close()
    return render_template("onecolumn.html", policy = policy, capacity = capacity)

@app.route("/twocolumn1")
def twocolumn1():
    im = Image.open('static/images/notfound.png')
    im =im.convert('RGB')
    data = io.BytesIO()
    im.save(data, "JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())
    return render_template("twocolumn1.html",image_value=encoded_img_data.decode('utf-8'))

def get_keys(keys,offset=0,per_page=10):
    return keys[offset:offset+per_page]

@app.route("/twocolumn2")
def twocolumn2():
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM key_image')
    keys = cursor.fetchall()
    cursor.close()
    page,per_page,offset = get_page_args(page_parameter="page",per_page_parameter="per_page")

    keys_len = len(keys)
    pagination_keys = get_keys(keys = keys,offset=offset, per_page=per_page)

    pagination = Pagination(page=page,per_page=per_page,total=keys_len,css_framework='foundation')
    return render_template("twocolumn2.html",keys=pagination_keys, page=page,
                             per_page=per_page,pagination=pagination)

@app.route("/threecolumn")
def threecolumn():
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM cache ORDER BY created_at DESC LIMIT 1')
    stats= cursor.fetchall()
    cursor.close()
    items = cache.count()
    requsts = cache.requsts
    size = cache.sizeMB()
    miss_rate = cache.missRate()
    hit_rate = cache.hitRate()
    stats = None
    if(stats != None and len(stats) != 0):
        items = stats[0][1]
        requsts = stats[0][2]
        size = stats[0][3]
        miss_rate = stats[0][4]
        hit_rate = stats[0][5]
    return render_template("threecolumn.html", items=items, requsts=requsts, size=size, miss_rate=miss_rate, hit_rate=hit_rate)

@app.route('/put', methods =["POST"])
def put():
    cursor = db.cursor()
    image_key = request.form.get("Key")
    image = request.files.get('filename')
    image_value = secure_filename(image.filename)
    image.save(os.path.join(f"{os.getcwd()}\\static\\uploads", image_value))
    try:
        cursor.execute('INSERT INTO key_image (image_key,image_value) VALUES (%s,%s)',
                        (image_key,image_value,))
    except mysql.connector.errors.IntegrityError:
        cursor.execute('UPDATE key_image SET image_value = %s WHERE image_key= %s',
                        (image_value,image_key,))
    db.commit()
    cursor.close()
    im = Image.open(f"static/uploads/{image.filename}")
    im =im.convert('RGB')
    data = io.BytesIO()
    im.save(data, "JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())
    cache.put(key= image_key, image= encoded_img_data)
    flash('image added successfuly !')
    return render_template("index.html")

@app.route('/get', methods =["POST"])
def get():
    image_key = request.form.get("Key")
    cacheResult = cache.get(image_key)
    if(cacheResult != None):
        flash(f'image for key {image_key}')
        return render_template("twocolumn1.html",image_value= cacheResult.decode('utf-8'))
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM key_image WHERE image_key = %s', (image_key,))
    image_p= cursor.fetchall()
    cursor.close()
    if image_p:
        im = Image.open(os.path.join('static/uploads',image_p[0][1]))
        im =im.convert('RGB')
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue())
        cache.put(key= image_key, image= encoded_img_data)
        flash(f'image for key {image_key}')
        return render_template("twocolumn1.html",image_value= encoded_img_data.decode('utf-8'))
    else:
        flash('key doesn\'t exist !!')
        im = Image.open('static/images/notfound.png')
        im =im.convert('RGB')
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue())
        return render_template("twocolumn1.html",image_value= encoded_img_data.decode('utf-8')) , 404

@app.route('/delete_key', methods =["POST"])
def delete_key():
    key = request.form.get('key_to_delete')
    if cache.get(key):
        cache.drop(key)
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM key_image WHERE image_key=%s',(key,))
    db.commit()
    cursor.close()
    flash(f'key "{key}" and its image deleted successfuly !')
    return redirect(url_for('twocolumn2'))


def storeStats():
    cursor = db.cursor()
    cursor.execute(f''' INSERT INTO cache (no_of_items, no_of_req_served, total_size, miss_rate, hit_rate) VALUES (%s, %s, %s, %s, %s) ''',
    (cache.count(), cache.requsts , cache.sizeMB(), cache.missRate(), cache.hitRate()))
    db.commit()
    cursor.close()


@app.route('/clear', methods =["POST"])
def clear():
    cache.clear()
    # storeStats()
    return redirect(url_for('onecolumn'))

@app.route('/change_policy', methods =["POST"])
def change_policy():
    cache.updateLru()
    cursor = db.cursor()
    if cache.lru:
        cursor.execute('UPDATE cache_configuration SET policy_type_id = %s',
                        (0,))
    else:
        cursor.execute('UPDATE cache_configuration SET policy_type_id = %s',
                        (1,))
    db.commit()
    cursor.close()
    return redirect(url_for('onecolumn'))


@app.route('/change_capacity', methods =["POST"])
def change_capacity():
    new_size = request.form.get("new_size")
    cache.updateMaxSizeMB(int(new_size))
    cursor = db.cursor()
    cursor.execute('UPDATE cache_configuration SET capacity = %s',
                    (new_size,))

    db.commit()
    cursor.close()
    return redirect(url_for('onecolumn'))

if __name__ == "__main__":
    cursor = db.cursor()
    cursor.execute(''' CREATE TABLE IF NOT EXISTS key_image(
        image_key VARCHAR(255) PRIMARY KEY,
        image_value VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )''')
    cursor.execute(''' CREATE TABLE IF NOT EXISTS cache(
        id INT AUTO_INCREMENT PRIMARY KEY,
        no_of_items INT,
        no_of_req_served INT,
        total_size FLOAT,
        miss_rate FLOAT,
        hit_rate FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute(''' CREATE TABLE IF NOT EXISTS policy_type(
        id INT PRIMARY KEY,
        type VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute(''' CREATE TABLE IF NOT EXISTS cache_configuration(
        capacity INT,
        policy_type_id INT,
        FOREIGN KEY (policy_type_id) REFERENCES policy_type(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    cursor.execute(''' INSERT IGNORE INTO policy_type (id, type) VALUES (0, 'Least Recently Used') ''')
    cursor.execute(''' INSERT IGNORE INTO policy_type (id ,type) VALUES (1, 'Random') ''')
    cursor.execute(f'SELECT * FROM cache_configuration')
    config= cursor.fetchall()
    if(len(config) == 0):
        cursor.execute(''' INSERT IGNORE INTO cache_configuration (capacity, policy_type_id) VALUES (2, 0) ''')
    db.commit()
    cursor.close()

    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM cache_configuration')
    config = cursor.fetchall()
    cursor.close()
    cache.updateMaxSizeMB(int(config[0][0]))
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=storeStats, trigger="interval", seconds=60*10)
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())
    app.run(debug=True)
