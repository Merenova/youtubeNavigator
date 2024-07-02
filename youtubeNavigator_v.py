from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import time
import re
import json

class youtubeNavigator:

    def __init__(self):
        self.history = []
        self.tmp_locator = []

        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless') 
        chrome_options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get('https://www.youtube.com/')
        self.driver.set_window_size(1920, 1080)

        #choose language from Korean to English (US)
        settings_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="button" and @class="style-scope yt-icon-button" and @aria-label="설정"]')))
        settings_button.click()
        time.sleep(1)
        language_option = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//yt-formatted-string[text()="언어:"]')))
        language_option.click()
        time.sleep(1)
        english_option = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//yt-formatted-string[text()="English (US)"]')))
        english_option.click()
        time.sleep(3)
        print('Changed language to English')

        #choose location to US
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        settings_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="button" and @class="style-scope yt-icon-button" and @aria-label="Settings"]')))
        settings_button.click()
        time.sleep(1)
        location_option = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[contains(text(), "Location:")]')))
        location_option.click()
        time.sleep(1)
        united_states_option = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//yt-formatted-string[text()="United States"]')))
        united_states_option.click()
        time.sleep(3)
        print('Changed location to US')

    def save_html(self, name):
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        html_code = soup.prettify()
        with open(f'{name}.html','w') as f:
            f.write(html_code)

    def save_screenshot(self, name):
        self.driver.save_screenshot(f'{name}.png')

    def convert_place_val(self, view_text):
        place_val_dict = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000}
        number_text = view_text.split(' ')[0]
        place_val = 1
        if number_text[-1] in place_val_dict.keys():
            place_val = place_val_dict[number_text[-1]]
            number_text = number_text[:-1]
        fix_number = float(number_text)
        return int(fix_number * place_val)

    def search(self, query):
        search_box = self.driver.find_element(By.NAME, 'search_query')
        search_box.clear()
        search_box.send_keys(query)
        search_box.submit()
        time.sleep(5)
        video_data = []
        search_results = self.driver.find_elements(By.XPATH, '//*[@class="style-scope ytd-video-renderer" and @id="dismissible"]')
        for i, result in enumerate(search_results):
            video_title = result.find_element(By.TAG_NAME, 'yt-formatted-string').text
            thumbnail_link = result.find_element(By.TAG_NAME, 'img').get_attribute('src')
            count_text = result.find_element(By.CLASS_NAME, 'inline-metadata-item.style-scope.ytd-video-meta-block').text
            is_live = True if 'watching' in count_text else False
            count = self.convert_place_val(count_text)
            video_data.append({'id': i, 'video_title': video_title, 'thumbnail_link': thumbnail_link, 'is_live': is_live, 'count': count, 'locator': result})
        self.tmp_locator = video_data
        return video_data

    def related_videos(self):
        # wait unitl related videoes come out
        WebDriverWait(self.driver, 20).until(EC.element_attribute_to_include((By.TAG_NAME, 'img'), 'src'))
        video_data = []
        related_videos = self.driver.find_elements(By.XPATH, '//*[@class="style-scope ytd-compact-video-renderer" and @id="dismissible"]')
        for i, related_video in enumerate(related_videos[:10]):
            video_title = related_video.find_element(By.ID, 'video-title').text
            thumbnail_link = related_video.find_element(By.TAG_NAME, 'img').get_attribute('src')
            #First occurrence is 'views' or 'watching', upload date second.
            count_text = related_video.find_element(By.CLASS_NAME, 'inline-metadata-item.style-scope.ytd-video-meta-block').text
            is_live = True if 'watching' in count_text else False
            count = self.convert_place_val(count_text)
            video_data.append({'id': i, 'video_title': video_title, 'thumbnail_link': thumbnail_link, 'is_live': is_live, 'count': count, 'locator': related_video})
        self.tmp_locator = video_data
        return video_data

    def navigate_video(self, video_id):
        self.tmp_locator[int(video_id)]['locator'].find_element(By.ID, 'video-title').click()
        time.sleep(3)
        self.save_screenshot('navigate')
        return self.related_videos()

    def finish(self):
        self.driver.quit()
        return self.history

if __name__ == "__main__":
    navi = youtubeNavigator()
    result = navi.search('python')
    print(result[1]['video_title'])
    navi.navigate_video(1)


    