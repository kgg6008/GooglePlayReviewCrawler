from GooglePlayStoreReviewCrawler import GooglePlayStoreReviewCrawler
from AppStoreReviewCrawler import AppStoreReviewCrawler
import pymysql

if __name__ == '__main__':
    chrome_driver_url = '/Users/hh/Downloads/chromedriver'
    # Crawling Google playstore review
    url = 'google_review_url'
    mysql = pymysql.connect(host='localhost', port=3306, user='root',
                            passwd='1234', db='google_play_review', charset='utf8mb4')
    crawler = GooglePlayStoreReviewCrawler(app_name='app_name',chrome_driver_url=chrome_driver_url, url=url, conn=mysql, limit_scroll=True, limit_num=0)
    crawler.start()
    mysql.close()
    # Crawling Apple  Appstore review
    url = 'apple_review_url'
    mysql = pymysql.connect(host='localhost', port=3306, user='root',
                            passwd='1234', db='app_store_review', charset='utf8mb4')
    crawler = AppStoreReviewCrawler(app_name='app_name', chrome_driver_url=chrome_driver_url, url=url, conn=mysql,
                                           limit_scroll=False, scroll_pause=5)
    crawler.start()
    mysql.close()
