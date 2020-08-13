import requests
import time
from fake_useragent import UserAgent
from lxml import etree
import json
import csv

class XiaomiSpider:

    def __init__(self):
        self.p_url = 'http://app.mi.com/'
        self.c_url = 'http://app.mi.com/categotyAllListApi?page={}&categoryId={}&pageSize=30'
        self.two_html_url = 'http://app.mi.com/details?id={}'
        self.f = open('xiaomi_application.csv','a')
        self.csv_write = csv.writer(self.f)

    def get_html(self,url):
        """获取主页内容"""
        html = requests.get(url=url,headers={'User-Agent':UserAgent().random})
        return html.text

    def get_application_type(self):
        """获取所有应用、编号"""
        parse_html = etree.HTML(self.get_html(self.p_url))
        # 获取分类应用链接
        link_list = parse_html.xpath('/html/body/div[6]/div/div[2]/div[2]/ul/li/a/@href')
        # 获取所有应用
        application_type_list = parse_html.xpath('/html/body/div[6]/div/div[2]/div[2]/ul/li/a/text()')
        # print(link_list, application_type_list,sep='\n')
        application_list = []  # -> [(应用编号，应用类型),(),..]
        for i in range(len(link_list)):
            application_list.append((link_list[i].split('/')[-1],application_type_list[i]))
        # print(application_list)
        return application_list

    def get_application_count(self,application_num):
        """获取分类下应用数"""
        url = self.c_url.format(0,application_num)
        json_str = self.get_html(url)
        count = json.loads(json_str)['count']
        # print(count)
        return int(count)

    def get_page(self,count):
        """获取应用页码数"""
        page = count // 30 if count % 30 == 0 else count // 30 + 1
        return page

    def load_application_msg(self,application_num,application_type,application_count):
        """爬取一级页应用数据信息"""
        page = self.get_page(application_count)
        for i in range(page):
            url = self.c_url.format(i,application_num)
            json_obj = json.loads(self.get_html(url))
            self.two_html_msg(json_obj['data'],application_type)
            time.sleep(0.2)


    def two_html_msg(self,application_list,application_type):
        """爬取二级页应用信息"""
        for i in application_list:
            name = i['displayName']
            link = self.two_html_url.format(i['packageName'])
            parse_html = etree.HTML(self.get_html(link))
            score = int(parse_html.xpath('/html/body/div[6]/div[1]/div[2]/div[1]/div/div[1]/div/@class')[0].split(' ')[-1].split('-')[-1])
            score_num = int(parse_html.xpath('/html/body/div[6]/div[1]/div[2]/div[1]/div/span/text()')[0].split(' ')[1][:-3])
            self.save_application({'name':name,'type':application_type[-1],'score':score,'score_num':score_num})
            time.sleep(0.1)

    def save_application(self,application_msg):
        """数据持久化存储"""
        print(application_msg)
        name = application_msg['name']
        type = application_msg['type']
        score = application_msg['score']
        score_num = application_msg['score_num']
        score = score//2 if score % 2 == 0 else score//2 +0.5
        # print(name,type,score,score_num,end=',')
        self.csv_write.writerow([name,type,score,score_num])


    def run(self):
        """启动函数"""
        application_list = self.get_application_type()
        for i in application_list:
            application_num = application_list[0]
            application_type = application_list[1]
            application_count = self.get_application_count(application_num)
            self.load_application_msg(application_num,application_type,application_count)



if __name__ == '__main__':
    sp = XiaomiSpider()
    sp.run()
    sp.f.close()






















