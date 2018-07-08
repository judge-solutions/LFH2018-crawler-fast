# coding:utf-8
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from elasticsearch import Elasticsearch
from selenium import webdriver

es = Elasticsearch()

"""
    LawTech Hackathon 2018
    AIRR

    The MIT License (MIT)

    Copyright (c) 2014-2015 almasaeed2010

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""


class Crawler(object):
    def __init__(self):
        self.capabilities = {
            "platform": "LINUX",
            "browserName": "firefox",
            "enableVNC": True
        }

        self.driver = webdriver.Remote(
            desired_capabilities=self.capabilities,
            command_executor='http://localhost:4444/wd/hub'
        )

        #
        # https://github.com/aerokube/selenoid
        # SELENOID É A IMPLEMENTAÇÃO EM GO DO SERVIDOR SELENIUM, 10X MAIS RAPIDA QUE A IMPLEMENTAÇÃO ORIGINAL (JAVA)
        #

        self.browser = requests.Session()
        self.browser.get("http://busca.tjsc.jus.br/jurisprudencia/busca.do")

    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def text_from_html(self, body):
        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(self.tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)

    def get_acordao(self, pags):
        t = datetime.now()

        self.driver.get(
            "http://busca.tjsc.jus.br/jurisprudencia/busca.do")
        for i in range(1, pags + 1):
            print(i)

            divs_res = self.driver.find_elements_by_class_name("resultados")
            for div in divs_res:
                a = div.find_elements_by_class_name("icones")[-3]
                soup = BeautifulSoup(a.get_attribute('innerHTML'), "lxml")
                ref = soup("a")[0]["href"]
                print(ref)
                result = requests.get(
                    "http://busca.tjsc.jus.br/jurisprudencia/" + ref)

                body = {
                    "acordao": self.text_from_html(result.text)
                }

                es.index(index="acordaos", doc_type="_doc", body=body)

            el = self.driver.find_element_by_id("paginacao")
            _el = el.find_elements_by_tag_name("li")[-1]
            _el.click()
            time.sleep(2)

        elapsed_time = datetime.now() - t

        print(elapsed_time)


if __name__ == "__main__":
    crawler = Crawler()
    crawler.get_acordao(5)
