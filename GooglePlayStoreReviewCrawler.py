from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re


class LimitNotMatched(Exception):
    def __init__(self, error_msg):
        super().__init__(error_msg)


class GooglePlayStoreReviewCrawler:
    """
    Google play에서 리뷰를 크롤링하는 class
    """
    def __init__(self, app_name:str, chrome_driver_url:str, url:str, conn, limit_scroll:bool = False, limit_num:int= -1, scroll_pause:int= 2):
        """

        :param app_name: 크롤링 할 어플리케이션 이름
        :param chrome_driver_url: 크롬 드라이버의 위치
        :param url: 크롤링 할 페이지 url
        :param conn: DB 연결
        :param limit_scroll: 스크롤 제한 설정
        :param limit_num: 스크롤 제한 수
        :param scroll_pause: 스크롤 동작 시 잠시 멈추는 시간

        """
        self.app_name = app_name
        self.__chrome_driver_url = chrome_driver_url
        self.url = url
        self.limit_scroll = limit_scroll
        self.limit_num = limit_num
        self.conn = conn
        self.scroll_pause = scroll_pause
        self.__make_table()

    def __make_table(self):
        """
        Table이 존재하지 않으면 생성
        :return: None
        """
        cur = self.conn.cursor()
        sql = '''
        CREATE TABLE IF NOT EXISTS {} (
            user_id VARCHAR(50),
            total_score TINYINT,
            review_score TINYINT,
            write_date DATE,
            useful_cnt SMALLINT,
            review_txt LONGTEXT
        ); 
        '''.format(self.app_name)
        cur.execute(sql)
        self.conn.commit()
        cur.close()

    def start(self):
        """
        크롤링을 진행하는 함수
        :return: None
        """
        if self.limit_scroll is False and self.limit_num != -1:
            raise LimitNotMatched("limit_scroll is False, but you enter limit_num.")

        cur = self.conn.cursor()

        driver = webdriver.Chrome(self.__chrome_driver_url)
        driver.get(self.url)

        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_cnt = 0

        while True:
            if self.limit_scroll is True and scroll_cnt >= self.limit_num:
                break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.scroll_pause)
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                try:
                    driver.find_element_by_xpath("//*[contains(@class,'U26fgb O0WRkf oG5Srb C0oVfc n9lfJ')]").click()
                except:
                    break

            last_height = new_height
            scroll_cnt += 1

        page = driver.page_source

        bs = BeautifulSoup(page, "lxml")
        rs = bs.find_all('div',{'class':'d15Mdf bAhLNe'})

        for rs_i in rs:
            name = rs_i.find('div', {'class': 'bAhLNe kx8XBd'}).find('span', {'class': "X43Kjb"}).text
            score = rs_i.find('div', {'class': 'pf5lIe'}).find('div').get('aria-label')
            total_score, review_score = re.findall('\d', score)
            date = rs_i.find('span', {'class': "p2TkOb"}).text
            date = '/'.join(re.findall('[0-9]+', date))
            useful_cnt = rs_i.find('div', {'class': 'YCMBp GVFJbb'}).find('div', {'class': "XlMhZe"}).find('div', {
                'class': "jUL89d y92BAb"}).text
            review_txt = rs_i.find('div', {'class': 'UD7Dzf'}).find('span', {'jsname': 'fbQN7e'}).text

            if len(review_txt) == 0:
                review_txt = rs_i.find('div', {'class': 'UD7Dzf'}).find('span', {'jsname': 'bN97Pc'}).text

            review_txt = review_txt.replace("'","\\'")

            sql = 'INSERT INTO {} VALUES (\'{}\',{},{},\'{}\',{},\'{}\')'.format(self.app_name, name, total_score,
                                                                     review_score, date, useful_cnt, review_txt)
            try:
                cur.execute(sql)
            except Exception as e:
                print('Error Occured in {} {} \n:{}'.format(name,date,e))
                print(sql)
        self.conn.commit()
        driver.close()
        print('Finished')



