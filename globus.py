import bs4
import cloudscraper, json, collections
from datetime import date
from bs4 import BeautifulSoup as bs
from services import GetTagValue, GetDictValue, list_to_dict, remove_shit

Product = collections.namedtuple('Product', 'date brand name price promo_price card_price rating desc comp url')
scraper = cloudscraper.create_scraper()


def collect_categories():
    response = scraper.get('https://online.globus.ru/').text
    soup = bs(response, 'lxml')
    categories_tags = soup.find('ul', class_='nav_main__content-list')
    categories_links = []
    for category in categories_tags:
        try:
            link = category.find('a').get('href')
            url = 'https://online.globus.ru' + link
            categories_links.append(url)
        except Exception as e:
            print(e, 'during collect_categories')

    return categories_links


def scrape_products_links(categories: list[str]):

    for category in categories:
        page = 1
        link = category + '?PAGEN_1={}'.format(page)
        try:
            response = scraper.get(link)

            while response:
                soup = bs(response.text, 'lxml')
                products = soup.find_all('a', class_='catalog-section__item__link catalog-section__item__link--one-line notrans')
                for product_link in products:
                    product = generate_product(f'https://online.globus.ru{product_link.get("href")}')
                    yield {
                        'date': product.date,
                        'brand': product.brand,
                        'name': product.name,
                        'reg_price': product.price,
                        'promo_price': product.promo_price,
                        'price_by_card': product.card_price,
                        'rating': product.rating,
                        'description': product.desc,
                        'composition': product.comp,
                        'url': product.url
                    }
                page += 1
        except Exception as e:
            print(e, 'during scrape_products_links')



def generate_product(product_link) -> Product:

    today = date.today().strftime('%d/%m/%Y')
    response = scraper.get(product_link)
    if response:
        soup = bs(response.text, 'lxml')
        getTag = GetTagValue(soup)

        price_tag = soup.find('span', class_='item-price__num')
        price = price_tag.find('meta').get('content').replace(' ', '.')

        name = remove_shit(getTag.scope('h1', {'class':'js-with-nbsp-after-digit'}))

        tbody = soup.find('tbody')
        arr = []
        for td in tbody.find_all('td'):
            arr.append(td.text.replace('\n', '').strip())
        brand_comp_dict = list_to_dict(arr)
        getDict = GetDictValue(brand_comp_dict)

        desc = getTag.scope('p', {'itemprop': 'description'})

        old_price_tag = getTag.scope('span', {'class':'item-price__old'})

        if old_price_tag:
            # oldprice = f"{old_price_tag.text}".replace('\n', '').replace(' ', '.')
            oldprice = old_price_tag.replace('\n', '').replace(' ', '.')
            return Product(
                date=today,
                brand=getDict.value('Бренд'),
                name=name,
                price=oldprice,
                promo_price=price,
                card_price=price,
                rating=None,
                desc=desc,
                comp=getDict.value('Состав'),
                url=product_link,
            )
        else:

            return Product(
                date=today,
                brand=getDict.value('Бренд'),
                name=name,
                price=price,
                promo_price=None,
                card_price=None,
                rating=None,
                desc=desc,
                comp=getDict.value('Состав'),
                url=product_link,
            )

categories = collect_categories()

from datetime import datetime

start = datetime.now()
print("Start Time =", start.strftime("%H:%M:%S"))

i = 0

with open('globus.json', 'w', encoding='utf-8') as f:
    for product in scrape_products_links(categories):
        
        print(i + 1)
        
        data = json.dumps(product)
        data = json.loads(str(data))
        json.dump(data, f, indent=4, ensure_ascii=False)
        
        i += 1
        if i >= 50:
            break
        
end = datetime.now()
print("End Time =", end.strftime("%H:%M:%S"))
print(f"Duration = {end - start}")