import cookielib
import urllib
import urllib2
import xmlrpclib
import ConfigParser
from bs4 import BeautifulSoup
import csv
import re
#from datetime import date
import time
import threading
#import sys
import os.path
#import unicodedata as ud
import codecs
#from send_mail import send_mail


__author__ = 'Carlos Espinosa'

class Spider:
    def __init__(self):
        self.opener = None
        self.RETRY_COUNT = 5
        self.USER_AGENT = ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1')
        self.headers = [self.USER_AGENT]

    def fetchData(self, url, referer=None, parameters=None, retry=0):
        opener = urllib2.build_opener(urllib2.HTTPRedirectHandler())
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1')]
        cookieJar = cookielib.LWPCookieJar()
        handlers = urllib2.HTTPCookieProcessor(cookieJar)
        opener.add_handler(handlers)
#        try:
        urllib2.install_opener(opener)
        response = opener.open(url)
        return response.info(), response.read()
        self.REFERER = ('Referer', referer)
        if referer is not None:
            self.headers.append(self.REFERER)
        self.opener = self.createOpener(self.headers, [self.createCookieJarHandler()])
        urllib2.install_opener(self.opener)

        if parameters is None:
            response = self.opener.open(url, timeout=200)
            return response.info(), response.read()
        else:
            response = self.opener.open(url, urllib.urlencode(parameters), timeout=200)
            return response.info(), response.read()
#        except Exception, x:
#            
#            print x
#            if retry < self.RETRY_COUNT:
#                self.fetchData(url, referer, parameters, retry + 1)
#            else:
#                print 'Failed to fetch data after 5 retry.'+url
#                return None
#        return None
class Report(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name=''
        self.path=''
        self.numErrors=0
        self.numProcess=0
        self.numSucces=0
        self.writer=''
        self.header=["Date generated","SKU","MFR","Name","BH Type of Sell","BH Special Price","BH Price","BH Price Rebate","BH Date Rebate","EA Special Price","EA Price","EA Price Rebate","EA Date Rebate","Type of sell to upload","Special Price to Upload","Price To Upload","Rebate to Upload","Date Rebate to Upload"]
        config = ConfigParser.ConfigParser()
        config.read("config.ini")
        tip="magento_live"
        #tip="magestaging"
        self.credential={}
        self.credential['mg_url'] = config.get(tip, "mg_url")
        self.credential['mg_username'] = config.get(tip, "mg_username")
        self.credential['mg_password'] = config.get(tip, "mg_password") 
        self.server = xmlrpclib.ServerProxy(self.credential['mg_url'])
    def checkTMPFile(self):
        if os.path.isfile(".tmp_"+self.name):
            return True
        else:
            self.checkTMPFile()
            return False
    def addProcces(self):
        self.numProcess=self.numProcess+1
    def addSucces(self):
        self.numSucces=self.numSucces+1
    def addError(self):
        self.numErrors=self.numErrors+1    
    
    def createTMPFile(self):
        self.writer = csv.writer(open(".tmp_"+self.name, "wb"))
    
    def create(self,name,path=''):
        self.name=name
#        updateArchive=str(date.today())+"_updates.csv"
        self.writer = csv.writer(codecs.open(self.name, "wb", encoding="utf-8"))
        self.writer.writerow(self.header)
        self.getItemsByAttributSet()
    def addrow(self,data):
        self.writer.writerow(data)
        
        
    def getItemsByAttributSet(self):
        #112    4    SLR Lenses-MAP    0
        #115    4    Point & Shoot-MAP    0
        #116    4    SLR Cameras-MAP    0
        #119    4    Mirrorless System Cameras-MAP    0
        #123    4    Tripods-MAP    0
        #124    4    Bags-MAP    0
        #125    4    DJ Turntable-MAP    0
        #127    4    Support & Rigs-MAP    0
        #128    4    Tripod Heads-MAP    0
        #130    4    DJ Controllers-MAP    0
        #131    4    DJ Software-MAP    0
        #132    4    Lighting-MAP    0
        #133    4    Light-stands, Booms, & Mountings-MAP    0
        #134    4    Studio-MAP    0
        #135    4    DJ Lighting-MAP    0
        #136    4    DJ Stage Effects-MAP    0
        #137    4    DJ Speakers-MAP    0
        #138    4    DJ Microphones-MAP    0
        #139    4    Batteries & Power-MAP    0
        #140    4    Cables-MAP    0
        #141    4    Binoculars-MAP    0
        #142    4    Remote Controls-MAP    0
        #143    4    Underwater Accessories-MAP    0
        #145    4    Underwater Equipment-MAP    0
        #146    4    Micro Four Thirds Lens Accessories-MAP    0
        #147    4    DJ CD, MP3 & Media Players-MAP    0
        #148    4    DJ Mixers-MAP    0
        #149    4    DJ Headphones-MAP    0
        #150    4    Speakers-MAP    0
        #151    4    Headphones-MAP    0
        #152    4    Bluetooth Headsets-MAP    0
        #153    4    Cell Phone Accessories-MAP    0
        #MapList={'112','115','116','119','123','124','125','127','128','130','131','132','133','134','135','136','137','138','139','140','141','142','143','145','146','147','148','149','150','151','152','153'}
        customList={'112','116'}
        allList=[]
        for item in range(116,170):
            allList.append(item)
        listToProcess=customList
        for process in listToProcess:
            token = self.server.login(self.credential['mg_username'], self.credential['mg_password'])
            parms=[{'attribute_set_id':process}]
            productsList = self.server.call(token, 'catalog_product.list',parms)
            if productsList is not None:
                for product in productsList:
                    item=Item()
                    print "one more"
                    item.sku= product['sku']
                    item.getMagentoInfo(self.server, self.credential)
                    scrap=Scrap()
                    if scrap.scrapSingleUrl(item):
                        if item.getBHInfo():
                            data=item.RunComparation()
                            if data:
                                self.addrow(data)

class Item(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sku=''
        self.itemUrl=''
        self.itemName=''
        self.model=''
        self.mfr=''
        self.brand=''
        self.importer=''

        self.price=0.0
        self.specialPrice=0.0
        self.priceRebate=0.0
        self.dateRebateFrom=''
        self.dateRebateTo=''
        
        self.BHprice=0.0
        self.BHspecialPrice=0.0
        self.BHpriceRebate=0.0
        self.BHdateRebateTo=''
        self.BHTypeOfSell="Normal"
        self.BHname=''
        
        self.PriceSync=''
        self.breadcrumbs=[]

        self.brand=''
        self.importer=''
        self.nikon=False
        self.available=True
        self.headerInfo=''


    def getMagentoInfo(self,server,credencial):
        try: 
            token = server.login(credencial['mg_username'], credencial['mg_password'])
            
            if self.sku=='':
                if self.mfr=='':
                    parms=[{'name':str(self.itemName)}]
                else:
                    parms=[{'model':str(self.mfr)}]
                
                    products = server.call(token, 'catalog_product.list',parms)
                    sku=''
                    for product in products:
                        sku = product['sku']
        except Exception, x:
            print " Exception dataItems"
            print x
            return False
        else:
            sku=self.sku
        try:
            info = server.call(token, 'catalog_product.info',[sku+" "])
         
            self.price= info['price']
            self.specialPrice= info['special_price']
            self.model=info['model']
            self.dateRebateTo=str(re.search(r'(\d{4}-\d[\d+-]*-\d[\d+-]*)',info['special_to_date']).group()) if info['special_to_date'] else ''
            self.dateRebateFrom=str(re.search(r'(\d{4}-\d[\d+-]*-\d[\d+-]*)',info['special_from_date']).group()) if info['special_to_date'] else ''
            self.priceRebate=info['instant_savings'] if 'instant_savings' in info else 0
            self.PriceSync=info['pricesync'] if 'pricesync' in info else ''
            self.priceRebate=float(self.priceRebate) if self.priceRebate else 0
            self.specialPrice=float(self.specialPrice) if self.specialPrice else 0
            self.price=float(self.price) if self.price else 0
            return True             
        except Exception, x:
            print " Exception Magento call"
            print x 
            return False     
  
    def getBHInfo(self):
        monts={("JAN","Jan"):"01",("FEB","Feb"):"02",("MAR","Mar"):"03",("APR","Apr"):"04",("MAY","May"):"05",("JUN","Jun"):"06",("JUL","Jul"):"07",("AUG","Aug"):"08",("SEP","Sep"):"09",("OCT","Oct"):"10",("NOV","Nov"):"11",("DEC","Dec"):"12"}
        try:
            spider=Spider()
            headerInfo, itemPageRequest = spider.fetchData(self.itemUrl)

            dataPagesoup = BeautifulSoup(itemPageRequest)
            breadCrum=dataPagesoup.find('ul', {'id': 'breadcrumbs'}).find_all('li')
            if breadCrum is not None:
                for li in breadCrum:
                    self.breadcrumbs.append(li.text.strip())
             
            info=dataPagesoup.find("div", {"id": 'productInfo'})
            productInfo=re.search('(?i)cmCreateProductviewTag\("([^"]*?)",(\s*?"[^"]*?"),(\s*?"[^"]*?"),\s*?"([^"]*)"',itemPageRequest)
            self.BHspecialPrice=float(productInfo.group(4).replace('$','').replace(',',''))  if productInfo.group(4) else ''
            self.itemName= productInfo.group(2) if productInfo.group(2) else ''
    
            priceinfo=info.find("li", {"class":"price hiLight"})
            if priceinfo is None: 
                return False
            classaux=re.search('"*.value.*"',priceinfo.prettify())
    
            if classaux:
                classaux=classaux.group().replace("\"",'')
                self.BHprice=float(priceinfo.find("span", {"class":classaux}).text.strip().replace('$','').replace(',',''))
            if re.search('See cart for product details', info.text):
                self.BHTypeOfSell="incar"
              
            if re.search('Instant Saving', info.text):
                if self.BHTypeOfSell=="incar":
                    self.BHTypeOfSell="incar-rebate"
                else:
                    self.BHTypeOfSell="rebate"
                BHPriceRebateinfo=info.find("li", {"class":"instant hiLight rebates"})
                if BHPriceRebateinfo is None or re.search(r'%',BHPriceRebateinfo.text) :
                    return False
    
                self.BHpriceRebate=abs(float(BHPriceRebateinfo.find("span", {"class": "value red"}).text.strip().replace('$','').replace(',','')))
                 
                BHDateRebate=info.find("span", {"class": "offerEnds"}).text.strip()#.replace('\S', '')#.replace('\n', '').replace('\r', '')
                match=re.search(r'.......\'..',BHDateRebate)
                if match:
                    BHDateRebate= match.group().replace("'",'').split()
                    mont=monts[BHDateRebate[0]] if BHDateRebate[0] in monts else '00'
                    self.BHdateRebateTo="20"+BHDateRebate[2]+"-"+mont+"-"+("0"+BHDateRebate[1])[-2:]
            if self.BHprice==self.BHspecialPrice:
                self.BHspecialPrice=0
            return True
        except Exception, x:
            print x
            return False
   
    def RunComparation(self):
    
        if self.BHTypeOfSell=="normal" and self.price==self.BHprice and (self.specialPrice is None or self.specialPrice=='' ):
            return False
        if  re.search('imported',self.importer, re.IGNORECASE):
            return False
        Nikon=False
        UploadType=self.BHTypeOfSell
        UploadPrice=self.BHprice
        UploadSpecialPrice=self.BHspecialPrice
        UploadDateRebate=self.BHdateRebateTo
        UploadPriceRebate=self.BHpriceRebate
           
    
        BHList=[self.BHprice,self.BHspecialPrice,self.dateRebateTo,self.BHpriceRebate]
        magentoList=[self.price,self.specialPrice,self.BHdateRebateTo,self.priceRebate]
#    ,self.dateRebateTo
#ud.normalize('NFKD',self.BHdateRebateTo).encode('ascii','ignore'),
        different=False
        for i in range(3):
            if BHList[i]!=magentoList[i]:
                different=True

        if self.BHTypeOfSell=='normal': 
            UploadSpecialPrice=''
        if self.brand=='Nikon':
            UploadDateRebate=''
            UploadPriceRebate=''
            UploadPrice=self.BHspecialPrice-10
            UploadSpecialPrice=''
            UploadType='normal'
            if self.specialPrice==UploadPrice:
                return False
                Nikon=False
    
        if different or Nikon:
                
            data=[time.strftime("%b %d %Y %H:%M:%S"),"'"+self.sku,"'"+str(self.mfr),self.itemName,self.BHTypeOfSell,self.BHspecialPrice,self.BHprice,self.BHpriceRebate,self.BHdateRebateTo,self.specialPrice,self.price,self.priceRebate,self.dateRebateTo,UploadType,UploadSpecialPrice,UploadPrice,UploadPriceRebate,UploadDateRebate]
            
            for crumb in self.breadcrumbs[1:]:
                data.append(crumb)
    
            print data
            return data
        else:
            return False                       
    
class Scrap():
    def __init__(self):
        pass

    def scraplevel1(self,url):
        try: 
            spider=Spider()       
            headerInfo, itemPageRequest = spider.fetchData(url)
        except Exception, x:
            print x
            return False
        itemPagesoup = BeautifulSoup(itemPageRequest)
        blockGroup=itemPagesoup.find("div", {"class": "categoryGroup"}) 
        blocka=blockGroup.find_all('a',href=True)
        for category in  blocka:
            self.scraplevel2( category['href'])
                


    def scraplevel2(self, url,pgn=1):
        threading.Thread.__init__(self)
        tmp =url.split('/')
        urlIntern='http://www.bhphotovideo.com/c/buy/'+tmp[5]+'/ipp/100/ci/'+tmp[7]+'/pn/'+str(pgn)+'/N/'+tmp[9]
        #print "URL "+ urlIntern
        try:        
            headerInfo, itemPageRequest = self.spider.fetchData(urlIntern, self.referer)
        except Exception, x:
            print x
            return False
        itemPagesoup = BeautifulSoup(itemPageRequest)
        block=itemPagesoup.find_all("div", {"class": "productBlockCenter"})
        for itemBlock in block:
            item=Item()
            urlinfo=itemBlock.find("div", {"id": "productTitle"})
            Item.brand=itemBlock.find("div", {"class":"brandTop"})
            mfrinfo=itemBlock.find("li", {"class":"singleBullet"})
            importerinfo=itemBlock.find("div", {"id": "grayMarket"}).text if itemBlock.find("div", {"id": "grayMarket"}) is not None else ''


            item.importer= importerinfo if importerinfo else ''         
            item.mfr= mfrinfo.find("span", {"class": "value"}).text if mfrinfo else ''
            item.itemUrl=urlinfo.find('a')['href']
            if Item.itemUrl:
                self.dataItems (Item)
        if re.search('<a href="[^"]*" class="lnext">Next',itemPageRequest):
            return self.scraplevel2(url, pgn + 1)

    def scrapSingleUrl(self, item):

#        tmp =url.split('/')
#        urlIntern='http://www.bhphotovideo.com/c/buy/'+tmp[5]+'/ipp/100/ci/'+tmp[7]+'/pn/'+str(pgn)+'/N/'+tmp[9]
        #print "URL "+ urlIntern
       
        try:
            url='http://www.bhphotovideo.com/c/search?Ntt='+item.mfr+'&N=0&InitialSearch=yes&sts=ma&Top+Nav-Search='
            spider=Spider()        
            headerInfo, itemPageRequest = spider.fetchData(url)
        except Exception, x:
            print x
            return False
        itemPagesoup = BeautifulSoup(itemPageRequest)
        if itemPagesoup.find(text='No Results were found'):
            return False
        block=itemPagesoup.find_all("div", {"class": "productBlockCenter"})
        for itemBlock in block:
            urlinfo=itemBlock.find("div", {"id": "productTitle"})
            mfrinfo=itemBlock.find("li", {"class": "singleBullet"})
            item.mfr= mfrinfo.find("span", {"class": "value"}).text

            item.brand=itemBlock.find("div", {"class":"brandTop"})
            item.importer=itemBlock.find("div", {"id": "grayMarket"}).text if itemBlock.find("div", {"id": "grayMarket"}) is not None else ''
            print "comparation " +item.model+" vs "+item.mfr
            if item.model!=item.mfr:
                return False
            
            if item.importer!='Imported':
                item.itemUrl=urlinfo.find('a')['href']
                return True
        return False
 


if __name__ == "__main__":
#    filename=sys.argv[1]
    filename='test.csv'
    report=Report()
    report.create(filename)
#    token = server.login(mg_username, mg_password)
#    main = Main(mainUrl)
#    
#    main.scrapCatSup('http://www.bhphotovideo.com/c/browse/Support-Equipment/ci/8310/N/4075788771')
    #main.scrapItem('http://www.bhphotovideo.com/c/buy/Digital-Cameras/ci/9811/N/4288586282')
    #main.scrapItem('http://www.bhphotovideo.com/c/buy/Lenses/ci/15492/N/4288584250')

    #sendMail=send_mail()
    #sendMail.send(updateArchive)


