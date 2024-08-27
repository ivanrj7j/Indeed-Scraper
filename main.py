from flask import Flask, render_template, request, redirect, url_for
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from proj_indeed.spiders.Intutorial import MySpider
import pandas as pd
import os
from datetime import datetime
import json

keyword_list = []   
location_list = []

app=app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        keyword = request.form['keyword']
        location = request.form['location']
        global k,l
        k=keyword
        l=location
        print("Before", keyword, location)
        keyword_list = keyword.split(',')
        location_list = location.split(',')
        print("After", keyword_list, location_list)
        for k in keyword_list:
            for l in location_list:               
                #keyword and location passed as argument
                p = Process(target=run_spider, args=(k, l))
                p.start()

    return render_template('p_age.html', keyword=keyword, location=location)


def run_spider(keyword,location):
    print("Lalalaa", keyword, location)

    # to get the current date and time to give the file name
    c_t = (datetime.now().strftime("%Y_%B_%d_%H_%M_%S")).replace(":",'')

    # Setting up fileNames
    file_name = f"{keyword}_{location}_{c_t}.json"
    file_path = os.path.join("outputs", file_name)

    #now we need to get the settings from the settings.py file
    settings = get_project_settings()
    settings.set("FEED_FORMAT", "json")
    settings.set("FEED_URI", file_path)
    
    # Run Scrapy spider with the latest input
    process = CrawlerProcess(settings)
    process.crawl(MySpider, keyword_list=keyword, location_list=location)
    process.start()
    process.join()
    
    

    if os.path.exists(file_path):
        data_df = pd.read_json(file_path)

        #from the data_df we are fetching relevant data and saving to two dataframes
        Jobs_df=data_df.iloc[:,:13].dropna(how='all', axis=0)
        Jobs_df["Search_KeyWord"]=keyword+" "+location
        Company_df=data_df.iloc[:,14:].dropna(how='all', axis=0)

        # Save DataFrames to CSV with requirement text current date and time
                #to get the current _date and time as text
        current_datetime = datetime.now().strftime("%Y%b%d_%H:%M:%S")
        ct1=current_datetime.replace(":",'')
        
        jobs_csv_name = f"Jobs_{keyword}_{location}_{ct1}.csv"
        company_csv_name = f"Company_{keyword}_{location}_{ct1}.csv"
        #now using the name fetched above we are creating the respective csv's
        Jobs_df.to_csv(os.path.join("outputs", jobs_csv_name), index=False)
        Company_df.to_csv(os.path.join("outputs", company_csv_name), index=False)
        
        return {"Jobs": Jobs_df, "Company": Company_df}
    else:
        return {"error": f"File '{file_name}' not found"} 


if __name__ == '__main__':
    app.run(debug=True)
