'''
Created on 17.05.2018

@author: Tschounas
'''
import py2exe
from distutils.core import setup


setup(console= ['RestaurantCrawler.py'],
options={
            "py2exe":{
                    "skip_archive": True,
                    "unbuffered": True,
                    "optimize": 2
            }
    }
)