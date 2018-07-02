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
    
    clearGUI() 
	#starts the browser and navigates to the google place
    navigateToRestaurantDetailPage(restaurantName, city)
	#prints messages to the GUI after the restaurant is crawled succesfully
    printMsg(restaurantName + " wurde erfolgreich gecrawled!")

'''     
method to navigate to the Google Place
validates if the place is a restaurant and uses the method crawlData() to safe the data 
 
'''
def navigateToRestaurantDetailPage(restaurantName , city):
        
    url = 'https://www.google.de/maps/search/' + restaurantName + '/@48.151241,11.4996846,12z'
    print(url)
    printMsg('URL wird in Google Chrome aufgerufen...')     
    
    #chrome driver config (dimension)
    driver = webdriver.Chrome(executable_path='..\..\driver\chromedriver.exe')
    driver.set_window_position(450, 0)
    driver.set_window_size(1024, 768)
    #starts chrome driver and opens the url
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    #check for so google popup elements and try to close it
    try:
        googleElement = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="consent-bump"]/div/div[2]/span/button[1]')))
        if(googleElement):
            googleElement.click()
    finally:        
    
    #checks for results and choose the first result as restaurant    
        try:  
            present = False
            try:
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-hero-header-description')))
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
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-hero-header-description'))) 
                                    
        except Exception as err:
            print('Es wurde kein Ergebniss für das Restaurant: ' + restaurantName + ' gefunden.')
            printMsg('Es wurde kein Ergebniss für ' + restaurantName + ' gefunden.')
            #closes the chrome driver 
            driver.close()
        #crawls all restaurant data                  
        crawlData(driver, wait)
 
'''     
method to crawl the data with selenium and safe the restaurant data to objects from class restaurant.
After saving the data, the informations will be stored in the database (insertReviewIntoDB())
 
'''       
        
def crawlData(driver, wait):  
    #creates database and tables
    try:
        db = TinyDB('..\database\db.json', sort_keys=True, indent = 4)
        db.purge()
        restaurantTable = db.table('RESTAURANT TABLE')
        reviewTable = db.table('REVIEW TABLE')
        reviewPicturesTable = db.table('REVIEW PICTURE TABLE')
        
    except:
        print("Fehler beim Anlegen der Datenbank")
        printMsg("Fehler beim Anlegen der Datenbank")
        
    #checks for restaurant         
    try:
        googlePlace = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[1]/div[3]/div[2]/div/div[2]/span[1]/span[1]/button'))).get_attribute("innerHTML")
    except:
        googlePlace = None
        print('Gefundener Ort ist kein Restaurant')  
        printMsg('Gefundener Ort ist kein Restaurant')   
    
    #crawling data and saves restaurant_title, restaurant_stars and restaurant_rushHour
    if('Restaurant' in googlePlace or 'restaurant' in googlePlace):
        
            restaurant_title = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-hero-header-title'))).get_attribute("innerHTML")
            restaurant_stars = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-star-display'))).get_attribute("innerHTML")
            # get all hour elements out of the rushhour chart 
            workload = []
            days = driver.find_elements_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[14]/div[2]/div')
            maxWorkloadAtDays = {}
            for j in range (0, len(days)):
                hours = days[j].find_elements_by_class_name('section-popular-times-bar')
                
                for i in range (0, len(hours)): 
                    
                    string = hours[i].get_attribute('aria-label')
                    if not  (re.findall('([0-9]*)', string) == ""):
                        workload.append((re.findall('([0-9]*)', string[10:])))
                #get maximum workload for each day      
                maxWorkloadAtDays[j] = max(workload)
                
               
            #get the day of the maximum workload of the restaurant and save it to the rushHour variable
            if (len(maxWorkloadAtDays) == 0):
                restaurant_rushHour = 'Keine Stosszeit gefunden'
            else:
                restaurant_rushHour = getRushHourDay(max(maxWorkloadAtDays)) + 's'
            numberOfReviewsButton = driver.find_element_by_class_name('section-reviewchart-numreviews')
            numberOfReviews = numberOfReviewsButton.get_attribute("innerHTML")[0:-9]
            #saves number of reviews 
            if('.' in numberOfReviews):
                numberOfReviews = int(numberOfReviews.replace('.', ''))
            else:
                numberOfReviews = int(numberOfReviews)
            #prints restaurant information to the GUI
            printRestaurant(restaurant_title, restaurant_stars, str(numberOfReviews), restaurant_rushHour)
            
            
            try:
                #clicks on the review button
                numberOfReviewsButton.click()
            except:
                #scrolls to the review button and clicks
                driver.execute_script("return arguments[0].scrollIntoView();", driver.find_element_by_class_name('section-reviewchart-right'))
                numberOfReviewsButton.click()
                    
            reviewDetailPage = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'section-header-title')))
            if reviewDetailPage.get_attribute("innerHTML") == 'Alle Rezensionen':
                #scroll over all reviews and crawl all data
                reviewList = scrollOverAllReviews(driver, 0.1, wait, numberOfReviews)
                #saves all data to the restaurant object
                restaurant = Restaurant(restaurant_title, restaurant_stars, restaurant_rushHour , reviewList)
                #inserts all restaurant data into the database
                insertReviewIntoDB(restaurant, restaurantTable, reviewTable, reviewPicturesTable)  
           
    else: 
            print('Gefundener Ort ist kein Restaurant')
            printMsg('Gefundener Ort ist kein Restaurant')

            
            '''     
method to get the day of the week where most visitors are in the restaurant
 
'''           
def getRushHourDay(maxWorkloadAtDays):    
    
    #switch case to select a day 
    switcher = {
        0: "Montag",
        1: "Dienstag",
        2: "Mittwoch",
        3: "Donnerstag",
        4: "Freitag",
        5: "Samstag",
        6: "Sonntag"
    }
    return switcher.get(maxWorkloadAtDays) 

'''     
method to store data in the database including all Reviews, Pictures and main information of the restaurant
 
'''           
        
def insertReviewIntoDB(restaurant, restaurantTable, reviewTable, reviewPicturesTable):
    
    #checks for duplicate in the restaurant table
    if not(checkForDuplicate('Restaurantname',restaurant.restaurant_title, restaurantTable)):
        #inserts the restaurant, the rating and the rush hour into the restaurant table   
        restaurantTable.insert({'Restaurantname': restaurant.restaurant_title, 'Gesamtbewertung' : restaurant.restaurant_stars, 'Stosszeiten' : restaurant.rush_hours})    
    else:
        print("Restaurant wurde bereits in der Vergangenheit gecrawled")
        print("Update der Datenbank erfolgt!")     
        printMsg("Restaurant wurde bereits gecrawled. Datenbank wurde aktualisert.")  
        
    for i in range (0, len(restaurant.reviewList)):   
        #checks for duplicate in the user table
        if not(checkForDuplicate('User',restaurant.reviewList[i].userName, reviewTable)): 
            #inserts the restaurant name, the user and all the review information into the review table      
            reviewTable.insert({'Restaurantname': restaurant.restaurant_title, 'User':  restaurant.reviewList[i].userName, 'Sterne':  restaurant.reviewList[i].reviewStars, 'Kommentar':  restaurant.reviewList[i].comment})
            #checks if review includes pictures
            if(restaurant.reviewList[i].pictures != None):
                for k in range (0, len(restaurant.reviewList[i].pictures)):
                    if("https" in restaurant.reviewList[i].pictures[k]):
                        #inserts the user name and the pictures into the pictures table
                        reviewPicturesTable.insert({'User':  restaurant.reviewList[i].userName, 'BildURL':  restaurant.reviewList[i].pictures[k]})
       
'''     
wrapper method to check for duplicates in the database tables

''' 
        
def checkForDuplicate (dbfield, element, dbTable): 
    #searches the element and returns true or false if the element is already in the database       
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
        #google stops loading after 835 Reviews
        if(i >= 835):
            break
        else:
            #checks for unknown elements and tries to skip it     
            unknownIsPresent = False
            try:
                scrollElement = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[8]/div[' + str(i) + ']')))
            except Exception as err:
                print('Unbekanntes Element gefunden: Element wird übersprungen')
                printMsg('Unbekanntes Element gefunden: Element wird übersprungen')
                
                unknown = scrollElement.find_element_by_class_name('section-review-interaction-button')
                unknownIsPresent = True
                
            if(unknownIsPresent == True): 
                #scrolls over the unkown element
                driver.execute_script("return arguments[0].scrollIntoView();", unknown)
                time.sleep(scroll_pause_time) 

            else:
                #crawls the user name
                userName = scrollElement.find_element_by_class_name('section-review-title').get_attribute("innerText")
                # checks for an expand button in the review 
                expandButtonIsPresent = False
                try:
                    
                    expandReviewButton = scrollElement.find_element_by_css_selector('button.section-expand-review.blue-link')
                    
                    if(expandReviewButton.get_attribute("style") != "display: none;"):
                                            
                        expandButtonIsPresent = True
                except:
                    
                    expandButtonIsPresent = False
                    
                if(expandButtonIsPresent == True):
                    #tries to click the review expand button
                    expandReviewButton.click()
                #crawls the review text, the review stars and the pictures
                reviewText = scrollElement.find_element_by_class_name('section-review-text').get_attribute("innerText")
                reviewStars = scrollElement.find_element_by_class_name('section-review-stars').get_attribute("aria-label")
                reviewPhotoList = []
                #checks for pictures and saves it to the photoList
                if(scrollElement.find_element_by_class_name('section-review-photos').get_attribute("style") != "display: none;"):
                    photoCount = len(scrollElement.find_element_by_class_name('section-review-photos').find_elements_by_tag_name("button"))
                    for j in range (0, photoCount):
                        photo = scrollElement.find_elements_by_class_name('section-review-photo')[j]
                        if(photo.find_element_by_class_name('section-review-photo-overlay').get_attribute("style") != "display: none;"):
                            photo.find_element_by_class_name('section-review-photo-overlay').click()
                        reviewPhotoList.append(photo.get_attribute("style")[21:])  
                else:
                    reviewPhotoList = None
                
                #saves all review data to the review object    
                review = Review(userName, reviewStars, reviewText, reviewPhotoList)
                #append the review to all reviews 
                reviewList.append(review)
                #print review to the GUI
                printReview(review)
                
                #scrolls to the next review in the review list
                driver.execute_script("return arguments[0].scrollIntoView();", scrollElement)
                time.sleep(scroll_pause_time)
            
    return reviewList   

'''     
method to start the GUI

'''

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

'''     
method to print messages to the GUI

'''

def printMsg(msg):
    messageText['text'] = msg
    
    gui.update()

'''     
method to print main information of the restaurant to the GUI

'''

def printRestaurant(restaurant_title, restaurant_stars, numberOfReviews, restaurant_rushHour):
    restaurantTextbox.insert('end', 'Restaurant: ' + restaurant_title + '\n')
    restaurantTextbox.insert('end', 'Sterne: ' + restaurant_stars + '\n')
    restaurantTextbox.insert('end', 'Stoßzeiten: ' + restaurant_rushHour + '\n')
    restaurantTextbox.insert('end', 'Anzahl der Bewertungen: ' + numberOfReviews + '\n')
    
    gui.update()

'''     
method to print informations of a review to the GUI

'''    

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

'''     
method to clear the GUI

'''  
def clearGUI():
    reviewTextbox.delete('1.0', END)
    restaurantTextbox.delete('1.0', 'end')
    messageText['text'] = ''

#start the program
startGUI()

