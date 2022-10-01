from flask import Flask,redirect,url_for,render_template,request,flash
import mysql.connector
import mysql
from werkzeug.utils import secure_filename
import os
from flask_paginate import Pagination,get_page_args

app = Flask(__name__,static_folder="G:/University/الفصل الاخير/flask/templates/")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db = mysql.connector.connect(user='web', password='qwe@123', database='cloud')


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/onecolumn")
def onecolumn():
    return render_template("onecolumn.html")

@app.route("/twocolumn1")
def twocolumn1():
    return render_template("twocolumn1.html",image_path='/templates/3322919-200.png')

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
    pagination_keys = get_keys(keys = keys,offset=offset,per_page=per_page)

    pagination =Pagination(page=page,per_page=per_page,total=keys_len,css_framework='foundation')
    return render_template("twocolumn2.html",keys=pagination_keys, page=page,
                             per_page=per_page,pagination=pagination)

@app.route("/threecolumn")
def threecolumn():
    return render_template("threecolumn.html")

@app.route('/post_key_image', methods =["POST"])
def post_key_image():
    cursor = db.cursor()
    image_key = request.form.get("Key")
    image = request.files.get('filename')
    image_value = secure_filename(image.filename)
    image.save(os.path.join(f"{os.getcwd()}\\templates", image_value))
    try:
        cursor.execute('INSERT INTO key_image (image_key,image_value) VALUES (%s,%s)',
                        (image_key,image_value,))
    except mysql.connector.errors.IntegrityError:
        cursor.execute('UPDATE key_image SET image_value = %s WHERE image_key= %s',
                        (image_value,image_key,))
    db.commit()
    cursor.close()
    flash('image added successfuly !')
    return render_template("index.html")

@app.route('/get_image', methods =["POST"])
def get_image():
    image_key = request.form.get("Key")
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM key_image WHERE image_key = %s', (image_key,))
    image_path= cursor.fetchall()
    cursor.close()
    if image_path:
        flash(f'image for key {image_key}')
        return render_template("twocolumn1.html",image_path=f'/templates/{image_path[0][1]}')
    else:
        flash('key doesn\'t exist !!')
        return render_template("twocolumn1.html",image_path='/templates/3322919-200.png')

@app.route('/delete_key', methods =["POST"])
def delete_key():
    key = request.form.get('key_to_delete')
    cursor = db.cursor()
    cursor.execute(f'DELETE FROM key_image WHERE image_key=%s',(key,))
    db.commit()
    cursor.close()
    flash(f'key "{key}" and its image deleted successfuly !')
    return redirect(url_for('twocolumn2'))



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
        total_size INT,
        miss_rate INT,
        hit_rate INT,
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
    
    db.commit()
    cursor.close()
    app.run(debug=True)