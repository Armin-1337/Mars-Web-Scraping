#!/usr/bin/env python
# coding: utf-8


from bs4 import BeautifulSoup
import time
import requests
import re
import pymongo
import pandas as pd
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist


def init_browser():
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=True, incognito=True)


def scrape_info():
    browser = init_browser()

    #Scrape Latest Mars news
    url_1 = 'https://mars.nasa.gov/news/'
    browser.visit(url_1)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    #Website lists a number of news items by the div "slide"
    #Target slide and grab the first instance for latest news
    slide = soup.find('li', class_='slide')
    news_title = slide.find('div', class_='content_title').text
    news_paragraph = slide.find('div', class_='article_teaser_body').text

    #Scrape Nasa Mars image of the day
    url_2 = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url_2)
    browser.click_link_by_partial_text('FULL IMAGE')
    #time.sleep(1)
    browser.click_link_by_partial_text('more info')
    #time.sleep(1)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    featured_image = soup.find('img', class_='main_image').attrs['src']

    featured_image_link = f"https://www.jpl.nasa.gov{featured_image}"
   

    #Scrape Twitter for latest mars weather report
    url_3='https://twitter.com/marswxreport?lang=en'
    
    browser.visit(url_3)
    #Need time to load twitter or else script may fail
    time.sleep(1)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")
    # First, find a tweet with the data-name `Mars Weather`
    tweet_attrs = {"class": "tweet", "data-name": "Mars Weather"}
    mars_weather_tweet = soup.find("div", attrs=tweet_attrs)
    # Next, search within the tweet for the p tag or span tag containing the tweet text
    # As Twitter is frequently making changes the try/except will identify the tweet
    # text using a regular expression pattern that includes the string 'sol' if there
    # is no p tag with a class of 'tweet-text'
    try:
        mars_weather = mars_weather_tweet.find("p", "tweet-text").get_text()

    except AttributeError:

        pattern = re.compile(r'sol')
        mars_weather = soup.find('span', text=pattern).text

    #Scrape Mars facts
    url_4 = 'https://space-facts.com/mars/'
    tables = pd.read_html(url_4)
    df = tables[0]
    mars_facts = df.to_html()

    #Scrape Mars Hemisphere images 
    url_5 = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    #html parser has its limits for more complicated functions, use lxml
    #To obtain an image for each hemisphere, will need to follow each hemisphere's url
    response=requests.get(url_5)
    py_soup=BeautifulSoup(response.text, 'lxml')
    items = py_soup.find("div", class_="collapsible results")
    #Script for preliminairy url finding
    # for a in items.find_all('a', href=True):
    #     print ("Found the URL:", a['href'])
    hemisphere_image_urls = []
    for a in items.find_all('a', href=True):
        hemisphere = {}
        Linku = ("https://astrogeology.usgs.gov"+ a['href'])
        browser.visit(Linku)
        #time.sleep(1)
        hemisphere['title'] = browser.find_by_css("h2.title").text
        picturelinku = browser.find_link_by_text('Sample')
        hemisphere['img_url'] = picturelinku['href']
        hemisphere_image_urls.append(hemisphere)
        #time.sleep(1)

    mars_data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image_key": featured_image_link,
        "mars_weather": mars_weather,
        "keymars_facts": mars_facts,
        "hemispheres": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data
