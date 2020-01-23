from GooglePlayStoreReviewCrawler import GooglePlayStoreReviewCrawler
from AppStoreReviewCrawler import AppStoreReviewCrawler
import pymysql

if __name__ == '__main__':
    chrome_driver_url = '/Users/h/Downloads/chromedriver'
    # # Crawling Google playstore review
    # url = 'https://play.google.com/store/apps/details?id=com.kakao.talk&hl=ko&showAllReviews=true'
    # mysql = pymysql.connect(host='localhost', port=3306, user='root',
    #                         passwd='root', db='google_play_review', charset='utf8mb4')
    # crawler = GooglePlayStoreReviewCrawler(app_name='Conects',chrome_driver_url=chrome_driver_url, url=url, conn=mysql, limit_scroll=True, limit_num=0)
    # crawler.start()
    # mysql.close()
    # Crawling Apple  Appstore review
    url = 'https://apps.apple.com/kr/app/%EC%BB%A4%EB%84%A5%EC%B8%A0-500%EB%A7%8C-%EB%8B%A4%EC%9A%B4%EB%A1%9C%EB%93%9C-%EC%A0%84%EA%B3%BC%EB%AA%A9-%EC%8B%A4%EC%8B%9C%EA%B0%84-%EC%A7%88%EB%AC%B8%EB%8B%B5%EB%B3%80-%EC%95%B1/id1435555792#see-all/reviews'
    mysql = pymysql.connect(host='localhost', port=3306, user='root',
                            passwd='root', db='app_store_review', charset='utf8mb4')
    crawler = AppStoreReviewCrawler(app_name='Conects', chrome_driver_url=chrome_driver_url, url=url, conn=mysql,
                                           limit_scroll=True, limit_num=0)
    crawler.start()
    mysql.close()