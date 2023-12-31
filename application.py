from flask import Flask,  render_template, request, jsonify
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import requests
#import logging
from pymongo.mongo_client import MongoClient

#logging.basicConfig(filename="scrapper.log", level=logging.INFO)

application = Flask(__name__)

@application.route("/", methods=['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@application.route("/review", methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method =='POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = urlopen(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})
            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except:
                    pass
                    #logging.info("no name")

                try:
                    rating = commentbox.div.div.div.div.text
                except:
                    pass
                    #rating = 'No Rating'
                    #logging.info(rating)

                try:
                    commentHead = commentbox.div.div.div.p.text
                except:
                    pass
                    #commentHead = 'No Comment Heading'
                    #logging.info(commentHead)

                try:
                    custComment = commentbox.div.div.find_all('div', {'class': ''})[0].div.text
                except Exception as e:
                    pass
                    #logging.info(e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            #logging.info("log my final result {}".format(reviews))
            uri = "mongodb+srv://amaanrizvi39:Amaan369@cluster0.jwbt0oa.mongodb.net/?retryWrites=true&w=majority"
            # Create a new client and connect to the server
            client = MongoClient(uri)
            db = client['Flipkart_Reviews_Scrapper']
            coll = db['cust_reviews']
            coll.insert_many(reviews)
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            #logging.info(e)
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    application.run(debug=True)