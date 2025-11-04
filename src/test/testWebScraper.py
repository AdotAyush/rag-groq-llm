import requests
from bs4 import BeautifulSoup
url = "https://example.com"
html = requests.get(url).text
soup = BeautifulSoup(html, 'lxml')
print(soup.title)