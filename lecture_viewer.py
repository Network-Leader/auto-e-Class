from login_session import LoginSession
from lecture import Lecture

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

import time
import os
import unicodedata


class LectureViewer:
    def __init__(self, login: LoginSession):
        self.login = login

        opts = webdriver.ChromeOptions()
        opts.add_argument("--log-level=3")
        opts.add_argument(f"user-agent={login.USER_AGENT}")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=opts
        )
        self.driver.implicitly_wait(30)

    def __enter__(self):
        self.driver.get(f"https://{self.login.HOST}{self.login.PATH_MAIN}")
        self.driver.add_cookie(
            {
                "name": "WMONID",
                "value": self.login.wmonid,
                "domain": self.login.HOST,
            }
        )
        self.driver.add_cookie(
            {
                "name": "LMS_SESSIONID",
                "value": self.login.sessionid,
                "domain": self.login.HOST,
            }
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()

    def __mute(self):
        try:
            volume_button = self.driver.find_element(
                By.CLASS_NAME, "vc-pctrl-volume-btn"
            )
            if "muted" not in volume_button.get_attribute("class").split():
                volume_button.click()
            return True
        except NoSuchElementException:
            return False

    def __play(self) -> bool:
        try:
            iframe = self.driver.find_element(By.TAG_NAME, "iframe")
            self.driver.switch_to.frame(iframe)
            self.driver.find_element(By.CLASS_NAME, "vc-front-screen-play-btn").click()
            self.driver.switch_to.default_content()
            return True
        except NoSuchElementException:
            return False

    def __report_lecture(self, class_name: str, week_no: int):
        print()
        print(f"[{class_name}] {week_no}주차 강의")

    def __report_progress(self, lecture_name: str, progress: float):
        width, _ = os.get_terminal_size()
        lecture_name_count = len(lecture_name) + sum(
            1 for c in lecture_name if unicodedata.east_asian_width(c) in "WF"
        )
        square = "\u2588"
        square_count = int(progress * width)
        blank = "\u2591"
        blank_count = (
            width - lecture_name_count - 2 - square_count - 8
        )  # 2 for ': ', 8 for ' 100.00% '
        print(
            f"\r{lecture_name}: {square * square_count}{blank * blank_count} {progress * 100: 3.2f}%",
            end="",
        )

    def view(self, lecture: Lecture):
        self.driver.get(lecture.get_baseurl())
        self.driver.find_element(
            By.CSS_SELECTOR, f"#lecture-{lecture.lecture_id} img.view"
        ).click()
        titles: list[str] = []
        title_elements = self.driver.find_elements(
            By.CSS_SELECTOR, "div.item-title-lesson"
        )
        for e in title_elements:
            titles.append(e.text)
        self.__report_lecture(lecture.class_name, lecture.week_no)
        for idx, (cur, tot) in enumerate(lecture.times):
            self.__mute()
            self.__play
            while cur <= tot:
                self.__report_progress(titles[idx], cur / tot)
                cur += 0.1
                time.sleep(0.1)
            print()
            if idx < len(lecture.times) - 1:
                self.driver.find_element(By.ID, "next_").click()
        self.driver.find_element(By.ID, "close_").click()


if __name__ == "__main__":
    from lecture_browser import LectureBrowser

    with LoginSession() as login, LectureViewer(login) as viewer:
        browser = LectureBrowser(login)
        lectures = browser.get_lectures()
        for lecture in lectures:
            viewer.view(lecture)