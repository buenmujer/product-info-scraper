import urllib 
import lxml.html
from bs4 import BeautifulSoup 
import time
import os
import constants
import pandas as pd
import psycopg2
import re

def scrape_product_info(product_list):
    
    '''
    This function scrapes the Pet Smart website to isolate information
    into separate variables from the url passed to it. 
    Because the html markers on this site are a bit unstable, the 
    data needs to be cleaned up before putting it into 
    a database. The function exports the information to a pickle file.
    The pickle file can be then imported as a dataframe,
    cleaned up, and finally stored into a database.
       
    Input:
    A list of urls of pet food product pages generated from crawler.py
       
    Output:
    
    product_df.pkl
    name(str), productID(int), price(str), food_type(str), life_stage(str), 
    health_consideration(str), flavor(str),primary_ingredient(str), url(str)
    package_weight(str) 
    
    nutrition_df.pkl
    name(str), productID(int), url(str), a set of columns iterated from the 
    "Guaranteed Analysis" portion of the product page, which lists things like 
    %protein and % moisture.
    
    ingredient_df.pkl
    name(str), productID(int), url(str), ingredient_list(str) and 
    ingredient_list2(str)
    
    Error tracking: returns 3 lists of urls that indicate which urls failed 
    while accessing the website or while scraping the ingredients or 
    nutritional analysis information (the most unstable).
    '''
    
    #Error tracking
    failed_url = []
    ingredients_url = []
    nutrition_url = []
    
    #Data
    dictionary_list = []
    nutrition_dict_list = []
    ingredient_dict_list = []
    
    #Open product pages from the product url list created from the  crawler 
    #function 
    for url in product_list:
        dict = {}  
        ingredient_dict = {}
        nutrition_dict = {}
        
        try:     
            # Open each url, turn each page into a Beautiful Soup object
            r = urllib.urlopen(url)
            soup_page = BeautifulSoup(r, 'lxml') #'html.parser'
        except:
            print "Error getting page" 
            failed_url.append(url)
        
        #check HTTP status codes while running (200 is good)
        print urllib.urlopen(url).getcode()
            
        #Isolate each variable of interest from the web page using the Beautiful
        #Soup tags, put them in the dictionary.         
        try:           
            name_box = soup_page.find('div', attrs={'class': 'product-name'})
            dict['name'] = name_box.get_text().strip()             
        except:
            dict['name'] = '' 
        try:
            prodID_box = soup_page.find('span', attrs={'class': 'productID'})       
            dict['product_id'] = prodID_box.get_text()   
        except:
            dict['product_id'] =''
        try:
            price_box = soup_page.find('span', attrs={'class': 'price-regular'})
            dict['price'] = price_box.get_text()
        except:
            dict['price']=''
        try:
            type_box = soup_page.find('div', attrs={'class': 'tab-content'})
            dict['food_type'] = type_box.find_all('b')[0].next_sibling 
        except:
            dict['food_type']=''
        try:
            dict['life_stage'] = type_box.find_all('b')[1].next_sibling
        except:
            dict['life_stage'] = ''
        try:
            dict['health_consideration'] = type_box.find_all('b')[2].next_sibling
        except:
            dict['health_consideration'] = ''
        try:
            dict['flavor'] = type_box.find_all('b')[3].next_sibling
        except:
            dict['flavor'] = ''
        try:
            dict['primary_ingredient'] = type_box.find_all('b')[4].next_sibling
        except:
            dict['primary_ingredient'] = ''
        try:
            dict['package_weight'] = type_box.find_all('b')[5].next_sibling.strip()
        except:
            dict['package_weight'] = ''                      
        try:
            dict['url']=url
        except:
            dict['url']=''
            
        #append all keys:values to dictionary list
        dictionary_list.append(dict)
                
    ###put ingredients into a separate list of dataframe to be parsed later
       
        try:        
            name_box = soup_page.find('div', attrs={'class': 'product-name'})
            prodID_box = soup_page.find('span', attrs={'class': 'productID'})        
            ingredient_dict['name'] = name_box.get_text().strip()  
            ingredient_dict['product_id'] = prodID_box.get_text()
            ingredient_dict['url']=url
        except:
            pass               
        try:
            type_box = soup_page.find('div', attrs={'class': 'tab-content'})
            ingredient_dict['ingredients'] = type_box.find_all('b')[6].next_sibling                    
        except:
            ingredient_dict['ingredients'] = ''
            ingredients_url.append(url)
            pass
        try:
            type_box = soup_page.find('div', attrs={'class': 'tab-content'})
            ingredient_dict['ingredients2'] = type_box.find_all('b')[7].next_sibling                    
        except (IndexError, TypeError):
            pass
        
        ingredient_dict_list.append(ingredient_dict) 
        
    #put all nutrition information into its own dataframe. 

        try:        
            name_box = soup_page.find('div', attrs={'class': 'product-name'})
            prodID_box = soup_page.find('span', attrs={'class': 'productID'})        
            nutrition_dict['name'] = name_box.get_text().strip()  
            nutrition_dict['product_id'] = prodID_box.get_text()
            nutrition_dict['url']=url
        except:
            pass               

        try:  
            type_box = soup_page.find('div', attrs={'class': 'tab-content'})
            tag = type_box.findAll('p')[1].next_sibling
            tag_s = str(tag)
            new = tag_s.split("<br/>")
            for i, line in enumerate(new):
                nutrition_dict[i]= re.findall("\)\s*(.*?)\s*%", line) 
        except:
            nutrition_url.append(url)
                        
        try:
            type_box = soup_page.find('div', attrs={'class': 'tab-content'})
            tag2 = type_box.findAll('p')[2].next_sibling
            tag_s2 = str(tag2)
            new2 = tag_s2.split("<br/>")
            for i, line in enumerate(new2):
                nutrition_dict[i]= re.findall("\)\s*(.*?)\s*%", line)             
        except (IndexError, TypeError):
            pass
        
        #append all keys:values to nutrition dictionary list
        nutrition_dict_list.append(nutrition_dict)   
    
    #turn dictionary lists into a dataframes    
    df = pd.DataFrame(dictionary_list) 
    nutrition_df = pd.DataFrame(nutrition_dict_list) 
    ingredient_df = pd.DataFrame(ingredient_dict_list)

    #export the dataframe from the function as a pickle file to access later
    df.to_pickle('product_df.pkl')
    nutrition_df.to_pickle('nutrition_df.pkl')
    ingredient_df.to_pickle('ingredient_df.pkl')
                  
    return failed_url, ingredients_url, nutrition_url, nutrition_dict_list, \
           ingredient_dict_list, dictionary_list

scrape_product_info(constants.product_urls)  