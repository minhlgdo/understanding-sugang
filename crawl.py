from pandas.core.frame import DataFrame
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

def reformatProfessorsName(name):
    name = name.strip()
    if (len(name) > 0):
        if (',' in name):
            name = name.replace(',', '')
        name = name.title()
        return name
    
    return ''
    
def crawling():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    driver.get("https://sugang.snu.ac.kr/sugang/cc/cc100InterfaceSrch.action?lang_knd=en")
    driver.implicitly_wait(3)

    showClassList = driver.find_element_by_class_name('total-search-btn').click()
    sleep(3)

    start_page = 1

    while (True):
        print("Page: " + str(start_page))
        sleep(2)
        class_count = driver.find_element_by_xpath("//div[@class='total-list-count']/span[@class='num']")
      
        if (int(class_count.text) == 0):
            break

        classList = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='course-info-list']/div[@class='course-info-item']")))
        # driver.implicitly_wait(5)
        # classList = driver.find_element_by_xpath("//div[@class='course-info-list']/div[@class='course-info-item']")
        # print(len(classList))
        if (len(classList) > 0):
            for item in classList:
                detailedClassInfo = item.find_element_by_xpath('.//div[@class="course-name"]').click()
                driver.implicitly_wait(3)

                item_source = driver.page_source
                soup = BeautifulSoup(item_source, 'lxml')

                course = {}
                # category = soup.find('span', id_='submattFgNm').get_text().strip()
                course['category'] = soup.find("ul", {"class":"cd-user"}).find("li").find("span", {"id": "submattFgNm"}).get_text().strip()
                # print(category)

                course['level'] = soup.find("ul", {"class":"cd-user"}).find("li").find("span", {"id": "submattCors"}).get_text().strip()
                # print(level)

                course['year'] = soup.find("ul", {"class":"cd-user"}).find("li").find("span", {"id": "openShyr"}).get_text().strip()
                if (len(course['year']) != 0):
                    course['year'] = course['year'][0]
                # print(academic_year)

                name = soup.find("ul", {"class": "cd-info"}).find_all("li")[1].find("strong").get_text().strip()
                course['name'] = name.split(":")[1].strip()
                # print(name)
                
                course['id'] = soup.find("ul", {"class": "cd-info"}).find_all("li")[2].get_text().strip()
                # print(id)

                course['credits'] = soup.find("ul", {"class": "cd-info"}).find_all("li")[3].find("em").get_text().strip()[0]
                # print(credits)

                professor = soup.find("ul", {"class":"cd-user"}).find_all("li")[1].find("span", {"id":"profNm"}).get_text().strip()
                course['professor'] = reformatProfessorsName(professor)
                # print(professor)

                course['department'] = soup.find("ul", {"class":"cd-user"}).find_all("li")[1].find("span", {"id":"deptKorNm"}).get_text().strip()
                
                course['sub-category'] = soup.find("ul", {"class": "cd-info"}).find_all("li")[0].find("strong").get_text().strip()
                # print(subCategory)

                course['language'] = soup.find("table", {"class": "course-info-table diff"}).find("tbody").find_all("tr")[1].find_all("td")[0].get_text()
                # print(language)

                course['location'] = []
                for tr in soup.find("table", {"class":"course-info-table diff rowspan"}).find("tbody").find_all("tr"):
                    info = {}
                    tds = tr.find_all("td")
                    info["time"] = tds[0].get_text()
                    info["place"] = tds[2].get_text()
                    course['location'].append(info)

                course['remark'] = soup.find_all("table", {"class" : "course-info-table diff"})[3].find("tbody").find_all("tr")[1].find_all("td")[1].get_text()
                # print(remark)

                closeButton = driver.find_element_by_class_name('close-md-btn')
                driver.execute_script("arguments[0].click();", closeButton)
                data.append(course)

            start_page = start_page+1
            driver.execute_script("fnGotoPage(" + str(start_page) +")")
            sleep(5)
        
    driver.close()

if __name__ == "__main__":
    print("Start scraping the file")
    data = []
    crawling()
    dataFrame = pd.DataFrame.from_dict(data)
    # Serving for analysing the data later on
    dataFrame.to_csv('data.csv', index=False, header=True, encoding='utf-8-sig') 
    # Uploading to database?
    # dataFrame.to_json('data.json', orient = 'records', lines=False, index="True") 
    print("Finish")
    print("Number of crawed classes: " + str(len(data)))


