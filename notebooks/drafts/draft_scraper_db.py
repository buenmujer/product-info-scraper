import urllib 
import lxml.html
from bs4 import BeautifulSoup 
import time
import os
import constants
import pandas as pd
import psycopg2

#Define DB and User names, imported from constants file
dbname = constants.dbname
username = constants.username

def scrape_product_info(product_list):
      
    '''
    This function scrapes the Pet Smart website to isolate information
    into separate variables from the url passed to it and stores
    the variables into a Postgres database.
       
    Input:
    A list of urls of pet food product pages generated from crawler.py
       
    Output:
    name(str), productID(int), price(str), food_type(str), life_stage(str), 
    health_consideration(str), flavor(str),primary_ingredient(str), 
    package_weight(str), ingredient_list(str) and ingredient_list2(str)
    
    Error tracking: returns 3 lists of urls that indicate which urls failed 
    while accessing the website, scraping the data, or storing the data into
    the database.
    '''

    #Connect to the Postgres database:
    con = None
    con = psycopg2.connect(database = dbname, user = username)

    #Initialize empty lists to help track where errors occur
    failed_url = []
    failed_scrape = []
    failed_db = []

    #Open product pages from the product url list created from the  crawler function 
    for url in product_list:
        
        try:     
            # Open each url, turn each page into a Beautiful Soup object
            r = urllib.urlopen(url)
            soup_page = BeautifulSoup(r, 'lxml') #'html.parser'

        except:
            print "Error getting page" 
            failed_url.append(url)
            
        #Isolate each variable of interest from the web page using the Beautiful
        #Soup tags:        
        try:
            #Name
            name_box = soup_page.find('div', attrs={'class': 'product-name'})
            name = name_box.get_text()  
        
            #Product ID
            prodID_box = soup_page.find('span', attrs={'class': 'productID'}) 
            product_id = prodID_box.get_text()

            #Price
            price_box = soup_page.find('span', attrs={'class': 'price-regular'})
            price = price_box.get_text()

            #several product attributes are held in this class
            type_box = soup_page.find('div', attrs={'class': 'tab-content'})

            #To do here: edit this so it iterates through a list rather than 
            #writing out all of them.

            #Food Type
            food_type = type_box.find_all('b')[0].next_sibling 
        
            #Life Stage
            life_stage = type_box.find_all('b')[1].next_sibling
        
            #Health Consideration
            health_consideration = type_box.find_all('b')[2].next_sibling
        
            #Flavor    
            flavor = type_box.find_all('b')[3].next_sibling
        
            #Primary Ingredient
            primary_ingredient = type_box.find_all('b')[4].next_sibling
        
            #Package Weight
            package_weight = type_box.find_all('b')[5].next_sibling
        
            #Ingredient List
            ingredients = type_box.find_all('b')[6].next_sibling
        
            #Ingredient List2 - sometimes the html tags move around here
            ingredients2 = type_box.find_all('b')[7].next_sibling
        
        except:
            failed_scrape.append(url)
      
        #add the variables to a Postgres database
        try: 
            # Insert the variables into the pet food table
            cur = con.cursor()
            SQL = """INSERT INTO 
            cat_food_petSmart (name, product_id, price, food_type, 
            life_stage, health_consideration, flavor, primary_ingredient, 
            package_weight, ingredients, ingredients2) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            data = (name, product_id, price, food_type, life_stage, 
                    health_consideration, flavor, primary_ingredient, 
                    package_weight, ingredients, ingredients2)
            cur.execute(SQL, data)  
            con.commit()
        except:
            print "db step didn't work"
            failed_db.append(url) 
            
    return failed_url, failed_scrape, failed_db

scrape_product_info(constants.test_product_list5)