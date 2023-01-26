# from flask import Flask,render_template, request
# from flask_mysqldb import MySQL
# import mysql.connector
# cnx = mysql.connector.connect(user='root', database='cloud')
# app = Flask(__name__)
 
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'flask'
# app.config['MYSQL_PORT'] = 3306
# curA = cnx.cursor()
# mysql = MySQL(app)

# curA.execute('SELECT * FROM key_image')

# print(len(curA.fetchall()))
# cnx.commit()
###################################################

from flask import Flask, render_template
from PIL import Image
import base64
import io
import os

im = Image.open("G:\\University\\الفصل الاخير\\flask\\static\\images\\pic2.jpg")
data = io.BytesIO()
im.save(data, "JPEG")
encoded_img_data = base64.b64encode(data.getvalue())

print(len(encoded_img_data)*3/4)




