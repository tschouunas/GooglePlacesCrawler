# coding=utf8
from builtins import print
import time
from tinydb import TinyDB, where
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import *
from tkinter import ttk

'''
Created on 17.04.2018

@author: Jonas Kammerl


'''

# Global GUI implementation
gui = Tk()
mainframe = ttk.Frame(gui, padding="3 3 12 12") 
messageText = Message(mainframe, width = 400)
restaurantTextbox = Text(mainframe, width = 49, height = 5)  
reviewTextbox = Text(mainframe, width=49, height=25)

'''     
class to represent a review of an user
'''
class Review:

    def __init__(self, userName, reviewStars, comment, pictures=[]):
        self.userName = userName
        self.reviewStars = reviewStars
        self.comment = comment
        self.pictures = pictures


'''     
class to represent a restaurant
'''
class Restaurant:

    def __init__(self, restaurant_title, restaurant_stars, rush_hours, reviewList=[]):
        self.restaurant_title = restaurant_title
        self.restaurant_stars = restaurant_stars
        self.rush_hours = rush_hours
        self.reviewList = reviewList

'''     
main method to start the GUI and the webcrawler
 
'''
def main(restaurantName, city):
    
    #city = 'Muenchen'
    #print('Ueber welches Restaurant in ' + city + ' wollen Sie Informationen erhalten?:')

    #restaurantName = input() 
    clearGUI()  
    navigateToRestaurantDetailPage(restaurantName, city)
    printMsg(restaurantName + " wurde erfolgreich gecrawled!")

'''     
method to navigate to the Google Place
validates if the place is a restaurant and uses the method crawlData() to safe the data 
 
'''
def navigateToRestaurantDetailPage(restaurantName , city):
        
    url = 'https://www.google.de/maps/search/' + restaurantName + '/@48.151241,11.4996846,12z'
    print(url)
    printMsg('URL wird in Google Chrome aufgerufen...')     
        
    driver = webdriver.Chrome(executable_path='..\..\driver\chromedriver.exe')
    driver.set_window_position(450, 0)
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
                print("Mehrer Ergebnisse wurden gefunden. Es wird das erste Restaurant in der Liste ausgewählt")   
                printMsg("Mehrer Ergebnisse gefunden, erstes Restaurant der Liste wird ausgewählt.")  
                results = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-result-content')))
                if(results):
                    foundElements = driver.find_elements_by_class_name('section-result-content')
                    if(foundElements):
                        foundElements[0].click()
            else:
                productDetailPage = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-hero-header-description'))) 
                                    
        except Exception as err:
            print('Es wurde kein Ergebniss für das Restaurant: ' + restaurantName + ' gefunden.')
            printMsg('Es wurde kein Ergebniss für ' + restaurantName + ' gefunden.')
            
            driver.close()
                          
        crawlData(driver, wait)
 
'''     
method to crawl the data with selenium and safe the restaurant data to objects from class restaurant.
After safing the data, the informations will be stored in the database (insertReviewIntoDB())
 
'''       
        
def crawlData(driver, wait):  
    
    try:
        db = TinyDB('..\database\db.json', sort_keys=True, indent = 4)
        db.purge()
        restaurantTable = db.table('RESTAURANT TABLE')
        reviewTable = db.table('REVIEW TABLE')
        reviewPicturesTable = db.table('REVIEW PICTURE TABLE')
        
    except:
        print("Fehler beim Anlegen der Datenbank")
        printMsg("Fehler beim Anlegen der Datenbank")
             
    try:
        googlePlace = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div[2]/span[1]/span[1]/button'))).get_attribute("innerHTML")
    except:
        googlePlace = None
        print('Gefundener Ort ist kein Restaurant')  
        printMsg('Gefundener Ort ist kein Restaurant')   
    #if(googlePlace == None):
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
            """     
            print(restaurant_title)
            print(restaurant_stars)
            print(numberOfReviews)
            """
            printRestaurant(restaurant_title, restaurant_stars, str(numberOfReviews))
            
            
            try:
                numberOfReviewsButton.click()
            except:
                driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_class_name('section-reviewchart-right'))
                numberOfReviewsButton.click()
                    
            reviewDetailPage = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-header-title')))
            if reviewDetailPage.get_attribute("innerHTML") == 'Alle Rezensionen':
                # Crawl Comments
                
                reviewList = scrollOverAllReviews(driver, 0.1, wait, numberOfReviews)
                
                restaurant = Restaurant(restaurant_title, restaurant_stars, restaurant_rushHour , reviewList)
                
                insertReviewIntoDB(restaurant, restaurantTable, reviewTable, reviewPicturesTable)  
           
    else: 
            print('Gefundener Ort ist kein Restaurant')
            printMsg('Gefundener Ort ist kein Restaurant')


'''     
method to store data in the database including all Reviews, Pictures and main information of the restaurant
 
'''           
        
def insertReviewIntoDB(restaurant, restaurantTable, reviewTable, reviewPicturesTable):
    
    if not(checkForDuplicate('Restaurantname',restaurant.restaurant_title, restaurantTable)):
           
        restaurantTable.insert({'Restaurantname': restaurant.restaurant_title, 'Gesamtbewertung' : restaurant.restaurant_stars, 'Stosszeiten' : restaurant.rush_hours})    
    else:
        print("Restaurant wurde bereits in der Vergangenheit gecrawled")
        print("Update der Datenbank erfolgt!")     
        printMsg("Restaurant wurde bereits gecrawled. Datenbank wurde aktualisert.")  
        
    for i in range (0, len(restaurant.reviewList)):   
        if not(checkForDuplicate('User',restaurant.reviewList[i].userName, reviewTable)):       
            reviewTable.insert({'Restaurantname': restaurant.restaurant_title, 'User':  restaurant.reviewList[i].userName, 'Sterne':  restaurant.reviewList[i].reviewStars, 'Kommentar':  restaurant.reviewList[i].comment})
            if(restaurant.reviewList[i].pictures != None):
                for k in range (0, len(restaurant.reviewList[i].pictures)):
                    if("https" in restaurant.reviewList[i].pictures[k]):
                        reviewPicturesTable.insert({'User':  restaurant.reviewList[i].userName, 'BildURL':  restaurant.reviewList[i].pictures[k]})
       
'''     
wrapper method to check for duplicates in the database tables

''' 
        
def checkForDuplicate (dbfield, element, dbTable): 
           
    if(dbTable.contains((where(dbfield) == element))): 
        return True 
    else:
        return False   

'''     
method to scroll over all reviews and also safing the data to objects from the review class

''' 

def scrollOverAllReviews(driver, scroll_pause_time, wait, numberOfReviews):
    
    """
    print('Reviews:')
    print('')
    """
    reviewList = []
        
    for i in range(1, numberOfReviews):
    #for i in range(1, 50):    
        # google stops loading after 835 Reviews
        if(i >= 835):
            break
        else:    
            unknownIsPresent = False
            try:
                scrollElement = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[8]/div[' + str(i) + ']')))
            except Exception as err:
                print('Unbekanntes Element gefunden: Element wird übersprungen')
                printMsg('Unbekanntes Element gefunden: Element wird übersprungen')
                
                unknown = scrollElement.find_element_by_class_name('section-review-interaction-button')
                unknownIsPresent = True
                
            if(unknownIsPresent == True): 
                
                driver.execute_script("return arguments[0].scrollIntoView();", unknown)
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

                if(scrollElement.find_element_by_class_name('section-review-photos').get_attribute("style") != "display: none;"):
                    photoCount = len(scrollElement.find_element_by_class_name('section-review-photos').find_elements_by_tag_name("button"))
                    for j in range (0, photoCount):
                        photo = scrollElement.find_elements_by_class_name('section-review-photo')[j]
                        if(photo.find_element_by_class_name('section-review-photo-overlay').get_attribute("style") != "display: none;"):
                            photo.find_element_by_class_name('section-review-photo-overlay').click()
                        reviewPhotoList.append(photo.get_attribute("style")[21:])  
                else:
                    reviewPhotoList = None
                review = Review(userName, reviewStars, reviewText, reviewPhotoList)
                reviewList.append(review)
                
                printReview(review)
                
                """
                print('User: ' + review.userName)
                print('Sterne: ' + review.reviewStars)
                print('Comment: ' + review.comment)
                if(review.pictures != None):
                    print('PicturesCount: ' + str(len(review.pictures)))
                    for k in range (0, len(review.pictures)) :
                        print('Pictures' + review.pictures[k])
                print('---------------------------------------------------')
                """
                driver.execute_script("return arguments[0].scrollIntoView();", scrollElement)
            
                time.sleep(scroll_pause_time)
            
    return reviewList   


def startGUI():
    
    gui.title("Google Places Webcrawler") # Window title
    gui.geometry('440x729+0+0') # Window size and position

    # Parent Element Settings
    mainframe.grid(column=0, row=0, sticky=(N, W, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)
    
    # Variables
    city = 'München'
    guiInputValue = StringVar()

    # Text label
    ttk.Label(mainframe, text ='Über welches Restaurant in ' + city + ' wollen Sie Informationen erhalten?').grid(column=0, row=1, sticky=W)

    # Restaurant Input Box
    restaurantInput = ttk.Entry(mainframe, width=10, textvariable=guiInputValue)
    restaurantInput.grid(column=0, row=2, sticky=(W, E))

    # Output Message Text
    messageText.grid(column=0, row=3, sticky= W)
    
    # Start Webcrawler Button
    ttk.Button(mainframe, text='Start', command=lambda: main(guiInputValue.get(), city) ).grid(column=0, row=4, sticky=E)
    
    # Output Label RestaurantInfo
    ttk.Label(mainframe, text ='Restaurant Information:').grid(column=0, row=5, sticky=(W))
    
    # Output Textbox Restaurant meta-data    
    restaurantTextbox.grid(column=0, row=6, sticky=(W,E), padx = 10, pady = 10)

    # Output Label Reviews
    ttk.Label(mainframe, text ='Bewertungen:').grid(column=0, row=7, sticky=(W))
    
    # Output Textbox Reviews
    reviewTextbox.grid(column=0, row=8, sticky=W, padx = 10, pady = 10)

    scrollbarY = ttk.Scrollbar(mainframe, orient=VERTICAL, command=reviewTextbox.yview)
    scrollbarY.grid(column=1, row=8, sticky=(N,S))
    reviewTextbox['yscrollcommand'] = scrollbarY.set
   

    # Add padding to all child-elements of mainframe
    for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

    restaurantInput.focus()
    gui.bind('<Return>', lambda event: main(guiInputValue.get(), city))

    gui.mainloop() # Start GUI


def printMsg(msg):
    messageText['text'] = msg
    
    gui.update()


def printRestaurant(restaurant_title, restaurant_stars, numberOfReviews):
    restaurantTextbox.insert('end', 'Restaurant: ' + restaurant_title + '\n')
    restaurantTextbox.insert('end', 'Sterne: ' + restaurant_stars + '\n')
    restaurantTextbox.insert('end', 'Anzahl der Bewertungen: ' + numberOfReviews + '\n')
    
    gui.update()
    

def printReview(review):
    
    reviewTextbox.insert('end', 'User: ' + review.userName + '\n')
    reviewTextbox.insert('end', 'Sterne: ' + review.reviewStars + '\n')
    reviewTextbox.insert('end', ('Comment: ' + review.comment  + '\n').encode("utf-8", "ignore"))
    if(review.pictures != None):
        reviewTextbox.insert('end', 'PicturesCount: ' + str(len(review.pictures)) + '\n')
        for k in range (0, len(review.pictures)) :
            reviewTextbox.insert('end', 'Pictures' + review.pictures[k] + '\n')
    reviewTextbox.insert('end', '\n' + '------------------------------------------------' + '\n\n')
    reviewTextbox.see(END)
    
    gui.update()


def clearGUI():
    reviewTextbox.delete('1.0', END)
    restaurantTextbox.delete('1.0', 'end')
    messageText['text'] = ''

startGUI()

