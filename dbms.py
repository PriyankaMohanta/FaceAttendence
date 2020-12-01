# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 15:52:30 2020

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
from datetime import timedelta,datetime

model = VGGFace(model='resnet50',
                include_top=False,
                input_shape=(224,224,3),pooling='avg')

face_data="haarcascade_frontalface_alt.xml"

cascade=cv2.CascadeClassifier(face_data)

URL="http://25.66.223.134:8080/shot.jpg"

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


class Student:
    
    def preprocess(self,img):
        """helper function to preprocess image"""
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        img = cv2.resize(img,(224,224))
        img = img.reshape(1,224,224,3)
        img = asarray(img,np.float32)
        img = preprocess_input(img,version=2)
        return img        
    

    
    def register(self,URL,Sid,Sname,SclassId,SphoneNo,Spassword):
        
        while True:
            imgreshp=urllib.request.urlopen(URL)
            imgarray=np.array(bytearray(imgreshp.read()),dtype=np.uint8)
    
            img=cv2.imdecode(imgarray,-1)
    
            img=cv2.resize(img,(800,500))
    
            faces=cascade.detectMultiScale(img)
    
            
            for x,y,w,h in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),
                              (0,0,255),2)
                cv2.putText(img,'press q to capture',(10,470),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
                face_img = img[y:y+h,x:x+w]
            cv2.imshow('cam',img)
            
            if cv2.waitKey(1)==ord('q'):
                break
        cv2.destroyAllWindows()
        
        emb = model.predict(self.preprocess(face_img))
        
        curr=sql.connect("attendenceSym.db",detect_types=sql.PARSE_DECLTYPES)
        query="""INSERT INTO student_details(Sid,Sname,
                                            SclassId,
                                            SphoneNo,
                                            Spassword) values(?,?,?,?,?)"""
        curr.execute(query,(Sid,Sname,SclassId,SphoneNo,Spassword))
        
        query = """INSERT INTO student_face_data(Sid,arr) VALUES(?,?)"""
        
        curr.execute(query,(Sid,emb))
        
        
        curr.commit()
        curr.close()  


    def fetch_student_attendance(self,Sid,StartDate,EndDate):
        curr=sql.connect("attendenceSym.db",detect_types=sql.PARSE_DECLTYPES)
        query="""SELECT Sname FROM student_details WHERE Sid=?"""
        
        ret=curr.execute(query,(Sid,))
        ret=ret.fetchall()
        
        if len(ret)>0:
            atten={"Roll":[Sid],"Name":[ret[0][0]]}
            
        daterange=[]
        
        Start=datetime.strptime(StartDate,"%d-%m-%y")
        End=datetime.strptime(EndDate,"%d-%m-%y")
        Step=timedelta(days=1)
        
        while Start<=End:
            daterange.append(Start.strftime("%d-%m-%y"))
            Start=Start+Step
        
        for i in daterange:
            query="""SELECT Sid FROM student_attandance WHERE date=?"""
            
            ret=curr.execute(query,(i,))
            ret=ret.fetchall()
            
            ret=[x[0] for x in ret]
            
            if Sid in ret:
                atten.update({i:["P"]})
            else:
                atten.update({i:["A"]})
                
        curr.close()
        return atten



class Employee:
    
    def register_faculty(self,Eid,Ename,Ephone,Epassword,Etype):
        
        con = sql.connect('attendence_sys.db',detect_types=sql.PARSE_DECLTYPES)

        query = """INSERT INTO employee_details(Eid,
                                                Ename,
                                                Ephone,
                                                Epassword,
                                                Etype) VALUES (?,?,?,?,?)"""
        con.execute(query,(Eid,Ename,Ephone,Epassword,Etype))
        con.commit()
        con.close()
        
    def fetch_faculty(self,Ephone,Epassword):
        con = sql.connect('attendence_sys.db',detect_types=sql.PARSE_DECLTYPES)

        query = """SELECT * FROM employee_details WHERE Ephone=? AND Epassword=?"""
        ret = con.execute(query,(Ephone,Epassword))
        ret = ret.fetchall()
        if len(ret)>0:
            return {'Eid':ret[0][0],'Ename':ret[0][1],'Enumber':ret[0][2],'Etype':ret[0][4]}
        else:
            return False
        con.close()













