'''
Created on 11.04.2018

@author: Tschounas

'''
# coding=utf8
from builtins import print
# from tinydb import TinyDB, Query
import time


from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import wait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# if foundElement:
#     while (foundElement)==0:
#         time.sleep(100)
#     foundElement.click()
#     while len(driver.find_element_by_class_name('class="section-hero-header-description"'))==0:
#         time.sleep(100)
#     
#     restaurant_title = driver.find_element_by_class_name('section-hero-header-title').get_attribute("innerHTML")
#     restaurant_stars = driver.find_element_by_class_name('section-star-display').get_attribute("innerHTML")
#     
#     print(restaurant_title)
#     
#     
#     
#     driver.quit()



        
    def navigateToRestaurantDetailPage(restaurantName ,city):
        
        url = 'https://www.google.de/maps/search/' + restaurantName + '/@48.151241,11.4996846,12z'
        print(url)
        
        driver = webdriver.Chrome(executable_path='C:/Users/Tschounas/python_workspace/hm.edu.webcrawler/chromedriver.exe')
        driver.get(url) 
        
#         try:
#         foundElement = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[3]/div[1]')))
#         except ValueError:
#         print("Oops!  Element could not get loaded.  Try again...")
#         
#         foundElement.click()
#         

        city = 'Muenchen'
        print('Ueber welches Restaurant in ' + city + ' wollen Sie Informationen erhalten?:')
        restaurantName = "Alter Wirt"
        #restaurantName = input()
        
    navigateToRestaurantDetailPage(restaurantName, city)
      
    
            
 











    
   
  
    
#data-result-index="1"
#

# db = TinyDB('C:/Users/Tschounas/python_workspace/hm.edu.webcrawler/src/db.json')
# 
# crawledList = ['Alter Wirt', 'Bayrisches Restaurant', 4.8, 'Stosszeiten', ['Kundenname', 4.72, 'Bewertungstext', 'BildURL']]
# 
# 
# db.insert({'Restaurantname': crawledList[0], 'RestaurantType': crawledList[1], 'Gesamtbewertung' : crawledList[2]})
# 
# 
# for item in db:
#     print(item)
#     
# restaurant = Query()
# print(db.search(restaurant.Gesamtbewertung == 4.8))

