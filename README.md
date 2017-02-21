# pet-products-scraper
A web scraper used to build a product information database for use in animal health research. It was written to scrape the Pet Smart website.

**crawler.py** is a script that collects urls of product information pages from the Pet Smart website. This could be adapted to other websites by altering the base urls in constants.py

**scraper_pkl.py** is a script that takes the product information urls produced in crawler.py as input, scrapes the product information and exports the information from the function as a Pickle file. This can then be imported into a Pandas dataframe for cleaning. It will scrape: product name, product id, price, food type, life stage, health consideration, flavor, primary ingredient, package weight, ingredients and guranteed analysis.

**product_info_scraper.ipynb** in the notebooks folder shows the function in use in an iPython notebook with initial results. 

**constants.py** is a file that contains any information the user might want to change (base urls, sleep times, etc.)

**postgres_commands.txt** is a file that contains commands for setting up a Postgres table, viewing it, and deleting it from the Terminal on a Mac.
