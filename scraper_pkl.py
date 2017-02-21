import urllib 
import lxml.html
from bs4 import BeautifulSoup 
import time
import os
import constants
import pandas as pd
import psycopg2
import re

def product_info(product_list):
    """
    This function scrapes the Pet Smart website to isolate information
    into separate variables from the url passed to it and exports the 
    information to a pickle file. The pickle file can be imported as a 
    dataframe, cleaned up, then stored into a database.

    Input:
    A list of urls of pet food product pages generated from crawler.py

    Output:

    nutrition_df.pkl
    name(str), productID(int), price(str), food_type(str), life_stage(str), 
    health_consideration(str), flavor(str),primary_ingredient(str), url(str)
    package_weight(str), , ingredient_list(str) and a set of columns iterated 
    from the "Guaranteed Analysis" portion of the product page, which lists 
    things like %protein and % moisture."""

    nutrition_dict_list = []
    def nutrition_regex(tag_list, nutrition_dict):

        """This function goes to the Guaranteed Analysis portion of the page
           and isolates the percentage of each nutritional component listed
           into it's appropriate key.
           
           Input: a list of sections of the webpage to search and the 
           dictionary to store the information in that is defined below.
           
           Output: Key: Value pairs listing the percentage of each 
           nutritional component. Values are percentages. These get added
           to the dictionary of product information defined in the overall
           function."""

        for tag in tag_list:
            if "Guaranteed Analysis" in tag:
                new = tag.split("<br/>")  
                for i, line in enumerate(new):
                    if "Crude Protein (min" in line:
                        nutrition_dict['crude_protein_min']= \
                        re.findall("\)\s*(.*?)\s*%", line) 
                    elif "Crude Protein (max" in line:
                        nutrition_dict['crude_protein_max']= \
                        re.findall("\)\s*(.*?)\s*%", line)
                    elif "Crude Fat (min" in line:
                        nutrition_dict['crude_fat_min']= \
                        re.findall("\)\s*(.*?)\s*%", line) 
                    elif "Crude Fat (max" in line:
                        nutrition_dict['crude_fat_max']= \
                        re.findall("\)\s*(.*?)\s*%", line) 
                    elif "Crude Fiber (min" in line:
                        nutrition_dict['crude_fiber_min']= \
                        re.findall("\)\s*(.*?)\s*%", line) 
                    elif "Crude Fiber (max" in line:
                        nutrition_dict['crude_fiber_max']= \
                        re.findall("\)\s*(.*?)\s*%", line) 
                    elif "Moisture (min" in line:
                        nutrition_dict['moisture_min']= \
                        re.findall("\)\s*(.*?)\s*%", line) 
                    elif "Moisture (max" in line:
                        nutrition_dict['moisture_max']= \
                        re.findall("\)\s*(.*?)\s*%", line) 
                    elif "Ash (min" in line:
                        nutrition_dict['ash_min']= \
                        re.findall("\)\s*(.*?)\s*%", line) 
                    elif "Ash (max" in line:
                        nutrition_dict['ash_max']= \
                        re.findall("\)\s*(.*?)\s*%", line) 
                    elif "Taurine (min" in line:
                        nutrition_dict['taurine_min']= \
                        re.findall("\)\s*(.*?)\s*%", line) 
                    elif "Taurine (max" in line:
                        nutrition_dict['taurine_max']= \
                        re.findall("\)\s*(.*?)\s*%", line) 
                    else:                        
                        nutrition_dict['tag'] = None
            else:
                None
        return nutrition_dict

    #Open product pages from the product url list created from the 
    #crawler function
    for url in product_list: 

        nutrition_dict = {}
        try:
        # Open each url, turn each page into a Beautiful Soup object
            r = urllib.urlopen(url)
            soup_page = BeautifulSoup(r, 'lxml') #'html.parser'
        except:
            print "Error getting page" 

        #check HTTP status codes while running (200 is good)
        print urllib.urlopen(url).getcode()

        try:        
            name_box = soup_page.find('div', attrs={'class': 'product-name'})
            prodID_box = soup_page.find('span', attrs={'class': 'productID'})
            nutrition_dict['name'] = name_box.get_text().strip()  
            nutrition_dict['product_id'] = prodID_box.get_text()
        except:
            pass   

        try:
            price_box = soup_page.find('span', attrs={'class': 'price-regular'})
            nutrition_dict['price'] = price_box.get_text()
        except:
            nutrition_dict['price']=''
        try:
            nutrition_dict['url']=url
        except:
            nutrition_dict['url']=''

        #This section defines the places interesting variables could be.
        #The html is messy, so I will define all the "b" tags and 
        #iterate through them below.

        type_box = soup_page.find('div', attrs={'class': 'tab-content'})

        try:
            zero = type_box.find_all('b')[0]
        except:
            zero =  ''
        try:
            one = type_box.find_all('b')[1]
        except:
            one = ''
        try:
            two = type_box.find_all('b')[2]
        except:
            two = ''
        try:
            three = type_box.find_all('b')[3]
        except:
            three = ''
        try:
            four = type_box.find_all('b')[4]
        except:
            four = ''
        try:
            five = type_box.find_all('b')[5]
        except:
            five = ''
        try:
            six = type_box.find_all('b')[6]
        except:
            six = ''
        try:
            seven = type_box.find_all('b')[7]
        except:
            seven = ''
        try:
            eight = type_box.find_all('b')[8]
        except:
            eight = ''
        try:
            nine = type_box.find_all('b')[9]
        except:
            nine = ''

        #Make a list of the variables
        info_list = [zero, one, two, three, four, five, six,
                     seven, eight, nine] 

        #Iterate through the list to find where the information is
        #and put it into its appropriate key.
        for info in info_list:           
            if "Ingredients:" in info:  
                nutrition_dict['ingredients'] = info.next_sibling
            elif 'Food Type:' in info:
                nutrition_dict['food_type'] = info.next_sibling.strip()
            elif 'Life Stage:' in info:
                nutrition_dict['life_stage'] = info.next_sibling.strip()
            elif 'Health Consideration:' in info:
                nutrition_dict['health_consideration'] = \
                info.next_sibling.strip() 
            elif 'Flavor:' in info:
                nutrition_dict['flavor'] = info.next_sibling.strip() 
            elif 'Primary Ingredient:' in info:
                nutrition_dict['primary_ingredient'] = info.next_sibling
            elif 'Package Weight:' in info:
                nutrition_dict['package_weight'] = info.next_sibling.strip()
            else:
                None

        #This section defines the places "Guaranteed Analysis" could be.
        #The html is messy, so I will look in several places, and parse
        #through it using the nutrition_regex function above (called below).
        try:
            tag0 = str(type_box.findAll('p')[0].next_sibling).strip()
        except:
            tag0 = '' 
        try:
            tag1 = str(type_box.findAll('p')[1].next_sibling).strip()
        except:
            tag1 = ''       
        try:
            tag2 = str(type_box.findAll('p')[2].next_sibling).strip()
        except:
            tag2 = ''     
        try:
            tag3 = str(type_box.findAll('p')[3].next_sibling).strip()
        except:
            tag3 = ''
        try:
            tag4 = str(type_box.findAll('p')[4].next_sibling).strip()
        except:
            tag4 = ''

        #Make a list of the variables
        tag_list = [tag0, tag1, tag2, tag3, tag4]               

        #This calls the nutritional information parser from above,
        #feeding in the list of places to look on the page (tags)
        #for the nutritional information
        nutrition_dict = nutrition_regex(tag_list, nutrition_dict)   

        #append all keys:values to nutrition dictionary list
        nutrition_dict_list.append(nutrition_dict)    

    #turn dictionary list into a dataframes    
    nutrition_df = pd.DataFrame(nutrition_dict_list) 

    #export the dataframe from the function as a pickle file to access later
    nutrition_df.to_pickle('product_info_df.pkl')

    return nutrition_dict_list

product_info(constants.product_urls) 