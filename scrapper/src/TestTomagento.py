import xmlrpclib
import ConfigParser
import threading

class Main(threading.Thread):
    def __init__(self):
        pass
    def insert(self):
        threading.Thread.__init__(self)
        server = xmlrpclib.ServerProxy(mg_url)
        token = server.login(mg_username, mg_password)


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
            
            2013-27-4
            
            """
            sku='701001011315 '
            data={}

            data['msrp_enabled']='0'
            #data['special_price']=None
            data['special_to_date']='2013-27-4'
            #data['instant_savings']=None
            #data['special_price']=None          
            
            
            

            parms=[sku,data]
            
            dataStok = server.call(token, 'product_stock.list',[sku])
            del dataStok[0]['sku']
            dataStok[0]['manage_stock']='1'
            dataStok[0]['use_config_manage_stock']='1'
            dataStok.insert(0,sku)

            
            r = server.call(token, 'catalog_product.update',parms)
            print r 
            server.call(token, 'product_stock.update',dataStok)
             
            
            print dataStok
        except Exception, x:
            print "Error  " 
            print x
if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    tip="magento_test"
    mg_url = config.get(tip, "mg_url")
    mg_username = config.get(tip, "mg_username")
    mg_password = config.get(tip, "mg_password")
    main = Main()
    main.insert()
