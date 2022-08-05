import streamlit as st
import numpy as np
import pandas as pd
import requests
from lxml import etree
from LAC import LAC
import re
import json
import time

st.set_page_config(page_title="医药公司人物信息查询", layout="wide")
st.title("医药公司人物信息查询")
def progress(percentage):
    my_bar.progress(percentage)
    

st.write('  ')
st.write('  ')
st.write('###### 点击左上角小箭头，在侧边栏输入网址！')
st.write('##### 请等待进度条的加载完！')
my_bar=st.progress(0)#进度条初始
url = st.sidebar.text_input('请输入爬取网址url，然后按回车键','')
# url = 'https://www.nuwacell.com/'
time.sleep(10)
myheaders={'User-Agent':"Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11"}
st.write('您输入网址url是：',url)
res = requests.get(url,headers=myheaders)
html = etree.HTML(res.text)
childs = html.xpath('./*')#存父类节点
progress(5)#进度5%
for child in childs:
    node_list1 = child.xpath("//*[contains(text(),'Leadership') or contains(text(),'Team') or contains(text(),'管理团队') or contains(text(),'团队介绍')]")
    node_list2 = child.xpath("//*[contains(text(),'团队') or  contains(text(),'管理') or contains(text(),'专家')]")

if node_list1 :#如果存在关键词网页
    if len(node_list1[0].xpath("./@href")):
        link = node_list1[0].xpath("./@href")  # 定位人物的链接,都是列表
        corporation = childs[0].xpath('//head/title/text()')  # 用初始的根节点公司名，列表
        if not str(link[0]).startswith('http'):
            link = url + str(link[0])#变成字符串
        else:
            link = str(link[0])#变成字符串

    elif len(node_list1[0].xpath('../@href')):
        link = node_list1[0].xpath("../@href")  # 定位人物的链接,都是列表
        corporation = childs[0].xpath('//head/title/text()')  # 用初始的根节点公司名，列表
        if not str(link[0]).startswith('http'):
            link = url + str(link[0])  # 变成字符串
        else:
            link = str(link[0])  # 变成字符串

elif node_list2:
    if len(node_list2[0].xpath("./@href")):
        link = node_list2[0].xpath("./@href")  # 定位人物的链接,都是列表
        corporation = childs[0].xpath('//head/title/text()')  # 用初始的根节点公司名，列表
        if not str(link[0]).startswith('http'):
            link = url + str(link[0])#变成字符串
        else:
            link = str(link[0])#变成字符串

    elif len(node_list2[0].xpath('../@href')):
        link = node_list2[0].xpath("../@href")  # 定位人物的链接,都是列表
        corporation = childs[0].xpath('//head/title/text()')  # 用初始的根节点公司名，列表
        if not str(link[0]).startswith('http'):
            link = url + str(link[0])  # 变成字符串
        else:
            link = str(link[0])  # 变成字符串
else:
    progress(100)  # 进度100
    st.success("抱歉，你所爬取的网站人员信息不存在！")

try :
    if link:
        st.write("请耐心等待!")
except:
    pass

if link != '':
    file = open("people.json", 'w').close()#初始清空文本
    progress(20)#进度20
    res2 = requests.get(link,headers=myheaders)#再爬起有人物信息的网站
    html2 = etree.HTML(res2.text)
    childs2 = html2.xpath('./*')
    node_list = childs2#存父节点列表
    while len(node_list) > 0:
        node = node_list.pop(0)
        childs = node.xpath('./*')
        # corporation = node.xpath('//head/title/text()')# 公司名
        # corporation = ''.join(str(corporation[0]).split())  # 去括号
        # progress(20)#进度条20%
        for child in childs:
            node_list.append(child)
            info = child.xpath(".//text()")  # 列表中存在字符串，存在姓名与简介

            if len(info) == 0:
                continue
            lac = LAC(mode="lac")  # 标准模式
            # # info = ' '.join(list)#将列表里内容去括号，还是列表
            # # info = ','.join(info)#将列表用逗号连接成字符串
            info = [x.strip() for x in info if x.strip()]  # 列表去空格，返回列表

            if len(info) == 0:  # 再去一次空列表
                continue
            if len(info) > 7:  # 除掉过长的列表
                continue
            # print(info)
            count = 0  # 计人名个数
            for i in info: #遍历可能存在人名的列表
                if len(i) < 10:  # 名字长度小于10才去判断是否是人名
                    lac_result = lac.run(i)  # 传入姓名,字符串类型
                    # lac_result列表形式[['研发', '创新'], ['vn', 'vn']]
                    for index, lac_label in enumerate(lac_result[1]):
                        if (lac_label) == "PER":
                            count += 1

            if count == 1:#如果只存在一个名字，说明改list说我们要的信息
                item={}
                name = info[0]
                info.pop(0)
                if len(info) != 0:
                    item['name'] = name  # 姓名
                    item['info'] = ','.join(info)  # 简介
                    item['corporation'] = corporation[0].strip()
                    item['link'] = url
                    try:
                        with open('people.json', 'a', encoding="utf-8") as fp:
                            fp.write(json.dumps(item, ensure_ascii=False) + ",\n")

                    except IOError as err:
                        print('error' + str(err))
                    finally:
                        progress(60)  # 进度60
                        fp.close()

    progress(90)#进度9%
    with open(r'people.json', 'r+', encoding='utf-8') as file:
        data = file.readlines()  # 字符串每一行
        exist_name_list = []  # 人名
        non_repeat_list = []  # 信息
        if data != '':
            for i in data:
                name = re.match(r'{"name":.*?,', i.strip())  # 前正则式，后字符串
                if name.group() in exist_name_list:  # 已经存在同名结果
                    continue
                else:
                    exist_name_list.append(name.group())
                    non_repeat_list.append(i.strip())
            file.close()
            non_repeat_list[-1] = non_repeat_list[-1].rstrip(",")
            f = open(r"people.json", "w+", encoding='utf-8')
            f.write('[')
            f.write('\n'.join(map(str, non_repeat_list)))
            f.write(']')
            f.close()
            shows = pd.read_json('people.json')
            shows
            progress(100)#进度100%
            st.success("全部步骤执行完毕！")
        else:
            progress(100)  # 进度100%
            st.success("抱歉，你所爬取的网站人员信息不存在！")
