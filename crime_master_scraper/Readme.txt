This scraper scrapes all webpages that belong to the same domain as that of the input url.

###Scrapy basic steps###

Run "scrapy startproject <project_name>"" to start a project

To start scraping, execute 'scrapy crawl crime_master -a start_url=<start_url> -o <filename.csv> -t csv'
Provide appropriate start_url and output filename in the above command.

A step-by-step tutorial for creating and executing a scrapy project can be found at http://mherman.org/blog/2012/11/05/scraping-web-pages-with-scrapy/