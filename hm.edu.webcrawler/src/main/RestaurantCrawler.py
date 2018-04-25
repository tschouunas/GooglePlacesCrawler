# coding=utf8
from builtins import print
import time
from tinydb import TinyDB, Query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import wait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.expected_conditions import alert_is_present
from ftplib import print_line

'''
Created on 17.04.2018

@author: Tschounas


'''


class Review:
    '''
    classdocs
    '''

    def __init__(self, userName, reviewStars, comment, pictures=[]):
        self.userName = userName
        self.reviewStars = reviewStars
        self.comment = comment
        self.pictures = pictures
        '''
        Constructor
    
        '''
class Restaurant:
    '''
    classdocs
    '''

    def __init__(self, restaurant_title, restaurant_stars, rush_hours, reviewList=[]):
        self.restaurant_title = restaurant_title
        self.restaurant_stars = restaurant_stars
        self.rush_hours = rush_hours
        self.reviewList = reviewList
        '''
        Constructor
    
        '''

def main():
    city = 'Muenchen'
    print('Ueber welches Restaurant in ' + city + ' wollen Sie Informationen erhalten?:')
    restaurantName = "Alter Wirt"
    # restaurantName = input()
    navigateToRestaurantDetailPage(restaurantName, city)
        


def navigateToRestaurantDetailPage(restaurantName , city):
        
        url = 'https://www.google.de/maps/search/' + restaurantName + '/@48.151241,11.4996846,12z'
        print(url)
        
        driver = webdriver.Chrome(executable_path='..\..\driver\chromedriver.exe')
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
    restaurant_rushHour = ''
    numberOfReviewsButton = driver.find_element_by_class_name('section-reviewchart-numreviews')
    numberOfReviews = int(numberOfReviewsButton.get_attribute("innerHTML")[0:-9])
        
    print(restaurant_title)
    print(restaurant_stars)
    print(numberOfReviews)
        
    numberOfReviewsButton.click()
    reviewDetailPage = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-header-title')))
    if reviewDetailPage.get_attribute("innerHTML") == 'Alle Rezensionen':
        # Crawl Comments
        scrollOverAllReviews(driver, 0.2, wait, 25)
       
        reviewList = []
        reviewBox = driver.find_elements_by_class_name('section-review-content')
        
        print(len(reviewBox))
        
        print('Reviews:')
        print('')
        db = TinyDB('..\database\db.json')
        db.purge()
        restaurantTable = db.table('RESTAURANT TABLE')
        reviewTable = db.table('REVIEW TABLE')
        reviewPicturesTable = db.table('REVIEW PICTURE TABLE')
        

        
        for x in range (0, len(reviewBox)-1) :
            userName = reviewBox[x].find_element_by_class_name('section-review-title').get_attribute("innerText")
            reviewText = reviewBox[x].find_element_by_class_name('section-review-text').get_attribute("innerText")
            reviewStars = reviewBox[x].find_element_by_class_name('section-review-stars').get_attribute("aria-label")
            reviewPhotoList = []
            
            present = False
            try:
                driver.find_elements_by_class_name('section-review-photo')
                present = True
            except Exception as err:
                print('Element: section-review-photo missing', err)    
            if(present == True):
                photoCount = len(reviewBox[x].find_elements_by_class_name('section-review-photo'))
                for i in range (0, photoCount):
                    reviewPhotoList.append(reviewBox[x].find_elements_by_class_name('section-review-photo')[i].get_attribute("style")[21:])
                print(reviewPhotoList)
            else:
                reviewPhotoList = [None]
            review = Review(userName, reviewStars, reviewText, reviewPhotoList)
            reviewList.append(review)
            print('User: ' + review.userName)
            print('Sterne: ' + review.reviewStars)
            print('Comment: ' + review.comment)
            if(review.pictures):
                print('PicturesCount: ' + str(len(review.pictures)))
                for k in range (0, len(review.pictures)) :
                    print('Pictures' + review.pictures[k])
            print('---------------------------------------------------')
        
        restaurant = Restaurant(restaurant_title, restaurant_stars, restaurant_rushHour , reviewList)
        
        insertReviewIntoDB(restaurant, restaurantTable, reviewTable, reviewPicturesTable)    
    
        
def insertReviewIntoDB(restaurant, restaurantTable, reviewTable, reviewPicturesTable):
 
    restaurantTable.insert({'Restaurantname': restaurant.restaurant_title, 'Gesamtbewertung' : restaurant.restaurant_stars, 'Stosszeiten' : restaurant.rush_hours})    
    reviewTable.insert_multiple({'Restaurantname': restaurant.restaurant_title,'User':  restaurant.reviewList[i].userName, 'Sterne':  restaurant.reviewList[i].reviewStars, 'Kommentar':  restaurant.reviewList[i].comment, } for i in range(len(restaurant.reviewList)))
    print('Database Pictures:')
    print('')
    for j in range (0, len(restaurant.reviewList)-1):
        print('Reviewer: ' + restaurant.reviewList[j].userName)
        for k in range (0,len(restaurant.reviewList[j].pictures)):
            
            print(restaurant.reviewList[j].pictures[k])
            reviewPicturesTable.insert({'User':  restaurant.reviewList[j].userName, 'BildURL':  restaurant.reviewList[j].pictures[k]})
        
           
def scrollOverAllReviews(driver, scroll_pause_time, wait, numberOfReviews):
        
        # Get scroll height
    for i in range(8, numberOfReviews):
            scrollElement = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[8]/div[' + str(i) + ']/div/div[3]/div[2]/div/div[4]/button[1]')))
            #ActionChains(driver).move_to_element(scrollElement).perform()
            driver.execute_script("return arguments[0].scrollIntoView();", scrollElement)

            time.sleep(scroll_pause_time)
        

main()

