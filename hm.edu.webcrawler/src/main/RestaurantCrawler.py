# coding=utf8
from builtins import print
import time
from tinydb import TinyDB, Query, where
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from inspect import stack

'''
Created on 17.04.2018

@author: Jonas Kammerl


'''


class Review:

    def __init__(self, userName, reviewStars, comment, pictures=[]):
        self.userName = userName
        self.reviewStars = reviewStars
        self.comment = comment
        self.pictures = pictures

class Restaurant:

    def __init__(self, restaurant_title, restaurant_stars, rush_hours, reviewList=[]):
        self.restaurant_title = restaurant_title
        self.restaurant_stars = restaurant_stars
        self.rush_hours = rush_hours
        self.reviewList = reviewList


def main():
    city = 'Muenchen'
    print('Ueber welches Restaurant in ' + city + ' wollen Sie Informationen erhalten?:')

    restaurantName = input()
    navigateToRestaurantDetailPage(restaurantName, city)
    print(restaurantName + " wurde erfolgreich gecrawled!")


def navigateToRestaurantDetailPage(restaurantName , city):
        
    url = 'https://www.google.de/maps/search/' + restaurantName + '/@48.151241,11.4996846,12z'
    print(url)
        
    driver = webdriver.Chrome(executable_path='..\..\driver\chromedriver.exe')
    driver.set_window_position(0, 0)
    driver.set_window_size(1024, 768)
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    try:
        
        googleElement = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="consent-bump"]/div/div[2]/span/button[1]')))
        if(googleElement):
            googleElement.click()
    finally:        
        
        try:  
            present = False
            try:
                productDetailPage = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-hero-header-description')))
                present = True
            except:    
                present = False
                    
            if(present == False):  
                print("Mehrer Ergebnisse wurden gefunden --- Es wird das erste Restaurant in der Liste ausgewählt")     
                results = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-result-content')))
                if(results):
                    foundElements = driver.find_elements_by_class_name('section-result-content')
                    if(foundElements):
                        foundElements[0].click()
            else:
                productDetailPage = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-hero-header-description'))) 
                                    
        except Exception as err:
            print('Es wurde kein Ergebniss für das Restaurant: ' + restaurantName + ' gefunden.')
            driver.close()
                          
        crawlData(driver, wait)
       
        
def crawlData(driver, wait):  
    
    try:
        db = TinyDB('..\database\db.json', sort_keys=True, indent = 4)
        db.purge()
        restaurantTable = db.table('RESTAURANT TABLE')
        reviewTable = db.table('REVIEW TABLE')
        reviewPicturesTable = db.table('REVIEW PICTURE TABLE')
        
    except:
        print("Fehler beim Anlegen der Datenbank")
             
    try:
        googlePlace = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div[2]/span[1]/span[1]/button'))).get_attribute("innerHTML")
    except:
        googlePlace = None
        print('Gefundener Ort ist kein Restaurant')    
    
    if('Restaurant' in googlePlace or 'restaurant' in googlePlace):
        
            restaurant_title = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-hero-header-title'))).get_attribute("innerHTML")
            restaurant_stars = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-star-display'))).get_attribute("innerHTML")
            restaurant_rushHour = ''
            numberOfReviewsButton = driver.find_element_by_class_name('section-reviewchart-numreviews')
            numberOfReviews = numberOfReviewsButton.get_attribute("innerHTML")[0:-9]
            if('.' in numberOfReviews):
                numberOfReviews = int(numberOfReviews.replace('.', ''))
            else:
                numberOfReviews = int(numberOfReviews)
                
            print(restaurant_title)
            print(restaurant_stars)
            print(numberOfReviews)
            
                
            numberOfReviewsButton.click()
            reviewDetailPage = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-header-title')))
            if reviewDetailPage.get_attribute("innerHTML") == 'Alle Rezensionen':
                # Crawl Comments
                
                reviewList = scrollOverAllReviews(driver, 0.1, wait, numberOfReviews)
                
                restaurant = Restaurant(restaurant_title, restaurant_stars, restaurant_rushHour , reviewList)
                
                insertReviewIntoDB(restaurant, restaurantTable, reviewTable, reviewPicturesTable)  
           
    else: 
            print('Gefundener Ort ist kein Restaurant')
    
        
def insertReviewIntoDB(restaurant, restaurantTable, reviewTable, reviewPicturesTable):
    
    if not(checkForDuplicate('Restaurantname',restaurant.restaurant_title, restaurantTable)):
           
        restaurantTable.insert({'Restaurantname': restaurant.restaurant_title, 'Gesamtbewertung' : restaurant.restaurant_stars, 'Stosszeiten' : restaurant.rush_hours})    
    else:
        print("Restaurant wurde bereits in der Vergangenheit gecrawled")
        print("Update der Datenbank erfolgt!")     
        
    for i in range (0, len(restaurant.reviewList) - 1):   
        if not(checkForDuplicate('User',restaurant.reviewList[i].userName, reviewTable)):       
            reviewTable.insert({'Restaurantname': restaurant.restaurant_title, 'User':  restaurant.reviewList[i].userName, 'Sterne':  restaurant.reviewList[i].reviewStars, 'Kommentar':  restaurant.reviewList[i].comment})
            for k in range (0, len(restaurant.reviewList[i].pictures)):
                if(len(restaurant.reviewList[i].pictures) >= 1 and "https" in restaurant.reviewList[i].pictures[k]):
                    reviewPicturesTable.insert({'User':  restaurant.reviewList[i].userName, 'BildURL':  restaurant.reviewList[i].pictures[k]})
       
#Wrapper Funktion um zu überprüfen ob das Element bereits in der Datenbank enthalten ist.    
        
def checkForDuplicate (dbfield, element, dbTable): 
           
    if(dbTable.contains((where(dbfield) == element))): 
        return True 
    else:
        return False   


def scrollOverAllReviews(driver, scroll_pause_time, wait, numberOfReviews):
    
    print('Reviews:')
    print('')
    reviewList = []
        
    #for i in range(1, numberOfReviews):
    for i in range(1, 20):    
        # google stops loading after 835 Reviews
        if(i >= 835):
            break
        else:    
            ownerReviewIsPresent = False
            try:
                scrollElement = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[8]/div[' + str(i) + ']')))
            except Exception as err:
                print('Owner Review gefunden: Element wird übersprungen')
                
                ownerReview = scrollElement.find_element_by_class_name('section-review-owner-response-title')
                
                ownerReviewIsPresent = True
            if(ownerReviewIsPresent == True): 
                
                driver.execute_script("return arguments[0].scrollIntoView();", ownerReview)
            
                time.sleep(scroll_pause_time)   
            
            else:
                
                userName = scrollElement.find_element_by_class_name('section-review-title').get_attribute("innerText")
                # Mehr Button im Review
                expandButtonIsPresent = False
                try:
                    expandReviewButton = scrollElement.find_element_by_css_selector('button.section-expand-review.blue-link')
                    
                    if(expandReviewButton.get_attribute("style") != "display: none;"):
                                            
                        expandButtonIsPresent = True
                except:
                    
                    expandButtonIsPresent = False
                    
                if(expandButtonIsPresent == True):
                    
                    expandReviewButton.click()
                
                reviewText = scrollElement.find_element_by_class_name('section-review-text').get_attribute("innerText")
                reviewStars = scrollElement.find_element_by_class_name('section-review-stars').get_attribute("aria-label")
                reviewPhotoList = []
                
                present = False
                try:
                    driver.find_elements_by_class_name('section-review-photo')
                    present = True
                except Exception as err:
                    print('Element: section-review-photo missing', err)    
                if(present == True):
                    photoCount = len(scrollElement.find_elements_by_class_name('section-review-photo'))
                    for i in range (0, photoCount):
                        reviewPhotoList.append(scrollElement.find_elements_by_class_name('section-review-photo')[i].get_attribute("style")[21:])
                   
                else:
                    reviewPhotoList = [None]
                review = Review(userName, reviewStars, reviewText, reviewPhotoList)
                reviewList.append(review)
                print('User: ' + review.userName)
                print('Sterne: ' + review.reviewStars)
                print('Comment: ' + review.comment)
                if(review.pictures):
                    print('PicturesCount: ' + str(len(review.pictures) - 1))
                    for k in range (0, len(review.pictures)) :
                        print('Pictures' + review.pictures[k])
                print('---------------------------------------------------')
                
                driver.execute_script("return arguments[0].scrollIntoView();", scrollElement)
            
                time.sleep(scroll_pause_time)
            
    return reviewList   

main()

