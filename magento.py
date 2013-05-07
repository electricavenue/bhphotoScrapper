import xmlrpclib
import ConfigParser
import csv
import threading

class Main(threading.Thread):
    def __init__(self):
        pass
    def insert(self):
        threading.Thread.__init__(self)
        server = xmlrpclib.ServerProxy(mg_url)
        token = server.login(mg_username, mg_password)

        for row in infile:
            sku = row[1].replace("'","")
            (typeofSell,SpecialPrice,price,Rebate,DateRebate)=(row[14:19])
#            if mfr=='':
#                parms=[{'name':str(BHname)}]
#            else:
#                parms=[{'model':str(mfr.replace("'",""))}]
#            products = server.call(token, 'catalog_product.list',parms)
#            sku=''
#            for product in products:
#                sku = product['sku']
            
            if sku:
                try:
                
                    #info = server.call(token, 'catalog_product.info',[sku])
#                    magentoPrice= info['price']
#                    magentoEspecialPrice= info['special_price']
#                    BHprice=BHprice.replace("$", '').replace(",","")
#                    priceRebate=priceRebate.replace("$", '').replace(",","")

                    """
                    msrp_display_actual_price_type
                    
                    4 use config
                    3 on gesture
                    1 incart
                    
                    msrp_enabled  Apply MAP
                    0 No
                    1 Yes
                    
                    
                    
                    """


                    data={'price':price}
                    
                    if typeofSell=='normal':
                        data['msrp_enabled']='0'
                        data['special_price']=''
                        data['special_to_date']=''
                        data['instant_savings']=''                        
                    if typeofSell=='incar':
                        data['msrp_enabled']='1'
                        data['special_price']=SpecialPrice
                        data['special_to_date']=''
                        data['instant_savings']=''
                    if typeofSell=='rebate':
                        data['msrp_enabled']='0'
                        data['special_price']=SpecialPrice  
                        data['special_to_date']=str(DateRebate)
                        data['instant_savings']=Rebate                                                                         
                    if typeofSell=='incar-rebate':
                        data['msrp_enabled']='1'
                        data['special_price']=SpecialPrice 
                        data['special_to_date']=str(DateRebate)
                        data['instant_savings']=Rebate




                        
                    print sku
                    parms=[sku+" ",data]
                    #print data
                    dataStok = server.call(token, 'product_stock.list',[sku])
                    del dataStok[0]['sku']
                    dataStok[0]['manage_stock']='1'
                    dataStok[0]['use_config_manage_stock']='1'
                    dataStok.insert(0,sku) 
                    print dataStok                   
                    r = server.call(token, 'catalog_product.update',parms)
                    server.call(token, 'product_stock.update',dataStok)
                    #print parms
                    #print r
                    
                    writer.writerow([r,sku])
                except Exception, x:
                    print x

        

            
            
#


if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    #tip="magento_test"
    tip="magento_live"
    filename="2013-04-29_updates.csv"
    infile = csv.reader(open(filename))
    output='output.csv'
    writer = csv.writer(open("output.csv", "wb"))
    mg_url = config.get(tip, "mg_url")
    mg_username = config.get(tip, "mg_username")
    mg_password = config.get(tip, "mg_password")
    main = Main()
    main.insert()
