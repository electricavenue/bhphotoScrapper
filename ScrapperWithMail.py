import cookielib
import urllib
import urllib2
import xmlrpclib
import ConfigParser
from bs4 import BeautifulSoup
import csv
import re
from datetime import date
import time
import threading
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
class item(object):
    def __init__(self):
        self.sku=''
        self.itemUrl=''
        self.itemName=''
        self.price=0.0
        self.specialPrice=0.0
        self.priceRebate=0.0
        self.dateRebate=''
        self.BHprice=0.0
        self.BHspecialPrice=0.0
        self.BHpriceRebate=0.0
        self.BHdateRebate=''
        self.brand=''
        self.importer=''
        self.nikon=False
        self.available=True
        self.headerInfo=''


class getMagentoInfo():
    def __init__(self):
        pass
    def run(self,Item):
        token = server.login(mg_username, mg_password)

          
 
        if Item.mfr=='':
            parms=[{'name':str(name)}]
        else:
            parms=[{'model':str(Item.mfr)}]
        try: 
            products = server.call(token, 'catalog_product.list',parms)
            sku=''
            for product in products:
                sku = product['sku']
        except Exception, x:
            print " Exception dataItems"
            print x
            sku=None
 
        
        if sku:
            try:
                info = server.call(token, 'catalog_product.info',[sku+" "])
                magentoPrice= info['price']
                magentoSpecialPrice= info['special_price']
                magentoDateRebate=info['special_to_date']
                magentoPriceRebate=info['instant_savings']
                magentoSKU=info['sku']
                magentoPriceSync=info['pricesync']
                if magentoPriceSync!='1':
                    return 0
                magentoDateRebate=str(re.search(r'(\d{4}-\d[\d+-]*-\d[\d+-]*)',magentoDateRebate).group()) if magentoDateRebate else ''
                magentoPriceRebate=float(magentoPriceRebate) if magentoPriceRebate else ''
                magentoSpecialPrice=float(magentoSpecialPrice) if magentoSpecialPrice else ''
                magentoPrice=float(magentoPrice) if magentoPrice else ''             
            
            
            
            
            
            
            
            
            

        
        
class Main(threading.Thread):
    def __init__(self, url):
        self.spider = Spider()
        self.mainUrl = url
        self.referer = None

    def scrapCatSup(self,url):
        try:        
            headerInfo, itemPageRequest = self.spider.fetchData(url, self.referer)
        except Exception, x:
            return False
        itemPagesoup = BeautifulSoup(itemPageRequest)
        blockGroup=itemPagesoup.find("div", {"class": "categoryGroup"}) 
        blocka=blockGroup.find_all('a',href=True)
        for cat in  blocka:
            self.scrapItem( cat['href'])
                


    def scrapItem(self, url,pgn=1):

            
        #print "Pagina "+str(pgn)
        threading.Thread.__init__(self)
        tmp =url.split('/')
        urlIntern=mainUrl+'/c/buy/'+tmp[5]+'/ipp/100/ci/'+tmp[7]+'/pn/'+str(pgn)+'/N/'+tmp[9]
        #print "URL "+ urlIntern
        try:        
            headerInfo, itemPageRequest = self.spider.fetchData(urlIntern, self.referer)
        except Exception, x:
            return False
        itemPagesoup = BeautifulSoup(itemPageRequest)
        block=itemPagesoup.find_all("div", {"class": "productBlockCenter"})
        for itemBlock in block:
            Item=item()
            itemurlinfo=itemBlock.find("div", {"id": "productTitle"})
            Item.brand=itemBlock.find("div", {"class":"brandTop"})
            mfrinfo=itemBlock.find("li", {"class":"singleBullet"})
            Item.importer=itemBlock.find("div", {"id": "grayMarket"}).text
            #Nikon=True if brand.text=="Nikon" and  tmp[5]=="Lenses" else False
            #Nikon=True if brand.text=="Nikon" else False            
            if  not re.search('imported',Item.importer, re.IGNORECASE):
                if mfrinfo!=None:            
                    Item.mfr= mfrinfo.find("span", {"class": "value"}).text
                else:
                    Item.mfr='' 
                Item.itemUrl=itemurlinfo.find('a')['href']
                if Item.itemUrl:
                    self.dataItems (Item)
        if re.search('<a href="[^"]*" class="lnext">Next',itemPageRequest):
            return self.scrapItem(url, pgn + 1)

    
    def dataItems(self,Item):
        try:
            headerInfo, itemPageRequest = self.spider.fetchData(Item.itemUrl, self.referer)
        except Exception, x:
            return False
        #print headerInfo

        dataPagesoup = BeautifulSoup(itemPageRequest)
        breadcrumbs=[]
        for li in dataPagesoup.find('ul', {'id': 'breadcrumbs'}).find_all('li'):
            breadcrumbs.append(li.text.strip())
         
        BHPrice=''
        BHSpecialPrice= ''
        name=''
        code=''
        BHTypeOfSell="normal"
        BHPriceRebate=''
        BHDateRebate=''

        info=dataPagesoup.find("div", {"id": 'productInfo'})

        productInfo=re.search('(?i)cmCreateProductviewTag\("([^"]*?)",(\s*?"[^"]*?"),(\s*?"[^"]*?"),\s*?"([^"]*)"',itemPageRequest)
        code= productInfo.group(1) if productInfo.group(1) else ''
        name= productInfo.group(2) if productInfo.group(2) else ''
        BHSpecialPrice=float(productInfo.group(4).replace('$','').replace(',',''))  if productInfo.group(4) else ''


        priceinfo=info.find("li", {"class":"price hiLight"})
        if priceinfo==None: 
            log.writerow([code,'exception any without price hilight'])
            return 0
        classaux=re.search('"*.value.*"',priceinfo.prettify())

        if classaux:
            classaux=classaux.group().replace("\"",'')
            BHPrice=float(priceinfo.find("span", {"class":classaux}).text.strip().replace('$','').replace(',',''))

            

                    

        if re.search('See cart for product details', info.text):
            BHTypeOfSell="incar"

            
        if re.search('Instant Saving', info.text):
            if BHTypeOfSell=="incar":
                BHTypeOfSell="incar-rebate"
            else:
                BHTypeOfSell="rebate"
            BHPriceRebateinfo=info.find("li", {"class":"instant hiLight rebates"})
            if BHPriceRebateinfo in (None,"",False) or re.search(r'%',BHPriceRebateinfo.text) :
                log.writerow([code,'exception Rebate without value red'])
                return 0

            BHPriceRebate=abs(float(BHPriceRebateinfo.find("span", {"class": "value red"}).text.strip().replace('$','').replace(',','')))
             
            BHDateRebate=info.find("span", {"class": "offerEnds"}).text.strip()#.replace('\S', '')#.replace('\n', '').replace('\r', '')
            match=re.search(r'.......\'..',BHDateRebate)
            if match:
                BHDateRebate= match.group().replace("'",'').split()
                BHDateRebate[0]=monts[BHDateRebate[0]]
                BHDateRebate="20"+BHDateRebate[2]+"-"+BHDateRebate[0]+"-"+("0"+BHDateRebate[1])[-2:]
#
#
#            if price!= special_price and incar=="normal":
#                incar=incar+"WithShow"
#        
#        else:
#            price=special_price
#            incar=incar+"WitoutShow"
   

                if BHTypeOfSell=="normal" and magentoPrice==BHPrice and (magentoSpecialPrice==None or magentoSpecialPrice=='' ):
                    return 0
                
                
                
                UploadType=BHTypeOfSell
                UploadPrice=BHPrice
                UploadSpecialPrice=BHSpecialPrice
                UploadDateRebate=BHDateRebate
                UploadPriceRebate=BHPriceRebate

#                if LensesNikon:
#                    special_price=price
#                    incar="normal"
                    

                BHList=[BHPrice,BHSpecialPrice,BHDateRebate,BHPriceRebate]
                magentoList=[magentoPrice,magentoSpecialPrice,magentoDateRebate,magentoPriceRebate]

                different=False
                for i in range(3):
                    if BHList[i]!=magentoList[i]:
                        different=True
                if BHTypeOfSell=='normal': 
                    UploadSpecialPrice=''
                if Nikon:
                    UploadDateRebate=''
                    UploadPriceRebate=''
                    UploadPrice=BHSpecialPrice-10
                    UploadSpecialPrice=''
                    UploadType='normal'
                    if magentoPrice==UploadPrice:
                        different=False
                        Nikon=False

                if different or Nikon:
                        
                    data=[time.strftime("%b %d %Y %H:%M:%S"),"'"+magentoSKU,"'"+str(mfr),"'"+str(code),name,BHTypeOfSell,BHSpecialPrice,BHPrice,BHPriceRebate,BHDateRebate,magentoSpecialPrice,magentoPrice,magentoPriceRebate,magentoDateRebate,UploadType,UploadSpecialPrice,UploadPrice,UploadPriceRebate,UploadDateRebate]
                    
                    for crumb in breadcrumbs[1:]:
                        data.append(crumb)

                    writer.writerow(data)
                    print data                       
        
        
            except Exception, x:
                print " error catalog_product"
                print x            


if __name__ == "__main__":
    mainUrl = "http://www.bhphotovideo.com"
    monts={"JAN":"01","FEB":"02","MAR":"03","APR":"04","MAY":"05","JUN":"06","JUL":"07","AUG":"08","SEP":"09","OCT":"10","NOV":"11","DEC":"12"}
    Header=["Date generated","SKU","MFR","BH-Code","Name","BH Special Price","BH Price","BH Type of Sell","BH Price Rebate","BH Date Rebate","EA Special Price","EA Price","EA Price Rebate","EA Date Rebate","Type of sell to upload","Special Price to Upload","Price To Upload","Rebate to Upload","Date Rebate to Upload"]

    updateArchive=str(date.today())+"_updates.csv"
    writer = csv.writer(open(updateArchive, "wb"))
    writer.writerow(Header)
    log = csv.writer(open("log.csv", "a"))
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    #tip="magento_test"
    tip="magento_live"
    mg_url = config.get(tip, "mg_url")
    mg_username = config.get(tip, "mg_username")
    mg_password = config.get(tip, "mg_password") 
    
    server = xmlrpclib.ServerProxy(mg_url)
    token = server.login(mg_username, mg_password)
    main = Main(mainUrl)
    
    main.scrapCatSup('http://www.bhphotovideo.com/c/browse/Support-Equipment/ci/8310/N/4075788771')
    #main.scrapItem('http://www.bhphotovideo.com/c/buy/Digital-Cameras/ci/9811/N/4288586282')
    #main.scrapItem('http://www.bhphotovideo.com/c/buy/Lenses/ci/15492/N/4288584250')

    #sendMail=send_mail()
    #sendMail.send(updateArchive)


