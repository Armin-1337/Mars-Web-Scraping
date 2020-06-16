#!/usr/bin/env python
# coding: utf-8


from bs4 import BeautifulSoup
import time
import requests
import pymongo
import pandas as pd
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist

def init_browser():
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=True)


def scrape_info():
    browser = init_browser()

    #Scrape news title and paragraph
    url_1 = 'https://mars.nasa.gov/news/'
    browser.visit(url_1)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    #gotta narrow search down to "slide" div first
    slide = soup.find('li', class_='slide')
    news_title = slide.find('div', class_='content_title').text
    news_paragraph = slide.find('div', class_='article_teaser_body').text

    #Scrape image and image url
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
   

    #Scrape weather
    #Using requests since chromedriver is garbo for twitter
    url_3='https://twitter.com/marswxreport?lang=en'
    response=requests.get(url_3)
    #set up parser
    twitter_soup=BeautifulSoup(response.text, 'lxml')
    # #Tweets are organized by div classes called 'tweet'
    # soup.find_all('div', class_="tweet")[2]
    #pick out attributes specific to mars weather, most recent will be the first result
    mars_weather_tweet = twitter_soup.find("div", attrs={"class": "tweet", "data-name": "Mars Weather"})
    mars_weather=mars_weather_tweet.find('div', class_='js-tweet-text-container').p.text

    # Mars facts
    url_4 = 'https://space-facts.com/mars/'
    tables = pd.read_html(url_4)
    df = tables[0]
    mars_facts = df.to_html()

    #Mars Hemisphere 
    url_5 = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url_5)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    response=requests.get(url_5)
    #set up parser
    py_soup=BeautifulSoup(response.text, 'lxml')
    items = py_soup.find("div", class_="collapsible results")
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
        "hemispheres": hemisphere_image_urls,
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data





