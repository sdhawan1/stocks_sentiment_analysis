#! /bin/bash

for URL in $(cat ./rsslinks.txt) ; do
  echo $URL
  waybackpack $URL --list >> ./rss_wayback_links.txt
done
#waybackpack https://www.cnbc.com/rss-feeds/ -d ./archived_rss --to-date 2018

#after this we need to use python to crawl the links in that output file.
