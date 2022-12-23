from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

    
options = Options()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
driver.get('https://www.wolfgame.tools/address/0x6e34247a8ee476282E07E07a322b934c74641993?tokens=1')
page_state = driver.execute_script('return document.readyState;')
if(page_state == 'complete'):
    
#driver.set_page_load_timeout(40) # seconds
#driver.set_script_timeout(40) # seconds
#driver.implicitly_wait(40) # seconds

    html = driver.page_source
#soup = BeautifulSoup(html, "html.parser")

for link in BeautifulSoup(html, 'lxml', parse_only=SoupStrainer('a')):
    if link.has_attr('href'):
        print(link['href'])


# assetContainer = soup.find( class_ = "mt-20 container-fluid")
# print(soup)
# print(assetContainer)


#$(".tab-content").children[1].children[0].children[1].children[1].children[0].children[0].children[1].hrefn