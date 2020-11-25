# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 14:51:11 2020

@author: cttc
"""
import sqlite3 as sql
import io
import numpy as np


conn=sql.connect("attendenceSym.db")
conn.close()

"""
student details table creation

"""
con=sql.connect("attendenceSym.db")
query="""CREATE TABLE student_details(Sid TEXT PRIMARY KEY,Sname TEXT,
                                      SclassId TEXT,SphoneNo INTEGER,
                                      Spassword TEXT)"""

con.execute(query)
con.commit()
con.close()

"""
configuring database to store arrays
"""
def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

# Converts np.array to TEXT when inserting
sql.register_adapter(np.ndarray, adapt_array)

# Converts TEXT to np.array when selecting
sql.register_converter("array", convert_array)

"""
creatingf student face data table
"""

con=sql.connect("attendenceSym.db",detect_types=sql.PARSE_DECLTYPES)
query="""CREATE TABLE student_face_data(Sid TEXT,arr array,
                                        FOREIGN KEY (Sid) 
                                        REFERENCES student_details(Sid)
                                        ON DELETE CASCADE
                                        ON UPDATE CASCADE)"""

con.execute(query)
con.commit()
con.close()

"""
student attandance
"""
con=sql.connect("attendenceSym.db",detect_types=sql.PARSE_DECLTYPES)
query="""CREATE TABLE student_attandance(Sid TEXT,
                                        date TEXT,
                                        attendance TEXT DEFAULT 'A',
                                        FOREIGN KEY (Sid)
                                        REFERENCES student_details(Sid)
                                        ON DELETE CASCADE
                                        ON UPDATE CASCADE)"""

con.execute(query)
con.commit()
con.close()









