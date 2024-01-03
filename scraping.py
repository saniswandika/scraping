import requests
from bs4 import BeautifulSoup
import pandas as pd
import pymysql
from datetime import datetime, timedelta

start_date = input('Masukkan tanggal awal (format: YYYY-MM-DD): ')
end_date = input('Masukkan tanggal akhir (format: YYYY-MM-DD): ')
indeks_berita = input('Masukkan indeks berita: ')
site = input('Masukkan site berita: ')
# Ubah string tanggal ke dalam objek datetime
start = datetime.strptime(start_date, '%Y-%m-%d')
end = datetime.strptime(end_date, '%Y-%m-%d')

data = {'Title': [], 'Content': [], 'Image': [], 'Date': []}  # Tambahkan 'Image' ke dalam data

# Loop untuk setiap tanggal dalam rentang
current_date = start
while current_date <= end:
    formatted_date = current_date.strftime('%Y-%m-%d')
    if indeks_berita:
        url = f'https://indeks.kompas.com/{indeks_berita}/?site=all&date={formatted_date}'
    else:
        url = f'https://indeks.kompas.com/?site={site}&date={formatted_date}'
    
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')

    items = soup.find_all('a', class_='article__link')
    for item in items:
        link = item.get('href')
        if link:
            print("Scraping article:", link)
            article_req = requests.get(link)
            article_soup = BeautifulSoup(article_req.text, 'html.parser')

            article_title = article_soup.find('h1', class_='read__title')
            content = article_soup.find('div', class_='read__content')
            image = article_soup.find('div', class_='photo__wrap').find('img')['src']
            dates_news = article_soup.find('div', class_='read__time')
            if article_title and content and image:
                title_text = article_title.text.strip()
                content_text = content.text.strip()
                date_text = dates_news.text.strip().replace('Kompas.com - ', '')

                data['Title'].append(title_text)
                data['Content'].append(content_text)
                data['Image'].append(image)
                data['Date'].append(date_text)
            else:
                print("Some elements are missing in this article:", link)
    # Tambahkan 1 hari ke tanggal saat ini
    current_date += timedelta(days=1)
df = pd.DataFrame(data)

# Menyimpan DataFrame ke dalam file Excel
file_name = 'articles.xlsx'
df.to_excel(file_name, index=False, encoding='utf-8')
print(f"Data telah disimpan ke '{file_name}'")

# Saving to MySQL
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='scraping',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

for i in range(len(data['Title'])):
    title = data['Title'][i]
    content = data['Content'][i]
    image = data['Image'][i]
    date = data['Date'][i]
    

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO artikel (title, content, image, date) VALUES (%s, %s, %s ,%s)"
            cursor.execute(sql, (title, content, image, date))
        connection.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()

connection.close()
print(f"Data telah disimpan ke database mysql'")