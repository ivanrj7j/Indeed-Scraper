import scrapy
from datetime import datetime, timedelta
from urllib.parse import urlencode
from bs4 import BeautifulSoup



class MySpider(scrapy.Spider):
    name = 'indeed'

    def __init__(self, keyword_list, location_list, *args, **kwargs):
        super().__init__(**kwargs)

        print('-----------Keyword List and Location List:', keyword_list, location_list, "-----------\n\n")

        self.keyword_list = [keyword_list]
        self.location_list = [location_list]


    # get_indeed _search_url function is used to get the search url with relevant data

    def get_indeed_search_url(self, keyword, location, offset=0):
        parameters = {"q": keyword, "l": location, "filter": 0, "start": offset}
        return "https://www.indeed.com/jobs?" + urlencode(parameters) + '&sort=date'

    # start_requests gives the function call to parse 
    def start_requests(self):
        for k in self.keyword_list:
            for l in self.location_list:
                indeed_jobs_url = self.get_indeed_search_url(k, l)
                search_phrases = 'Key: ' + k + ' ' + 'Location: ' + l
                self.search_phrase = search_phrases
                # self.log(f"Requesting URL: {indeed_jobs_url} for {search_phrases}")
                yield scrapy.Request(indeed_jobs_url, callback=self.parse,
                                     meta={'keyword': k, 'location': l, 'offset': 0})

    def parse(self, response):
        #this function is used to parse through each job page
        jobs = response.xpath('//div[@class="job_seen_beacon"]')
        job_page_url = list(set(jobs.xpath(
            '//div[@class="css-dekpa e37uo190"]//a/@data-jk').getall()))  #(Returns  a list  of all  jobs available in a page)
        Posted_DT = jobs.xpath('//span[@data-testid="myJobsStateDate"]/text()').get()

        self.Posted_DT = Posted_DT
        
        for jk in job_page_url:  #(looping to get into each job page)
            job_link = 'https://www.indeed.com/viewjob?&jk=' + jk
            yield response.follow(job_link, callback=self.parse_job_page)  #navigating to each individual page

    #             break# for testing comment break to get all job details in a page

    #uncomment to get page navigation
    #navigating to each main page
        next_page = response.xpath('//a[@data-testid="pagination-page-next"]/@href').get()
        # if next page is not none it should navigate through next page and it will call parse func to get list of all listed jobs
        if next_page is not None:
            next_page_url= 'https://www.indeed.com'+ next_page
            yield response.follow(next_page_url,callback=self.parse)

    # tag remover function is used to remove tags from the data a kind of cleaning the data
    def tag_remover(self, text_to_parse):
        soup = BeautifulSoup(text_to_parse, 'html.parser')
        # Get the text without HTML tags
        plain_text = soup.get_text(separator=' ', strip=True)
        return plain_text

    #job page navigates through and fetches all relevant pages in each job page
    def parse_job_page(self, response):
        main = response.xpath('//div[@class="jobsearch-JobComponent css-u4y1in eu4oa1w0"]')
        j_d = self.tag_remover(response.xpath('//div[@id="jobDescriptionText"]').get())
        p_dt = self.Posted_DT
        # date in the website is not in the standard format ,"Just posted",'Today','Posted 30+ days ago','Posted 1 days ago'
        # the below logic was written to fetch the exact date of posting
        if p_dt is not None:
            if p_dt == 'Just posted' or p_dt == 'Today':
                posted_date = datetime.now().strftime("%d/%B/%Y")
            elif p_dt == 'Posted 30+ days ago':
                posted_date = p_dt
            else:
                posted_date = (datetime.now() - timedelta(days=int(p_dt.split(' ')[1]))).strftime("%d/%B/%Y")
        else:
            posted_date = p_dt

        c_li = main.xpath('//span[@class="css-1saizt3 e1wnkr790"]//a/@href').get()
        company_links = [c_li]
        # Check if c_li is not None before splitting
        if c_li is not None:
             c_key= c_li.split("tk=")[1].split("&")[0]
        else:
            c_key = None
        r_rating = main.xpath('//div[@class="css-1unnuiz e37uo190"]/span[@class="css-ppxtlp e1wnkr790"]/text()').get()
        scrapping_date = datetime.now().date()
        phrases = self.search_phrase

        # Format the scrapping date as 'dd/mmm/yyyy'
        formatted_scrapping_date = scrapping_date.strftime('%d/%B/%Y')
        yield response.follow(c_li, callback=self.parse_company_page)

        # Yield a dictionary with the extracted data
        yield {
            'Job_Page_Link': response.url,
            'Job_Title': main.xpath('//h1[@data-testid="jobsearch-JobInfoHeader-title"]/span/text()').get(),
            'Company_Name': main.xpath('//span[@class="css-1saizt3 e1wnkr790"]/a/text()').get(),
            'Job_Location': main.xpath('//div[@class="css-1ojh0uo eu4oa1w0"]/text()').get(),
            'Rating': r_rating,
            'Salary': response.xpath('//span[@class="css-19j1a75 eu4oa1w0"]/text()').get(),
            'Job_Page_ID': response.url.split("jk=")[1].split("&")[0],
            'PostedDT': posted_date,
            'SearchPhrases': phrases,
            'ScrappingDate': formatted_scrapping_date,
            'Company_Page_Link': c_li,
            'Company_ID': c_key,
            'JobDescription': j_d,
        }

    # to parse through company page 
    def parse_company_page(self, response):
        # extract company data
        company_data = self.extract_company_data(response)

        # extract the URL for reviews if available
        reviews_url = response.xpath('//li[@data-testid="reviews-tab"]//a/@href').get()

        # Fetch reviews asynchronously if reviews_url is not None
        # it crawls to review page and fetch relevant results
        if reviews_url:
            yield scrapy.Request(response.urljoin(reviews_url), callback=self.parse_review_page,
                                 meta={'company_data': company_data})
        else:
            # If no reviews URL, yield the company data directly
            yield company_data

    def parse_review_page(self, response):
        # Extract review data
        reviews_data = self.extract_review_data(response)

        # Retrieve the company data from the meta
        company_data = response.meta.get('company_data', {})

        # update the company data with the review information
        company_data.update(reviews_data)

        # Yield the combined company data with reviews
        yield company_data

    def extract_company_data(self, response):

        company_name = response.xpath('//div[@itemprop="name"]/text()').get()
        company_page_link = response.url
        company_ID = company_page_link.split("tk=")[1].split("&")[0]
        company_logo = response.xpath('//div[@class="css-1oe275d e37uo190"]/img/@src').getall()
        company_website_link = response.xpath('//li[@data-testid="companyInfo-companyWebsite"]//a/@href').get()
        company_description_xpath_result = response.xpath('//div[@class="css-y6ifcp eu4oa1w0"]').get()
        company_description = self.tag_remover(
            company_description_xpath_result) if company_description_xpath_result else None
        ceo = response.xpath('//div[@class="css-1w0iwyp e1wnkr790"]/text()').get()
        ceo_per = response.xpath('//span[@class="css-4oitjw e1wnkr790"]/text()').get()
        if ceo_per is not None:
            ceo_performance = ceo_per + '%'
        else:
            ceo_performance = None
        founded = response.xpath(
            '//li[@data-testid="companyInfo-founded"]/div[@class="css-1w0iwyp e1wnkr790"]/text()').get()
        c_size = response.xpath('//li[@class="css-1wsezwx e37uo190"]//div[@class="css-1k40ovh e1wnkr790"]//span').get()
        if c_size is not None:
            company_size = self.tag_remover(c_size)
        else:
            company_size = None
        revenue = response.xpath(
            '//li[@data-testid="companyInfo-revenue"]//div[@class="css-1k40ovh e1wnkr790"]/span/text()').get()
        industry = response.xpath('//a[@class="css-1rezcpd e19afand0"]/text()').get()
        headquarters = response.xpath('//span[@class="css-smaipe e1wnkr790"]/text()').get()
        salaries_xpath = response.xpath('//div[@class="cmp-SalaryCategoryCard css-n5zvfs e37uo190"]').get()
        salaries = self.tag_remover(salaries_xpath) if salaries_xpath else None
        rev_xpath = response.xpath('//div[@class="css-1j2sl1b e37uo190"]/div').get()
        rev = self.tag_remover(rev_xpath) if rev_xpath else None
        qna_xpath = response.xpath('//section[@data-testid="qna-section"]').get()
        fn_qna = self.tag_remover(qna_xpath) if rev_xpath else None
        company_wll_xpath = response.xpath('//section[@class="css-125rq2h eu4oa1w0"]').get()
        cmp_wll = self.tag_remover(company_wll_xpath) if rev_xpath else None
        company_dept_xpath = response.xpath('//section[@class="css-1xpzi0m eu4oa1w0"]').get()
        dept_rting = self.tag_remover(company_dept_xpath) if rev_xpath else None
        review_url = 'https:www.indeed.com' + response.xpath('//li[@data-testid="reviews-tab"]//a/@href').get()
        # about_url = 'https:www.indeed.com' + response.xpath('//li[@data-tn-element="about-tab"]/a/@href').get()

        return {
            'company_name': company_name,
            'company_page_link': company_page_link,
            'company_ID': company_ID,
            'company_logo': company_logo,
            'company_website_link': company_website_link,
            'ceo': ceo,
            'ceo_performance': ceo_performance,
            'founded': founded,
            'company_size': company_size,
            'revenue': revenue,
            'industry': industry,
            'headquarters': headquarters,
            'salaries': salaries,
            'review_main_page': rev,
            'QnA': fn_qna,
            'Company_Department_Rating': dept_rting,
            'Company_Wellbeing': cmp_wll,
            'company_description': company_description
        }

    def extract_review_data(self, response):
        # Extract review data as before
        review_list = response.xpath('//div[@class="css-lw17hn eu4oa1w0"]')
        reviews_cnt = response.xpath('//div[@data-testid="review-count"]/a/text()').get()
        if reviews_cnt is not None:
            reviews_count = reviews_cnt.split(" ")[2]
        else:
            reviews_count = None
        reviews_by_category = response.xpath(
            '//div[@class="css-xpga8e eu4oa1w0"]/div[@class="css-19hfeub eu4oa1w0"]/a/@aria-label').getall()
        reviewer_name = review_list.xpath('//div[@class="css-8a5o2x e1wnkr790"]//a/text()').getall()
        reviews = review_list.xpath(
            '//div[@data-tn-component="reviewDescription"]//span[@class="css-15r9gu1 eu4oa1w0"]/text()').get()
        review_desc = review_list.xpath(
            '//div[@data-testid="reviewDescription"]//span[@class="css-15r9gu1 eu4oa1w0"]/text()').getall()
        reviews_po_date = review_list.xpath('//div[@class="css-8a5o2x e1wnkr790"]').getall()
        if reviews_po_date is not None:
            reviews_posted_date = [i.split('><')[3].split('-->')[-1].split("<")[0] for i in reviews_po_date]
        else:
            reviews_posted_date = None

        return {
            'reviews_count': reviews_count,
            'reviews_by_category': reviews_by_category,
            'reviewer_name': reviewer_name,
            'reviews': reviews,
            'review_description': review_desc,
            'reviews_posted_date': reviews_posted_date,
        }
