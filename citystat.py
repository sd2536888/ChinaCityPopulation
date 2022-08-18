#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import hashlib
import os
import time
import csv


class CityStat:
    def get_url_from_cache(self, url, name=""):
        if name == "晋州市":
            url = url + "_(中华人民共和国)"

        print(url)
        result = hashlib.md5(url.encode())
        print(result.hexdigest())
        file = "cache/" + result.hexdigest() + ".txt"
        if os.path.exists(file):
            f = open(file)
            text = f.read()
            f.close()
        else:
            # 走代理
            proxies = {"http": "http://127.0.0.1:1081", "https": "http://127.0.0.1:1081", }
            response = requests.get(url, proxies=proxies)
            text = response.text
            f = open(file, "w")
            f.write(text)
            f.close()

        return text

    # Get the city list in China.
    def get_city_list(self):
        url = "https://zh.wikipedia.org/zh-cn/%E4%B8%AD%E5%8D%8E%E4%BA%BA%E6%B0%91%E5%85%B1%E5%92%8C%E5%9B%BD%E5%9F%8E%E5%B8%82%E5%88%97%E8%A1%A8"

        text = self.get_url_from_cache(url)

        soup = BeautifulSoup(text, "lxml")
        divs = soup.findAll("li")
        result = []
        is_break = 0
        for l in divs:
            if u'地级市' in l.text.strip() or u'县级市' in l.text.strip() or u'副省级市' in l.text.strip() or u'省直辖县级市' in l.text.strip():
                type_str = ""
                if u'地级市' in l.text.strip():
                    type_str = "地级市"
                if u'县级市' in l.text.strip():
                    type_str = "县级市"
                if u'副省级市' in l.text.strip():
                    type_str = "副省级市"
                if u'省直辖县级市' in l.text.strip():
                    type_str = "省直辖县级市"

                lists = l.findAll('a')
                for value in lists:
                    if value.text.strip() == "自治区直辖县级市" or value.text.strip() == "副省级市" or value.text.strip() == "地级市" or value.text.strip() == "副地级市":
                        continue
                    print(value, value.attrs)
                    if "href" in value.attrs:
                        result.append([value["href"], value.text.strip(), type_str])
                    if value.text.strip() == "胡杨河市":
                        is_break = 1
                        break
                if is_break:
                    break
        print(len(result))
        return result

    def get_city_info(self):
        city_list = self.get_city_list()
        prefix_url = "https://zh.wikipedia.org"
        city_info_list = []
        for index, (url, name, type_str) in enumerate(city_list):
            try:
                city_info_list = self.process_each_city(prefix_url + url, name, type_str, city_info_list)
            except Exception as err:
                print("Error:" + err)
                print("Error:" + url)
        return city_info_list

    def get_big_city_info(self, text, name, city_info_list):
        if name == "宁波市":
            return city_info_list

        if name == "青岛市":
            city_info_list.append(["青岛市", "370200", "10071700"])
            city_info_list.append(["市南区", "370202", "486600"])
            city_info_list.append(["市北区", "370203", "1096900"])
            city_info_list.append(["黄岛区", "370211", "1903600"])
            city_info_list.append(["崂山区", "370212", "502400"])
            city_info_list.append(["李沧区", "370213", "737300"])
            city_info_list.append(["城阳区", "370214", "1106900"])
            city_info_list.append(["即墨区", "370215", "1336100"])
            city_info_list.append(["胶州市", "370281", "987800"])
            city_info_list.append(["平度市", "370283", "1191300"])
            city_info_list.append(["莱西市", "370285", "720100"])
            return city_info_list
        if name == "嘉峪关市":
            city_info_list.append(["嘉峪关市", "620200", "231853"])
            return city_info_list
        if name == "儋州市":
            city_info_list.append(["儋州市", "460400", "932362"])
            return city_info_list
        if name == "中山市":
            city_info_list.append(["中山市", "442000", "4418060"])
            return city_info_list
        if name == "东莞市":
            city_info_list.append(["东莞市", "441900", "10466625"])
            return city_info_list
        if name == "三沙市":
            city_info_list.append(["三沙市", "460300", "1800"])
            city_info_list.append(["西沙区", "460321", "1800"])
            city_info_list.append(["南沙区", "460322", "0"])
            city_info_list.append(["中沙群岛", "460323", "0"])
            return city_info_list

        soup = BeautifulSoup(text, "lxml")

        table = soup.findAll(name="table", attrs={"class": "wikitable"})
        for index in range(len(table)):
            tb = table[index]
            if table[index].find("th") is None:
                continue
            title = tb.find("th").text
            # 行政区划图
            if title[-6:] != "行政区划图\n":
                continue

            trs = tb.findAll("tr")
            title_th = trs[2].findAll("th")
            population_index = 0
            for i in range(len(title_th)):
                if u'人口' in title_th[i].text.strip():
                    population_index = i - 2
                    break
            if name == "台州市":
                population_index = 4

            for index_tr in range(len(trs)):
                if index_tr < 4:
                    continue
                tr_text = trs[index_tr].text
                tr_th = trs[index_tr].findAll("th")
                tr_td = trs[index_tr].findAll("td")
                if len(tr_th) == 2 and 7 <= len(tr_td) <= 10:
                    city_code = tr_th[0].text
                    city_name = tr_th[1].text.replace("\n", "")
                    city_population = tr_td[population_index].text
                    city_population = city_population.split(u'[')[0]
                    print(city_name, city_code, city_population)
                    city_info_list.append([city_name, city_code, city_population])
            break
        return city_info_list

    def get_small_city_info(self, text, city_name, city_info_list):
        soup = BeautifulSoup(text, "lxml")

        table = soup.findAll(name="table", attrs={"class": re.compile(r'infobox.*vcard')})
        trs = table[0].findAll("tr")
        city_code = 0
        city_population = 0

        if city_name == "满洲里市":
            city_population = "250000"
        elif city_name == "延吉市":
            city_population = "700000"
        elif city_name == "江阴市":
            city_population = "1653400"
        elif city_name == "义乌市":
            city_population = "1885000"
        elif city_name == "乐清市":
            city_population = "1428500"
        elif city_name == "武夷山市":
            city_population = "233557"
        elif city_name == "石狮市":
            city_population = "314945"
        elif city_name == "共青城市":
            city_population = "220000"
        elif city_name == "武夷山市":
            city_population = "233557"
        elif city_name == "仙桃市":
            city_population = "1134700"
        elif city_name == "天门市":
            city_population = "1158600"
        elif city_name == "潜江市":
            city_population = "886547"
        elif city_name == "台山市":
            city_population = "968000"
        elif city_name == "浏阳市":
            city_population = "1278928"
            city_code = "430181"
        elif city_name == "潜江市":
            city_population = "886547"
        elif city_name == "什邡市":
            city_population = "1432579"
        elif city_name == "西昌市":
            city_population = "608300"
        elif city_name == "射洪市":
            city_population = "972400"

        for tr in trs:
            th = tr.find("th")
            td = tr.find("td")
            if city_code == 0 and th is not None and u'区划代码' in th.text.strip():
                city_code = td.text.strip()
            if city_population == 0 and th is not None and u'总人口' in th.text.strip():
                number = td.text.strip()
                if u'约' in td.text.strip() and u'万' in td.text.strip():
                    search_obj = re.search(r'约(\d+)万.*', td.text.strip(), flags=0)
                    city_population = str(int(search_obj.group(1)) * 10000)
                elif u'万' in td.text.strip():
                    if u'（' in number:
                        number = number.split(u'（')[0]
                    if u'常住人口' in number:
                        number = number.split(u'常住人口')[1]
                    number = number.split(u'万')[0]
                    number = number.split(u'[')[0]
                    number = number.strip().replace(',', '')
                    city_population = str(int(float(number) * 10000))
                else:
                    number = number.split(u'[')[0]
                    city_population = number.strip()
                break
            elif th is not None and u'人口' == th.text.strip():
                td = th.parent.next_sibling.find("td")
                city_population = td.text.strip().split(u'人')[0]
        print(city_name, city_code, city_population)
        city_info_list.append([city_name, city_code, city_population])
        return city_info_list

    def process_each_city(self, url, name, type_str, city_info_list):
        if type_str != "地级市":
            return city_info_list

        # if name != "台州市":
        # 	return cityInfoList

        text = self.get_url_from_cache(url, name)

        if type_str == "地级市" or type_str == "副省级市":
            city_info_list = self.get_big_city_info(text, name, city_info_list)
            return city_info_list

        city_info_list = self.get_small_city_info(text, name, city_info_list)

        return city_info_list

    def write_to_file(self, city_info_list):
        with open('citystatInfo_' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["名称", "区域代码", "人口"])
            for (name, city_code, number) in city_info_list:
                writer.writerow([name, city_code, number])


if __name__ == '__main__':
    cityStat = CityStat()
    cityInfoList = cityStat.get_city_info()
    cityStat.write_to_file(cityInfoList)
