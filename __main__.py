from GooglePlayStoreReviewCrawler import GooglePlayStoreReviewCrawler
import pymysql

if __name__ == '__main__':
    chrome_driver_url = '/Users/h/Downloads/chromedriver'
    url = 'https://play.google.com/store/apps/details?id=com.kakao.talk&hl=ko&showAllReviews=true'
    mysql = pymysql.connect(host='localhost', port=3306, user='root',
                            passwd='root', db='google_play_review', charset='utf8mb4')
    crawler = GooglePlayStoreReviewCrawler(app_name='Conects',chrome_driver_url=chrome_driver_url, url=url, conn=mysql, limit_scroll=True, limit_num=0)
    crawler.start()
    mysql.close()
