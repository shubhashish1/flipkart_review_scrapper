from flask import Flask,jsonify,render_template, request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

import logging

FORMAT = '%(asctime)s - %(message)s'

logging.basicConfig(filename='scrapper.log',level=logging.INFO,format=FORMAT)

app = Flask(__name__)

@app.route('/',methods = ['GET','POST'])
def home():
    return render_template('index.html')

@app.route('/review',methods = ['POST']) # Here the route name is review becz we have passed in index.html the redirection to
def index():                             # review route with POST method
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","") # cpntent becz in index.html we have given the input as content
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            #print("The url is ", flipkart_url)
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            #print("finding boxes ",box)
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding = 'utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            logging.info("Product, Customer Name, Rating, Heading, Comment \n")
            fw.write(headers)
            reviews = []

            for commentbox in commentboxes:
                try:
                    # name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    name = 'No Name'
                    logging.error("no name")

                try:
                    # rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'
                    logging.error("No Rating")

                try:
                    # commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                    logging.error("No Comment Heading")
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    # custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    print("Exception while creating dictionary: ", e)
                    logging.error("Exception while creating dictionary: ", e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                  "Comment": custComment}
                reviews.append(mydict)
            logging.info("reviews scrapped and stored in table format successfully")
            return render_template('result.html', reviews=reviews[0:(len(reviews) - 1)])

        except Exception as e:
            print('The Exception message is: ', e)
            logging.error('The Exception message is: ', e)
            return 'something is wrong'

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)