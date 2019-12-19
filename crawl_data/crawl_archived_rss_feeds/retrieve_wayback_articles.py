'''
  retrieve the articles from the rss wayback links.
'''
import requests
from bs4 import BeautifulSoup
import time

#first, open the file of rss links.
skipto = 7000
upto = 8000
ctr = 0
with open('./rss_wayback_links.txt') as f:
    for link in f:
        ctr += 1
        if skipto and (ctr < skipto):
            continue
        if upto and (ctr >= upto):
            break

        #each link takes up one line...
        print(ctr)
        print(link)
        time.sleep(15)
        resp = requests.get(link)
        soup = BeautifulSoup(resp.content, "lxml")

        if (ctr % 1000) == 1:
            #print(soup.findAll("item")[0])
            print(soup)

        #save the result to a file.
        ## example: https://web.archive.org/web/20191116073115/https://www.cnbc.com/id/19206666/device/rss/rss.html
        timestamp = link.split('/https:')[0].split('/')[-1]
        date = timestamp[:8]
        fname = str(ctr) + '_rss_' + date
        with open('./archived_rss_2/'+fname,'wb') as outfile:
            html = soup.prettify("utf-8")
            outfile.write(html)

        '''
        html = soup.prettify("utf-8")
        with open("output1.html", "wb") as file:
            file.write(html)
        '''


#then do a python get request for each of the links.
# save the links in a safe place.
