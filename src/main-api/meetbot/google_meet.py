from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import time

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)

class GoogleMeet():
    def __init__(self,Username,Pass,executable_path,link):
        self.Username = Username
        self.Pass = Pass
        self.executable_path = executable_path
        self.link = link
        
        self.driver = webdriver.Chrome(executable_path=executable_path, chrome_options=chrome_options)  

    def login(self):
        self.driver.get("")
        
    def join_meeting(self):
        self.driver.get(self.link)
        
    def scrape_caption(self):
        #scrape caption
        pass    
        
    def scrape_participants(self):
        #scrape participants
        pass
    
    def scrape_chat(self):
        #scrape chat
        pass
        
    def record_meeting(self):
        #click on record button
        pass
    
    def leave_meeting(self):
        self.driver.close()