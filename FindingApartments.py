# uses python 3.6 (64-bit)
# beautifulsoup4 (4.6.0)
# other packages are a part of python 3.6 (64-bit)

import bs4 as bs
import urllib.request
import smtplib
import re


# goes to specified CraigsList webpage to pull information on posted apartments
class CraigslistScraper:
    def __init__(self, url_search):
        self.url_search = url_search

    def CraigslistInfoGrabber(self):
        """returns list of Apartments from given Craigslist url. The list returned is: [url, location or null, str($price) or null]"""
        sauce = urllib.request.urlopen(self.url_search)
        soup = bs.BeautifulSoup(sauce, "lxml")
        craig_results = soup.findAll("li",{"class":"result-row"})#creates list of results
        apartments =[]
        for result in craig_results: # iterates through results
            new_apartment = []
            url_link = result.a["href"] # grabs links to results need to check if they work
            new_apartment.append(url_link)
            for item in result.findAll("p",{"class":"result-info"}):
                item_resultPrice = item.findAll("span",{"class":"result-price"})
                item_resultHood = item.findAll("span",{"class":"result-hood"})
                if not item_resultPrice:
                    item_resultPrice = "null"
                    new_apartment.append(item_resultPrice)
                    new_apartment.append(item_resultHood[0].text)
                if not item_resultHood:
                    item_resultHood = "null"
                    new_apartment.append(item_resultPrice[0].text)
                    new_apartment.append(item_resultHood)
                else:
                    item_resultHood = item_resultHood[0].text
                    item_resultHood = re.sub('[(){}<>]','',item_resultHood)
                    new_apartment.append(item_resultHood)
                    new_apartment.append(item_resultPrice[0].text)
            apartments.append(new_apartment)
        apartments = self.format_prices(apartments)
        return apartments

    def format_prices(self,apartments):
        """removes prices that are null and changes prices to int for further processing later in program"""
        count = 0
        keeping_apartments =[]
        while count < len(apartments):
            if apartments[count][2] != "null":
                getting_price = apartments[count][2].split("$")
                price = int('{}'.format(getting_price[1]))
                apartments[count][2] = price
                keeping_apartments.append(apartments[count])
            count += 1
        return keeping_apartments


# class used to sort the listing of apartments using mergesort algorithm to organize from cheapest to most expensive
class SortingAptList:
    """uses the mergesort algorithm to organize the apartments from the cheapest to the most expensive"""
    def MergeSort(self,apartments):
        if (len(apartments) == 0) or (len(apartments)==1):
            return apartments
        else:
            middleList = len(apartments)//2
            Left = self.MergeSort(apartments[:middleList])
            Right = self.MergeSort(apartments[middleList:])
            return self.Merge(Left,Right)
    

    def Merge(self,Left,Right):
        merged = []
        while (len(Left) != 0) and (len(Right) != 0):
            if Left[0][2] < Right[0][2]:
                merged.append(Left[0])
                Left.pop(0)
            else:
                merged.append(Right[0])
                Right.pop(0)
        if len(Left) == 0:
            for item in Right:
                merged.append(item)
        else:
            for item in Left:
                merged.append(item)
        return merged


# class used to manipulate the list of apartments postings from craigslist
class ManipulatingApartmentsListing:
    def __init__(self, ApartmentList):
        self.ApartmentList = ApartmentList

    def TopTenApartments(self):
        """Function will return the top 10 cheapest apartments on the current craigslist webpage given in search_url"""
        topten = []
        count = 0
        while count < 10: # can modify the number to change the amount of apartments to send to user
            topten.append(self.ApartmentList[count])
            count += 1
        print("Getting Top Ten")
        return topten


# class to separate functionality of sending emails to recipients
class EmailingUser:
    def __init__(self, gmail_user, gmail_password, ToEmail):
        self.gmail_user = gmail_user
        self.gmail_password = gmail_password
        self.ToEmail = ToEmail


    def sending_email(self, subject, content):
        """this function will be used to send an email message to update user about new cheap apartments"""
        try:
            mail_ssl = smtplib.SMTP_SSL('smtp.mail.yahoo.com',465)
            mail_ssl.ehlo()
            mail_ssl.login(self.gmail_user, self.gmail_password)
            email_msg = "Subject: {} \n\n{}".format(subject,content)
            mail_ssl.sendmail(self.gmail_user, self.ToEmail, email_msg)
        except:
            print("wasn't able to connect")

    def MakingEmailContent(self,SavedApartments):
        """This will make the email content that we will send to user email look presentable and easy to understand"""
        content = ""
        count = 1 
        for item in SavedApartments:
            content += "{}. {}\n \tThis Apartment is Located in {} and it costs {} dollars\n\n".format(count,item[0],item[1],item[2])
            count += 1
        content += "\n\n\n Do not Reply to This Message.\nIf you want to stop receiving these emails text Alex and let him know"
        return content 


def main(): 
    search_url = "https://chicago.craigslist.org/search/apa?query=studio&search_distance=10&postal=60153&max_price=1000&availabilityMode=0&sale_date=all+dates"
    CraigScrape = CraigslistScraper(search_url)
    ListOfApartments = CraigScrape.CraigslistInfoGrabber() # returns list of apartments currently in given url and removes those with no pricing
    OrganizingApartments = SortingAptList() # class used to organize apartments scraped from craigslist
    OrganizedApartments = OrganizingApartments.MergeSort(ListOfApartments) # returns list of apartments with increasing order of price
    ManageApartments = ManipulatingApartmentsListing(OrganizedApartments) # initializes the class ManipulatingApartmentsListing
    TopTenApartments = ManageApartments.TopTenApartments() # returns the top ten cheapest apartments
    from_email = ""
    email_password = "" 
    to_email = ""
    Emailing = EmailingUser(from_email,email_password, to_email)
    Subject = 'Top Ten Cheapest Apartments Today'
    Content = Emailing.MakingEmailContent(TopTenApartments)
    Emailing.sending_email(Subject, Content)
    print('Finished')

if __name__ == "__main__":
    main()
