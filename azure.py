""" Name: Bathala, Harikrishna
    ID: 1001415489
"""""

from pymongo import MongoClient
from flask import Flask, render_template,request
import io
import csv
import datetime

from azure.storage.blob import BlockBlobService
from azure.storage.blob import PublicAccess
from azure.storage.blob import ContentSettings


app=Flask(__name__)

block_blob_service = BlockBlobService(account_name='haristorage6', account_key='FJfgUXVVZhHBJNIBtjG+prdKI+6mfXPBvAUdHvRvVmtm3X0aD9t5HuMEUTQ1Xt3o93vreex9O5o6pxm6Jb7YeA==')
block_blob_service.create_container('mycontainer', public_access=PublicAccess.Container)
connection = MongoClient("mongodb://hari-nosql:x3FirtEAOz0FQdtDwswOC6ztz7WfoqKHqmkIRKydeFPcNeNFI1EgyeISqnDQto1Q6uuRs9KV9MaGf1prUy6qXg==@hari-nosql.documents.azure.com:10255/?ssl=true&replicaSet=globaldb")

db = connection.Cooking.Reciepe

reciepe = {}

@app.route("/", methods=["POST","GET"])
def start():
    return render_template("index.html")
@app.route("/uploadcsv", methods=["POST","GET"])
def uploadcsv():
    f=request.files['file']
    csv_name=f.filename
    csvnme=csv_name.split('.')
    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    print(stream)
    csv_input = csv.reader(stream)
    print(csv_input)

    generator = block_blob_service.list_blobs('mycontainer')

    for blob in generator:
        print(blob.name)
        if blob.name==csvnme[0]:
            obj1= block_blob_service.make_blob_url('mycontainer', blob.name, protocol='https')
            print(obj1)



    rowno=1
    for row in csv_input:
        if rowno==1:
            cal_list=row
            rowno=2
            continue
        elif rowno==2:
            ingred=row
            rowno=9
            continue
        else:
            state=row

    print(cal_list)
    print(ingred)
    print(state)
    reciepe = {"Author": "HARI"}
    i = 0
    j=0
    ingredient_list=''
    calories_list=''
    for ingredient in ingred:
        ingredient_list = ingredient_list+" "+ingred[i]
        i=i+1
    for cal in cal_list:
        calories_list=calories_list+" " +cal_list[j]
        j=j+1
    reciepe['ingredients']=ingredient_list
    reciepe['calories']=calories_list
    reciepe['url']=obj1
    reciepe['name']=csvnme[0]
    reciepe['status']=state[0]
    db.insert(reciepe)

    return render_template("index.html")

@app.route("/displayata", methods=["POST","GET"])
def displayata():
    before_up = datetime.datetime.utcnow()
    image_name=request.form['imgenme']

    res=db.find()
    img_url=[]
    img_ingred=[]
    img_cal=[]
    img_status=[]
    img_name=[]
    i=0
    for rec in res :
        if image_name in rec['ingredients'] and i<5:
            img_url.append(rec['url'])
            img_ingred.append(rec['ingredients'])
            img_cal.append(rec['calories'])
            img_status.append(rec['status'])
            img_name.append(rec['name'])
            i=i+1

    after_query_time_memcacahe = datetime.datetime.utcnow()
    differrnce1 = str(after_query_time_memcacahe - before_up)
    return render_template("index.html",differrnce1=differrnce1,imgg=zip(img_url,img_name))
    # return render_template("index.html",differrnce1=differrnce1,imgg=zip(img_url,img_name),img_ingred=img_ingred,img_cal=img_cal,img_status=img_status,img_name=img_name)


@app.route('/uploadimg', methods=['POST'])
def uploadimg():
        f= request.files['file']
        file_name=f.filename
        img_name=file_name.split('.')
        f.save('C:\\Users\\harik\\Desktop\\aws projects\\azure\\'+file_name)
        location ='C:\\Users\\harik\\Desktop\\aws projects\\azure\\'+file_name
        block_blob_service.create_blob_from_path('mycontainer',img_name[0],location,content_settings=ContentSettings(content_type='image/jpg'))
        return render_template("index.html")

@app.route('/min', methods=['POST'])
def min():
    before_up = datetime.datetime.utcnow()

    min_range=int(request.form['minrange'])
    print(min_range)
    res=db.find()
    img_url=[]
    img_name=[]
    for rec in res:
        weights=rec['calories']
        weights_list=weights.split()
        for wt in weights_list:
            int_wt=int(wt)
            print(int_wt)
            if int_wt < min_range :
                img_url.append(rec['url'])
                img_name.append(rec['name'])
    after_query_time_memcacahe = datetime.datetime.utcnow()
    differrnce1 = str(after_query_time_memcacahe - before_up)

    return render_template("index.html",imgg=zip(img_url,img_name),differrnce1=differrnce1)

connection.close()


if __name__=='__main__':
    # app.run(host='0.0.0.0', port=int(8080), threaded=True, debug=True)
    app.run(debug=True)
