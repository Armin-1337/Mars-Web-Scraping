from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import mars_webscrape

app = Flask(__name__)

# Use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")

@app.route("/")
def home():

    # Find one record of data from the mongo database
    mars = mongo.db.mars.find_one()

    # Return template and data
    return render_template("index.html", mars=mars)

# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    mars_data = mars_webscrape.scrape_info()

    mongo.db.mars.update({}, mars_data, upsert=True)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
