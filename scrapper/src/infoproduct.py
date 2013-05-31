import urllib
import urllib2
from bs4 import BeautifulSoup
import re
import ConfigParser
import xmlrpclib



config = ConfigParser.ConfigParser()
config.read("config.ini")
#tip="magento_test"
tip="magento_live"
#tip="magento_local"

#output='output.csv'
#writer = csv.writer(open("output.csv", "wb"))
mg_url = config.get(tip, "mg_url")
mg_username = config.get(tip, "mg_username")
mg_password = config.get(tip, "mg_password")
server = xmlrpclib.ServerProxy(mg_url)






token = server.login(mg_username, mg_password)
info = server.call(token, 'catalog_product.info',['031293019806 '])
#print server.call(token, 'getManufacturerText','481')
print info
