import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import csv
import time
import os
import requests
from scrapy import Request


class AHRecipeSpider(scrapy.Spider):
    name = 'Recipe'
    start_urls = []

    custom_settings = {
        'DOWNLOAD_DELAY': 1,  # Add a delay between requests to avoid rate limiting
        'CONCURRENT_REQUESTS': 1,  # Limit concurrent requests to avoid being blocked
        'USER_AGENTS': [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15'
            # Add more user-agents here for rotation
        ],
    }

    def __init__(self, urls=None, *args, **kwargs):
        super(AHRecipeSpider, self).__init__(*args, **kwargs)
        if urls:
            self.start_urls = urls

        # Delete existing recipes.csv file if it exists
        if os.path.exists('recipes.csv'):
            os.remove('recipes.csv')

        self.csv_file = open('recipes.csv', 'a', newline='', encoding='utf-8')
        self.csv_writer = csv.writer(self.csv_file, delimiter=';')

    def parse(self, response):
        recipe_title = response.xpath(
            '//*[@id="start-of-content"]/div/div[1]/div[1]/div/div/div/div/div[2]/div/div[3]/h1/text()').get()
        if recipe_title:
            recipe_title = recipe_title.strip()
        energy = response.xpath(
            '//*[@id="start-of-content"]/div/div[1]/div[1]/div/div/div/div/div[2]/div/div[3]/div[2]/div/text()').get()
        try:
            carbs_value = response.xpath('//*[@id="recipe-footer"]/div[2]/div/div[3]/div[1]/span[2]/text()').get()
            carbs_value2 = carbs_value + ' gram'
            protein_value = response.xpath('//*[@id="recipe-footer"]/div[2]/div/div[5]/div/span[2]/text()').get()
            protein_value2 = protein_value + ' gram'
            fat_value = response.xpath('//*[ @ id = "recipe-footer"]/div[2]/div/div[6]/div[1]/span[2]/text()').get()
            fat_value2 = fat_value + ' gram'
        except TypeError:
            carbs_value2 = 'unknown'
            protein_value2 = 'unknown'
            fat_value2 = 'unknown'
        time = response.xpath(
            '//*[@id="start-of-content"]/div/div[1]/div[1]/div/div/div/div/div[2]/div/div[3]/div[3]/div/text()').get().replace(
            ". bereiden", "")

        i_filter = 1
        filter_list = []
        filter = 'empty'
        while filter != None:
            filter = response.xpath(
                f'//*[@id="start-of-content"]/div/div[1]/div[1]/div/div/div/div/div[2]/div/div[5]/ul/li[{i_filter}]/a/span/text()').get()
            if filter != None:
                filter_list.append(filter)
            i_filter = i_filter + 1

        i_prep = 1
        step_list = []
        preparation_step = 'empty'
        while preparation_step != None:
            preparation_step = response.xpath(
                f'//*[@id="start-of-content"]/div/div[1]/div[2]/div[2]/div/div/div[2]/div[3]/div[1]/div[{i_prep}]/p/text()').get()
            if preparation_step != None:
                preparation_step.replace('\r', '')
                step_list.append(preparation_step)
            i_prep = i_prep + 1

        photo_url = response.xpath(
            '//*[@id="start-of-content"]/div/div[1]/div[1]/div/div/div/div/div[1]/figure/img/@srcset').get()
        srcset_list = photo_url.split(", ")
        recipe_photo_url = None
        for item in srcset_list:
            url, descriptor = item.split(" ", 1)
            if descriptor == "1224w":
                recipe_photo_url = url
                break
        print(recipe_title)
        self.csv_writer.writerow(
            [recipe_title, energy, carbs_value2, protein_value2, fat_value2, time, filter_list, step_list,
             recipe_photo_url])

    def closed(self, reason):
        self.csv_file.close()
        self.modify_csv()

    def modify_csv(self):
        headers = ["Recipe Title", "Energy", "Carbs", "Protein", "Fat", "Time", "Filters", "Preparation", "Photo"]
        with open('recipes.csv', 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter=';')
            rows = list(csv_reader)

        # Insert headers at the beginning
        rows.insert(0, headers)

        # Reopen the CSV file in write mode to save the modifications
        with open('recipes.csv', 'w', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file, delimiter=';')
            csv_writer.writerows(rows)


def urls_list():
    url_list = []
    base_string = 'https://www.ah.nl/allerhande/recept/R-R119'

    for i in range(1000, 1300):
        url = base_string + str(i)
        url_list.append(url)
    return url_list

def run_spider(urls):
    process = CrawlerProcess(settings=get_project_settings())
    process.crawl(AHRecipeSpider, urls=urls)
    process.start()


if __name__ == "__main__":
    urls = urls_list()
    run_spider(urls)
