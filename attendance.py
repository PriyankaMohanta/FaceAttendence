# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 15:16:44 2020

@author: cttc
"""

import sqlite3 as sql
import cv2
import numpy as np
from numpy import asarray
import io
import urllib
from keras_vggface import VGGFace
from keras_vggface.utils import preprocess_input
from datetime import date
from scipy.spatial.distance import cosine


URL="http://192.168.42.129:8080/shot.jpg"

def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sql.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

sql.register_adapter(np.ndarray, adapt_array)
sql.register_converter("array", convert_array)

model = VGGFace(model='resnet50',
                include_top=False,
                input_shape=(224,224,3),pooling='avg')

face_data="haarcascade_frontalface_alt.xml"

cascade=cv2.CascadeClassifier(face_data)


def preprocess(img):
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    img = img.reshape(1,224,224,3)
    img = asarray(img,np.float32)
    img = preprocess_input(img,version=2)
    return img 

conn=sql.connect("attendenceSym.db",detect_types=sql.PARSE_DECLTYPES)
query="""SELECT * FROM student_face_data """
ret=conn.execute(query)
ret=ret.fetchall()
conn.close()

while True:
    imgreshp=urllib.request.urlopen(URL)
    imgarray=np.array(bytearray(imgreshp.read()),dtype=np.uint8)
    
    frame=cv2.imdecode(imgarray,-1)
    
    faces=cascade.detectMultiScale(frame)
    
    for x,y,w,h in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
        cv2.putText(frame,'press q to capture',(10,470),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        face_img = frame[y:y+h,x:x+w]
        face_img=cv2.resize(face_img,(224,224))
        new_emb=model.predict(preprocess(face_img))
        
        for i in ret:
            if cosine(new_emb,i[1])<0.2:
                print(cosine(new_emb,i[1]))
                conn=sql.connect("attendenceSym.db",detect_types=sql.PARSE_DECLTYPES)
                query="""INSERT INTO student_attandance(Sid,date,attendance) VALUES(?,?,?)"""
                conn.execute(query,(i[0],date.today().strftime('%d_%m_%y'),"P"))
                conn.commit()
                conn.close()
                
    
    
    cv2.imshow('vedio',frame)
        
    if cv2.waitKey(1)==27:
        break

cv2.destroyAllWindows()

























