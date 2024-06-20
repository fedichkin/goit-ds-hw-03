import requests
from bs4 import BeautifulSoup, Tag
import json
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import OperationFailure
from dotenv import load_dotenv

load_dotenv()

base_url = 'https://quotes.toscrape.com'


def connect_to_db():
    user = os.getenv('MONGO_USER')
    password = os.getenv('MONGO_PASSWORD')
    mongo_url = f'mongodb+srv://{user}:{password}@cluster0.iphuf8z.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

    client = MongoClient(mongo_url, server_api=ServerApi('1'))
    return client.goit_3


def parse_quote(quote: Tag) -> dict:
    quote_text = quote.select('.text')[0].text
    author = quote.select('.author')[0].text
    tags = [tag.text for tag in quote.select('.tags .tag')]

    return {'quote': quote_text, 'author': author, 'tags': tags}


def parse_author(url):
    html_doc = requests.get(f'{base_url}{url}/')
    if html_doc.status_code == 200:
        soup = BeautifulSoup(html_doc.content, 'html.parser')
        fullname = soup.select('.author-title')[0].text
        born_date = soup.select('.author-born-date')[0].text
        born_location = soup.select('.author-born-location')[0].text
        description = soup.select('.author-description')[0].text.strip()

        return {'fullname': fullname, 'born_date': born_date, 'born_location': born_location,
                'description': description}


def parse_data():
    quotes = []
    authors = []
    authors_name = set()
    current_page = 1

    while True:
        html_doc = requests.get(f'{base_url}/page/{current_page}/')
        current_page += 1

        if html_doc.status_code == 200:
            soup = BeautifulSoup(html_doc.content, 'html.parser')
            quotes_tags = soup.select('.quote')

            if len(quotes_tags) == 0:
                break

            for quote in quotes_tags:
                quote_data = parse_quote(quote)
                quotes.append(quote_data)

                if quote_data['author'] not in authors_name:
                    authors_name.add(quote_data['author'])
                    author_page_url = quote.select('.author + a')[0].attrs['href']
                    author_data = parse_author(author_page_url)

                    if author_data is not None:
                        authors.append(author_data)
        else:
            break

    return quotes, authors


def save_json_to_file(url_file, data):
    with open(url_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_to_mongo_from_file(url_file, name_collection):
    try:
        with open(url_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            db = connect_to_db()
            db[name_collection].insert_many(data)
    except OperationFailure:
        print('Error to connect to Mongo DB')
    except FileNotFoundError:
        print('Error to read file')


def main():
    quotes, authors = parse_data()
    save_json_to_file('quotes.json', quotes)
    save_json_to_file('authors.json', authors)
    # load_to_mongo_from_file('quotes.json', 'quotes')
    # load_to_mongo_from_file('authors.json', 'authors')


if __name__ == '__main__':
    main()
