from bs4 import BeautifulSoup
import requests
import csv
from pathlib import Path
from unicodedata import normalize

def findJobs(keywords, location="remote"):
    jobsDict = []
    # get job's first page, get number of pages
    def scrapeWorkUA():
        kwSplit = keywords.replace("+", "plus").replace("#", "%23").split(" ")
        url = 'https://www.work.ua/jobs-' + location.lower() + "-"
        urlKW = url  # url with keywords, like https://www.work.ua/jobs-kyiv-python+developer
        index = 0
        for i in kwSplit:
            if index == 0:
                urlKW += i
                index += 1
            else:
                urlKW += "+" + i.lower()
        request = requests.get(urlKW).text
        soup = BeautifulSoup(request, 'lxml')
        try:
            pages = int(soup.find_all("nav")[-1].find('ul', class_="hidden-xs").find_all('li')[-2].text)
        except AttributeError:
            pages = 1
            
        def scrapePage(pageURL):
            urlW = 'https://www.work.ua/'
            requestPage = requests.get(pageURL).text
            soupPage = BeautifulSoup(requestPage, 'lxml')
            jobCards = soupPage.find_all('div', class_='job-link')
            for card in jobCards:
                cmpInfo = card.find('div', class_='mt-xs')
                jobName = card.find('h2', class_='my-0').text.strip()
                jobPay = "Не вказано"
                jobCompany = cmpInfo.span.span.text
                companyVerified = False
                companyAgency = False
                jobLocation = cmpInfo.find_all('span', class_="")[-1].text.replace(',', '').strip()
                jobPostTime = "Не вказано"
                jobInfoLink = urlW + 'jobs/' + card.find_previous('a')['name']
                jobReservation = False
                for i in card.find_all('span', class_="glyphicon"):
                    if i.find_next_sibling('span')!=None:
                        if i.find_next_sibling('span').text == "Бронювання" or i.text == "Бронювання":
                            jobReservation = True
                try:
                    jobPostTime = card.find('time')['datetime']
                except TypeError:
                    pass
                try:
                    if [True for i in cmpInfo if cmpInfo.find('ul')!=None][0] == True:
                        companyVerified=True
                except IndexError:
                    pass
                try:
                    if "Агенція" in cmpInfo.find("span", class_="label-text-gray").text:
                        companyAgency = True
                except AttributeError:
                    pass
                for i in card.find_all('span', class_='strong-600'):
                    if 'грн' in i.text:
                        jobPay = normalize("NFKD", i.text)  # convert unicode space codes into utf-8
                jobValues = {
                    "Company": jobCompany,
                    "Title": jobName,
                    "Location": jobLocation, 
                    "Salary": jobPay,
                    "Info": jobInfoLink,
                    "Post date": jobPostTime,
                    "Company Verified": companyVerified,
                    "HR Agency": companyAgency,
                    "Reservation": jobReservation
                }
                jobsDict.append(jobValues)
                
        # scrape all pages
        for i in range(1, pages+1):
            urlP = urlKW + f"/?_pjax=%23pjax&page={i}"
            scrapePage(urlP)

    
    #def scrapeRobotaUA(location1="ukraine"):
    #    kwSplit = keywords.replace("+", "%252B").replace("#", "%2523").split(" ")
    #    url = 'https://robota.ua/zapros/'
    #    urlKW = url  # url with keywords, like https://www.work.ua/jobs-kyiv-python+developer
    #    index = 0
    #    for i in kwSplit:
    #        if index == 0:
    #            urlKW += i
    #            index += 1
    #        else:
    #            urlKW += "-" + i
    #    urlKW += f"/{location1.lower()}"
    #    if location == "remote":
    #        urlKW += f"/params;scheduleIds=3"
    #    request = requests.get("https://robota.ua/zapros/python-developer/ukraine")
    #    print(request.text)
    #    soup = BeautifulSoup(request, 'lxml')
    #    pages = soup.find_all('a', class_="ng-star-inserted")
    #    print(pages)
    
    # scrapeRobotaUA()
    scrapeWorkUA()
    return jobsDict, keywords
        
def saveInCSV(dictJobs, searchKeyword):
    csvName = searchKeyword.replace(" ", "-") + ".csv"
    headerNames = ["Company", "Title", "Location", "Salary", "Info", "Post date", "Company Verified", "HR Agency", "Reservation"]
    filePath = Path(__file__).parent / 'jobCSVs' / csvName
    if filePath.is_file():
        pass # should append new listings
    else:
        with open(filePath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, headerNames)
            writer.writeheader()
            writer.writerows(dictJobs)
            
cdevDict, cdevKeywords = findJobs("C developer")
saveInCSV(cdevDict, cdevKeywords)