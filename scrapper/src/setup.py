from distutils.core import setup 
import py2exe 

setup(name="GenerateAndSendComparation", 
scripts=["ScrapperWithMail.py"], 
console=["ScrapperWithMail.py"],
options={"py2exe": {"bundle_files": 1}},
zipfile=None
)

