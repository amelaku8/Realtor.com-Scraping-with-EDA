from lxml import etree
from bs4 import BeautifulSoup
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


start_url = "https://www.realtor.com/realestateandhomes-search/Los-Angeles_CA"


def extract_data(resp):
    houses = etree.HTML(resp.page_source).xpath('//div[contains(@class,"BasePropertyCard_propertyCardWrap__J0xUj") ]')
    z = []
    next_ = resp.find_element(by = By.LINK_TEXT,value = 'Next' )

    i = 0
    
    while i < len(houses):
        
        houses = etree.HTML(resp.page_source).xpath('//div[contains(@class,"BasePropertyCard_propertyCardWrap__J0xUj") ]')

        house = BeautifulSoup(etree.tostring(houses[i]))
        if house.find("span",{"class":"card-title-text"}) == None:  
            time.sleep(2)
            next_.send_keys(Keys.PAGE_DOWN)
            continue

        broker = house.find("span",{"class":"card-title-text"}).text  
        status = house.find_all("div",{"data-testid":"card-description"})[0].text
        price = house.find_all("div",{"class":"price-wrapper"})[0].text
        attributes = house.find("ul")
        bed = -1
        bath = -1
        lot_size = -1
        area = -1

        for attribute in attributes:
            if attribute.text.find("bed") != -1:
                bed = attribute.text

            elif attribute.text.find("bath") != -1:
                bath =  attribute.text

            elif attribute.text.find("lot") != -1:
                lot_size = attribute.text
            elif attribute.text.find("sqft") != -1:
                area =  attribute.text
        address1 = house.find("div",{"data-testid":"card-address-1"}).text
        address2 = house.find("div",{"data-testid":"card-address-2"}).text
        values = {"broker":broker,"status":status,"price":price,
                  "bed" : bed,"bath":bath,"lot_size":lot_size,"area":area,
                  "address1":address1,"address2":address2}
        z.append(values)
        i = i+1

    return z    



def write_data(y):

    for row in y:
        with open("data.csv",'at',encoding = "utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(list(row.values()))


def main():

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome()
    driver.get(start_url)


    while True:
        y = extract_data(driver)
        write_data(y)
        print(f"Scraped {driver.current_url}")
        try:
            driver.find_element(by = By.LINK_TEXT,value = 'Next' ).click()
        except ElementClickInterceptedException:
           break
        
    

if __name__ == "__main__":
    main()
