from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
import pandas as pd
import time

# Open chromedriver
def init_browser():
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser = init_browser()

    # NASA (step 1) #############################
    NASA_url = 'https://mars.nasa.gov/news/'
    browser.visit(NASA_url)
    time.sleep(2)
    html = browser.html
    soup = bs(html, 'html.parser')
    news = soup.find_all('div', class_='list_text')
    news_titles_list = []
    news_paragraphs_list = []
    for news_item in news:
        news_title = news_item.find('div', class_='content_title').text
        news_titles_list.append(news_title)
        news_paragraph = news_item.find('div', class_='article_teaser_body').text
        news_paragraphs_list.append(news_paragraph)
    news_title = news_titles_list[0]
    news_p = news_paragraphs_list[0]

    time.sleep(1)

    # JPL Image (step 2) #############################
    JPL_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(JPL_url)
    browser.click_link_by_id('full_image')
    browser.click_link_by_partial_text('more info')
    image_html = browser.html
    JPL_image_soup = bs(image_html, 'html.parser')
    image = JPL_image_soup.body.find("figure", class_="lede")
    link = image.find('a')
    href = link['href']
    base_url='https://www.jpl.nasa.gov'
    featured_image_url = base_url + href

    time.sleep(1)

    # Mars Weather (step 3) #############################
    tweet_url  = 'https://twitter.com/marswxreport?lang=en'
    response = requests.get(tweet_url)
    soup = bs(response.text, 'lxml')
    mars_weather=soup.find('p', class_='TweetTextSize').text

    time.sleep(1)

    # Mars Facts (step 4) #############################
    facts_url = 'https://space-facts.com/mars/'
    tables = pd.read_html(facts_url)
    mars_df = tables[2]
    mars_df.columns = ['description', 'value']
    mars_df = mars_df.set_index('description')
    mars_facts_html = mars_df.to_html(justify='left')
  

    time.sleep(1)

    #Mars Hemispheres (step 5) #############################
    original_url = 'https://astrogeology.usgs.gov'
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    hemispheres_html = browser.html
    soup = bs(hemispheres_html, 'html.parser')
    all_mars_hemispheres = soup.find('div', class_='collapsible results')
    mars_hemispheres = all_mars_hemispheres.find_all('div', class_='item')
    hemisphere_image = []
    for i in mars_hemispheres:
        hemisphere = i.find('div', class_="description")
        title = hemisphere.h3.text        
        hemisphere_link = hemisphere.a["href"]    
        browser.visit(original_url + hemisphere_link)        
        image_html = browser.html
        image_soup = bs(image_html, 'html.parser')        
        image_link = image_soup.find('div', class_='downloads')
        image_url = image_link.find('li').a['href']
        image_dict = {}
        image_dict['title'] = title
        image_dict['img_url'] = image_url        
        hemisphere_image.append(image_dict)


    # Enter all items into dictionary for Flask
    mars_dict = {
            "news_title": news_title,
            "news_p": news_p,
            "featured_image_url": featured_image_url,
            "mars_weather": mars_weather,
            "fact_table": mars_facts_html,
            "hemispheres": hemisphere_image
    }

    

    browser.quit()
    return mars_dict





    







