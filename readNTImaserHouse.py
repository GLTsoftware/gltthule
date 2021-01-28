#!/usr/bin/python3
import time
import redis
import datetime
import requests
from bs4 import BeautifulSoup


red = redis.StrictRedis(host='192.168.1.11',port=6379,db=0)
 
while True:
    f = open("dataNTIsensorMaserHouse.txt","a")
    ts = time.time()
    r = requests.get('http://192.168.1.69',auth=('root','nti'))
    soup = BeautifulSoup(r.text,'html.parser')
    is0=soup.find_all(id='is0')[0].get_text()
    is1=soup.find_all(id='is1')[0].get_text()
    is2=soup.find_all(id='is2')[0].get_text()
#    es0=soup.find_all(id='es0')[0].get_text()
#    es1=soup.find_all(id='es1')[0].get_text()
#    es2=soup.find_all(id='es2')[0].get_text()
#    st=datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    st=datetime.datetime.fromtimestamp(ts).strftime('%d %b %Y %H:%M:%S')
    print(st,ts)
    print("Internal sensors: temp=", is0,"humidity=",is1,"dew point=",is2)
#    print("External Sensor port 1: temp=",es0,"humidity=",es1,"dew point=",es2)
    buffer = "%s %s %s %s %s\n" % \
             (ts,st,is0,is1,is2)
#    buffer = "%s %s %s %s %s %s %s %s\n" % \
#             (ts,st,is0,is1,is2,es0,es1,es2)
    f.write(buffer)
    f.close()
    red.zadd('maserHouseWeather',ts,{"timestamp":ts,"temperature":is0,"humidity":is1,"dewPoint":is2,"datetime":st})
    time.sleep(60)
 #time.strftime("%b %d %Y %H:%M:%S", time.gmtime(t))
