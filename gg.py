#!/usr/bin/env python
#Author: Abby Owen
#Purpose: Create a web scraper that will send a message to my friend Ray each day
#letting her know if there are any new listings of Golden Goose shoes available

import requests
from bs4 import BeautifulSoup
from Shoe import Shoe
import schedule
import time
from twilio.rest import Client
import datetime

# URL to scrape
url = 'https://www.therealreal.com/products?keywords=Golden%20Goose%20Shoes'

# File that keeps track of the listings that my system "knows about" so it can
# distinguish between new and old listings
listing_file = 'gg-listings_tester.txt'

# I use cronitor to manage my cron jobs so I get notified if there are any
# errors if the code doesn't run at 12:00 as it should
requests.get(
   'https://cronitor.link/HzlGgI/run',
   timeout=10
)

# Returns the number of lines in my file
def check_file_lines(filename):
    file = open(filename, 'r')
    lines = 0
    for line in filename:
        lines = lines + 1
    file.close()
    return lines


# Establish a base for the first run of the scraper
# Creates a csv file of the listings on the first pass
def base_listings(url, filename):

    file = open(filename, 'r+')

    # Flag myself as a User-Agent to allow access to the page as a scraper
    headers = {'User-Agent': 'APIs-Google (+https://developers.google.com/webmasters/APIs-Google.html)'}

    # Get the page to scrape
    page = requests.get(url, headers=headers)

    print("success")

    # Use Beautiful Soup to parse the HTML of the page
    soup = BeautifulSoup(page.content, 'html.parser')

    # Generate a list of all of the product cards for Golden Goose shoes on the shoes
    cards = soup.find_all('a', {'class': 'product-card js-plp-product-card', 'href': True, 'data-product-id': True})

    listings = []

    # Create a new shoe object for each product card
    for card in cards:
        # Get product ID of the shoe
        pID = card['data-product-id']

        # Get link to the shoe
        href = card['href']

        # Get the name of the shoe
        name = card.find("div", {"class": 'product-card__description'})

        # Get the size of the shoe
        size = card.find("div", {"class": 'product-card__size'})

        # Prices on the site are stored in 2 different ways, in a discount and
        # in a regular format. This portion is to make sure the price of the shoe
        # is captured whether it is in the discounted or full price format
        if card.find("div", {"class": 'product-card__price'}) != None:
            price = card.find("div", {"class": 'product-card__price'})
            shoe = Shoe(name.text, size.text, price.text, href, pID)
            listings.append(shoe.__str__())

        else:
            price = card.find("div", {"class": 'product-card__discount-price'})
            shoe = Shoe(name.text, size.text, price.text.split("- ")[1], href, pID)
            listings.append(shoe.__str__())

    # Write all of the lines to the file if it is empty
    if check_file_lines(filename) == 0:
        for listing in listings:
            filename.write(listing + "\n")


    file.close()
    return listings



# Handle new listings
def new_listings(url, filename):
    file = open(filename, 'a+')
    new_listings = []

    # Scrape the site to look for new listings
    check_listings = base_listings(url, filename)

    # Compare each listing in the new listing scrape to the file to see if it is
    # new or existing
    for listing in check_listings:
        size = float(listing.strip().split(",")[1])

        # Only keep listings that are size 9 (Ray's shoe size)
        if traverse_file(listing.__str__(), filename) == False and size == 9:
            new_listings.append(listing.__str__())

    # Check the size of the list that stored the new listings. If the list is
    # not empty there is something new
    if len(new_listings) != 0:
        print("something new is in store!")
        for listing in new_listings:
            file.write(listing + "\n")
    else:
        print("nothing new!")

    file.close()
    print(new_listings)
    return new_listings


# Helper function in order to determine a match between listings in the file
def traverse_file(string, filename):
    file = open(filename, 'r')
    for line in file:
        if line.strip().split(",")[4] == string.strip().split(",")[4]:
            file.close()
            return True
    file.close()
    return False



# Use of the Twilio to send daily messages regarding new shoes in store
def send_message(url, filename):
    account_sid = 'AC6d32438285a5bb7ad69b9cbe9272cb9b'
    auth_token = 'c7c1c1aef57821941025cf5f82a33608'

    # New listings
    updated = new_listings(url, filename)

    # Create a date and time object to include the date of the message
    x = str(datetime.datetime.now())
    dt_obj = datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')


    # Create messages to be sent
    if len(updated) > 0:
        # Base message saying the date and the amount of new listings that are in store
        client = Client(account_sid, auth_token)
        message = "Hello Ray! Today is " + datetime.datetime.strftime(dt_obj, "%B %d, %Y") + ". " + "This morning there are " + str(len(updated)) + " new golden goose listings on TheRealReal!"


        message = client.messages \
                        .create(
                            body = message,
                            from_ = '+19127374991',
                            to = '+12017390346'
                        )

        # Send a new message for each shoe in store
        for shoe in updated:
            client = Client(account_sid, auth_token)
            shoe_message = shoe.strip().split(",")[0] + ", Size " + shoe.strip().split(",")[1] + ", " + shoe.strip().split(",")[2] + " Link: " + "therealreal.com" + shoe.strip().split(",")[3]
            shoe_message = client.messages \
                                 .create(
                                    body = shoe_message,
                                    from_ = '+19127374991',
                                    to = '+12017390346'
                                 )


    # Message that will be sent if there are no new listings
    else:
        client = Client(account_sid, auth_token)
        message = "Hello Ray! Today is " +  datetime.datetime.strftime(dt_obj, "%B %d, %Y") + ". " + "This morning there are no new golden goose listings on TheRealReal."


        message = client.messages \
                        .create(
                            body=message,
                            from_='+19127374991',
                            to='+12017390346'
                     )


send_message(url, listing_file)
requests.get(
   'https://cronitor.link/HzlGgI/complete',
   timeout=10
)
