# import glib
import nltk
import sys 
from BeautifulSoup import BeautifulSoup, SoupStrainer
import re
import urllib2
#import requests
from HTMLParser import HTMLParser 
from re import sub 
from sys import stderr 
from traceback import print_exc
from urllib import urlopen

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ribbit_app.models import *
#from shouts.models import *

import json
from datetime import datetime
import sqlite3 as lite

#del 

@csrf_exempt
@require_POST
def new_shout(request):
    # READ IN ALL THE BRANCH AND ADDRESS
    br=[]
    bradd=[]
    con = None
    con = lite.connect("C:/Users/fpan/PY-Programs/bookPasser/ribbit/ribbit/database.db")
    cur = con.cursor()
    brcount=0
    br=range(100)
    bradd=range(100)
    for row in cur.execute("SELECT * FROM ribbit_app_branch"): 
        br[brcount] = row[1]
        bradd[brcount] = row[0]
        print brcount
        print br[brcount]
        print bradd[brcount]
        brcount=brcount+1    


    d=""
    dd=""
    lat = request.POST['lat']
    lng = request.POST['lng']
    author = request.POST['author']
    message = request.POST['message']
    keywords = request.POST['keywords']
    # keywords = keywords.lower()

    # START TO READ FROM BOOKPASSER, WRITE INTO SHOUT TABLE THE BOOK I CHECKED-IN
    count=0
    response = []
    chkincount=0
    chkin=range(15)
    chkinloc=range(15)
    Shout.objects.all().delete()
    for row in cur.execute("SELECT * FROM ribbit_app_bookpasser"):    
        if keywords == row[2]:
            chkin[chkincount] = row[2]
            chkinloc[chkincount] = row[3]
            print chkin[chkincount]
            print chkinloc[chkincount]          
            chkincount = chkincount + 1

    for s in range(chkincount):
        # r=r+1
        print chkin[s]
        print chkinloc[s]
        address = chkinloc[s]
        book = chkin[s]
        branchname = "fpan"
        count = count + 1
        shout = Shout.objects.create(lat=lat,lng=lng,author=author,message=message,book=book,address=address,branchname=branchname,count=count)

        response.append({
            'date_created': "", #shout.date_created.strftime("%b %d at %I:%M:%S%p"),
            'lat': "", #str(shout.lat),
            'lng': "", #str(shout.lng),
            'author': "", #author,
            'message': "", #message,
            'zipcode': "", #zip,
            'address': address, #address,
            'book': book, 
            'branchname': "",
            'count': count
        })

    # START TO READ FROM SHOUT TABLE
    # Shout.objects.all().delete()

    kw = keywords.replace(" ", "+")
    bkkw = keywords.replace(" ", "_")
    bkkw = "_" + bkkw
    # bkkw = "_" + bkkw + '" c'
    # print kw
    zip="10001"
    address = ""
    d=author
    dd=message
    a=0
    ddd = 'http://nypl.bibliocommons.com/search?t=title&q=' + kw + '&commit=Search&searchOpt=catalogue' 
    responser=get_url_content(ddd)
    # print responser
    bkkw=bkkw.lower()
    print bkkw
    for link in BeautifulSoup(responser, parseOnlyThese=SoupStrainer('a')):
        if link.has_key('href'):
            y = link['href']
            if bkkw in y:      
                print y
                bkcode = y[11:25]
                bkcode = 'http://nypl.bibliocommons.com/item/show_circulation/' + bkcode
                # print bkcode 
                responser=get_url_content(bkcode)
                clean_text = nltk.clean_html(responser)
                beg = clean_text.index("Available to borrow",1)
                end = clean_text.index("Not available at this time",beg)
                clean_text = clean_text[beg:end]
                # print clean_text
                for r in range(brcount):
                    # r=r+1
                    print br[r]
                    if br[r] in clean_text:
                        address = bradd[r]
                        book = keywords
                        branchname = br[r]
                        count = count + 1
                        print bradd[r]
                # print clean_text
                        shout = Shout.objects.create(lat=lat,lng=lng,author=author,message=message,book=book,address=address,branchname=branchname,count=count)

                        response.append({
                            'date_created': "", #shout.date_created.strftime("%b %d at %I:%M:%S%p"),
                            'lat': "", #str(shout.lat),
                            'lng': "", #str(shout.lng),
                            'author': "", #author,
                            'message': "", #message,
                            'zipcode': "", #zip,
                            'address': address, #address,
                            'book': book, 
                            'branchname': branchname,
                            'count': count
                        })

                break

    return HttpResponse(json.dumps(response))

def get_shouts(request):
    # keywords = request.POST['keywords']
    lat = float(request.GET['lat'])
    lng = float(request.GET['lng'])
    radius = float(request.GET['radius'])
    
    lat_low = str(lat - radius)
    lat_high = str(lat + radius)
    lng_low = str(lng - radius)
    lng_high = str(lng + radius)
    
    #shouts = Shout.objects.filter(lat__gte=lat_low,lat__lte=lat_high,lng__gte=lng_low,lng__lte=lng_high)[:10000]
    shouts = Shout.objects.filter(lat__gte=lat_low,lat__lte=lat_high,lng__gte=lng_low,lng__lte=lng_high)[:100]
    
    #zip="10001"

    response = []
    #for shout in shouts:
    for shout in shouts:
        response.append({
            'date_created': shout.date_created.strftime("%b %d at %I:%M:%S%p"),
            'lat': str(shout.lat),
            'lng': str(shout.lng),
            'author': shout.author,
            'message': shout.message,
            'zipcode': shout.zip,
            'address': shout.address,
            'count': shout.count,
            # 'address': shout.address, #address,
            'book': shout.book, 
            'branchname': shout.branchname            
        })
    # x=shout.book
    # print x

    
    return HttpResponse(json.dumps(response))

def get_url_content(site_url):
    rt=""
    try:
        request = urllib2.Request(site_url) 
        f=urllib2.urlopen(request)
        content=f.read()
        f.close()
    except urllib2.HTTPError, error:
        content=str(error.read())
    return content

class _DeHTMLParser(HTMLParser): 
    def __init__(self): 
        HTMLParser.__init__(self) 
        self.__text = [] 
 
    def handle_data(self, data): 
        text = data.strip() 
        if len(text) > 0: 
            text = sub('[ \t\r\n]+', ' ', text) 
            self.__text.append(text + ' ') 
 
    def handle_starttag(self, tag, attrs): 
        if tag == 'p': 
            self.__text.append('\n\n') 
        elif tag == 'br': 
            self.__text.append('\n') 
 
    def handle_startendtag(self, tag, attrs): 
        if tag == 'br': 
            self.__text.append('\n\n') 
 
    def text(self): 
        return ''.join(self.__text).strip() 
 
def dehtml(text):
    try: 
        parser = _DeHTMLParser() 
        parser.feed(text) 
        parser.close() 
        return parser.text() 
    except: 
        print_exc(file=stderr) 
        return text    