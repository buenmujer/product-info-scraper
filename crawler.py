import urllib
import lxml.html
import time
import os
import constants

# Make a list of all the pages on the website with cat food on them (35 total, 
# 24 products on each page). Here I'm using the range function to add the 
# page increments to a base url.
url_list = ['{}{}'.format(constants.crawler_base_url, num) for num in range(0,840,24)]

def crawler(url_list):

    '''
    This function crawls the Pet Smart website, gathering urls to the product 
    information pages for cat food. The url list fed into it is a list of all 
    the pages from the website that result from the searh 'cat food' 
    (35 total, 24 products on each page).
    
    Input is the url list of pages with all of the products to browse.
    Output is a list of urls to each of those products.
    '''
    
    # On each of the pages fed in, gather all links, then filter for only 
    # those 24 with the products I want on them
    
    link_list = []
    
    #for url in url_list:
    for url in url_list:
        http = urllib.urlopen(url)
        time.sleep(constants.sleep) # This slows down the requests to lessen the chance of 
        # having my IP address blocked from the website
        links = lxml.html.fromstring(http.read())    

        # This filters all urls by selecting the url in href for the 'a' tags,
        # and returns only those with '/cat/food-and-health/food/' and 
        # '.html?cgid=' in them, which indicate the product pages.
        for link in links.xpath('//a/@href'): 
            if '/cat/food-and-health/food/' in link and '.html?cgid=' in link:
                link_list.append(link)
            
    # Combine product listings with base url to get full list of product urls
    full_product_list = ['{}{}'.format(new_crawler_base_url, product_link) \
    for product_link in link_list]
 
    return full_product_list

crawler()

#just to check while testing
print full_product_list[0:5]



def write_file(list):

    '''
    This function writes a file from input. Here I'm using it as a record in case I 
    get blocked from the website later. The input is the product url list from the 
    crawler function and the output is a .txt file of that list.
    '''
    
    filename = 'product_list_path' + product_urls.txt
    fh = open(filename, 'a')
    fh.write(str(full_product_list)) 
    fh.close()

#write_file(full_product_list)
