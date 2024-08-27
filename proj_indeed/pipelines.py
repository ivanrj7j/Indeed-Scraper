# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from scrapy.pipelines.images import ImagesPipeline
# from slugify import slugify
# class CustomImagesPipeline(ImagesPipeline):
#     def file_path(self,request,response=None,info=None,*,item=None):
#         file_name= slugify(item['company_Name'],max_length=200)
#         return f'full/{file_name}.jpg'
