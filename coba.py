#import library pandas, regex, dan sqlite
import pandas as pd
import re
import sqlite3

#import library untuk Flask
from flask import Flask,jsonify
from flask import request, make_response, url_for
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'csv'}

#definisikan deskripsi dari swagger UI
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title' :LazyString(lambda: 'API dokumentasi untuk data preprocessing'),
        'version' : LazyString(lambda: '1.0.0'),
        'description' : LazyString(lambda:'API Dokumentasi untuk Data Teks Preprocessing'),
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs":[
        {
          "endpoint": 'dok',
          "route": '/dok.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui":True,
    "specs_route":"/dok"
}

swagger = Swagger(app, template=swagger_template,
                  config = swagger_config)

#Mengkonekkan data ke database
conn = sqlite3.connect('data\contoh.db', check_same_thread=False)

#mendefinisikan dan mengexecute quey untuk table data 
#tabel data ke-1 akan berisi kolom teks kotor dan teks yang sudah di cleaning dengan tipe data varchar
conn.execute(''' CREATE TABLE IF NOT EXISTS data (text varchar(255), text_clean varchar(225));''')

#endpoint 1, bahwa data yang diambil akan dari file
@swag_from ("dok/clean_text.yml", methods=['POST'])
@app.route('/text_clean', methods=['POST'])

#mendifine route
def text_proses():
  #mendapat inputan
  text = request.form.get('text')
  #proses cleansing dengan regex (mengambil semua data kecuali huruf kecil dan besar)
  text_clean = re.sub(r'[^a-zA-Z]','',text)

  #mengisi inputan tabel dengan form yang sudah diisi dan melakukan eksekusi query
  conn.execute("INSERT INTO data(text, text_clean) VALUES ('"+text+"','"+text_clean+"');")
  conn.commit()

  #denfine API response
  json_response = {
      'status_code' : 200,
      'description' : "Teks Sudah Bersih",
      'data' : text_clean,
  }
  response_data = jsonify(json_response)
  return response_data

#mendefinisikan dan mengexecute quey untuk table data 
#tabel data ke-2 akan berisi kolom teks kotor dan teks yang sudah di cleaning dengan tipe data varchar
conn.execute(''' CREATE TABLE IF NOT EXISTS file (text varchar(255), text_clean varchar(225));''')

#endpoint 2, bahwa data yang diambil akan dari form yang diisi user
@swag_from ("dok/file_text.yml", methods=['POST'])
@app.route ('/file_clean', methods=['POST'])

#mendifine route  
def file_proses():
  if request.method == 'POST':
    #perintah mengupload file
    file = request.files['file']
    try:
      data = pd.read_csv(file, encoding='iso-8859-1')
    except:
      data = pd.read_csv(file, encoding='utf-8')
    (data)
    #proses cleansing dengan regex (mengambil semua data kecuali huruf kecil dan besar)
    file_clean = re.sub(r'[^a-zA-Z]',' ', str(data))
    #mengisi inputan tabel dengan form yang sudah diisi dan melakukan eksekusi query
    conn.execute("INSERT INTO file (text, text_clean) VALUES ('"+str(data)+"','"+file_clean+"');")
    conn.commit()

    #denfine API response
    json_response = {
      'status_code' : 200,
      'description' : "File Teks Sudah Bersih",
      'data' : file_clean,
    }
    response_data = jsonify(json_response)
    return response_data

if __name__ == '__main__':
  app.run()
  