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


'''
Created on 17.04.2018

@author: Tschounas
'''

def navigateToRestaurantDetailPage(restaurantName ,city):
        
        url = 'https://www.google.de/maps/search/' + restaurantName + '/@48.151241,11.4996846,12z'
        print(url)
        
        driver = webdriver.Chrome(executable_path='C:/Users/Tschounas/python_workspace/hm.edu.webcrawler/chromedriver.exe')
        driver.get(url) 
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[3]/div[1]')))
        foundElement = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[3]/div[1]')
        if(foundElement):
            foundElement.click()
        
        productDetailPage = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-hero-header-description')))
        
        
        crawlData(driver, wait)
        
        
        driver.close()
        
       
        
def crawlData(driver, wait):     
    
    restaurant_title = driver.find_element_by_class_name('section-hero-header-title').get_attribute("innerHTML")
    restaurant_stars = driver.find_element_by_class_name('section-star-display').get_attribute("innerHTML")
    numberOfReviewsButton = driver.find_element_by_class_name('section-reviewchart-numreviews')
    numberOfReviews = numberOfReviewsButton.get_attribute("innerHTML")
        
    print(restaurant_title)
    print(restaurant_stars)
    print(numberOfReviews)
        
    numberOfReviewsButton.click()
    ReviewDetailPage = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-tab-info-stats-button-flex')))
        
    # Crawl Comments
        
    driver.execute_script("window.scrollBy(0, -150);")
          
        
        
        
        
        
      
       
             
        
        
city = 'Muenchen'
print('Ueber welches Restaurant in ' + city + ' wollen Sie Informationen erhalten?:')
restaurantName = "Alter Wirt"
#restaurantName = input()


navigateToRestaurantDetailPage(restaurantName, city)


