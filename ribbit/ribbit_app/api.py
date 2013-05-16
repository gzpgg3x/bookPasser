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
    br=[]
    bradd=[]
    con = None
    con = lite.connect("C:/Users/fpan/PY-Programs/publishing/bookieGoer/bookieGoer/db.db")
    cur = con.cursor()
    brcount=0
    br=range(100)
    bradd=range(100)
    for row in cur.execute("SELECT * FROM discover_branch"): #order by visit_count DESC"):   
        br[brcount] = row[1]
        bradd[brcount] = row[2]
        print brcount
        print br[brcount]
        print bradd[brcount]
        brcount=brcount+1    
    # print br[10]
    # print bradd[10]
    Shout.objects.all().delete()
    d=""
    dd=""
    lat = request.POST['lat']
    lng = request.POST['lng']
    author = request.POST['author']
    message = request.POST['message']
    keywords = request.POST['keywords']
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
    count=0
    response = []
    # ddd = 'http://searchwww.sec.gov/EDGARFSClient/jsp/EDGAR_MainAccess.jsp?search_text='+keywords+'&sort=Date&formType=Form8K&isAdv=true&stemming=true&numResults=100&fromDate=' + d + '&toDate=' + dd + '&numResults=100' 
    ddd = 'http://nypl.bibliocommons.com/search?t=title&q=' + kw + '&commit=Search&searchOpt=catalogue' 
    responser=get_url_content(ddd)
    # responser='# encoding: utf-8' + responser
    # print bkkw
    # bkind = responser.find("html")
    # bkind = responser.find(bkkw)
    # print bkind
    for link in BeautifulSoup(responser, parseOnlyThese=SoupStrainer('a')):
        if link.has_key('href'):
            y = link['href']
            if bkkw in y:      
                print y
                bkcode = y[11:25]

                bkcode = 'http://nypl.bibliocommons.com/item/show_circulation/' + bkcode
                # print bkcode 
                responser=get_url_content(bkcode)
                # beg = responser.index("Available to borrow",1)
                # end = responser.index("Available to borrow",beg)
                # responser = responser[beg:end]
                clean_text = nltk.clean_html(responser)
                beg = clean_text.index("Available to borrow",1)
                end = clean_text.index("Not available at this time",beg)
                clean_text = clean_text[beg:end]
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



    # xLast=""
    # zz=""
    # x=" "
    # e=0
    # for link in BeautifulSoup(responser, parseOnlyThese=SoupStrainer('a')):
    #     if link.has_key('href'):
    #         y = link['href']
    #         if 'javascript:opennew(' in y: # and xLast is not x:
    #             b = y.index("'",21)
    #             z = y[20:b]
    #             c = y.index("'", b+4)
    #             x = y[b+3:c]
    #             if not (xLast == x):# and zz is z[1:45]:
    #                 text = get_url_content(z)
    #                 zzz=dehtml(text)
    #                 xx=x[0:40]                
    #                 try:
    #                     e = zzz.index(kw ,1) #zzz.index("Item 5.02",1)
    #                 except:
    #                     e = 1
    #                 newzzz = zzz[e:e+250]
    #                 zz=z[1:45]
    #                 xLast=x
    #                 author=xx
    #                 message=z
    #                 cikidxbeg = y.index("http://www.sec.gov/Archives/edgar/data/",1) + 40
    #                 cikidxend = y.index("/", cikidxbeg)
    #                 cik = y[cikidxbeg-1:cikidxend]
    #                 cikText = get_url_content('http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=' + cik)
    #                 mailerLocA = cikText.index("<div class=\"mailer\">",1)
    #                 mailerLocB = cikText.index("<div class=\"mailer\">", mailerLocA + 20)
    #                 mailerText = cikText[mailerLocA:mailerLocB + 20]
    #                 address = dehtml(mailerText)
    #                 postal_code = re.match('^.*?(\d+)$', address)
    #                 if postal_code!=None:
    #                     zip = address[-5:len(address)]

    #                     if zip[-5:-4] == "-":
    #                         zip = address[-10:-6]

    #                     if zip >= "07000" and zip <="09000":
    #                         a = a + 1
    #                         address = address[16:len(address)]
    #                         shout = Shout.objects.create(lat=lat,lng=lng,author=author,message=message)

    #                         response.append({
    #                             'date_created': shout.date_created.strftime("%b %d at %I:%M:%S%p"),
    #                             'lat': str(shout.lat),
    #                             'lng': str(shout.lng),
    #                             'author': author,
    #                             'message': message,
    #                             'zipcode': zip,
    #                             'address': address,
    #                             'count': a
    #                         })

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
            'address': shout.address, #address,
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