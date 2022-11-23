from getpass import getpass

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep,time
import os


def time_converter(time: str):
    hour = 0
    times = time.split(':')
    counter = len(times)
    if counter == 2:  # 분, 초 2개만 있음
        minute = int(times[0])
        second = int(times[1])
    else:  # 시, 분, 초 모두 있음
        hour = int(times[0])
        minute = int(times[1])
        second = int(times[2])

    return hour * 3600 + minute * 60 + second


class Lecture:
    def __init__(self, inner_lecs):
        self.inner_lectures = inner_lecs
        self.inner_idx = 0

    def __repr__(self):
        ret = ""
        for i in self.inner_lectures:
            ret += f"내부 강의 잔여 시간(초): {i}\n"
        return ret

class AutomaticAttendance:
    def __init__(self):
        opt = webdriver.ChromeOptions()
        opt.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opt)
        self.driver.get("https://eclass.seoultech.ac.kr/ilos/main/main_form.acl")
        self.driver.implicitly_wait(time_to_wait=3)
        self.id: str
        self.pw: str

    def EndProcess(self):
        self.driver.close()

    def Login(self):
        self.id = input("ID를 입력하세요: ")
        self.pw = getpass()
        print('\n'*200)

        # login
        self.driver.find_element(By.CLASS_NAME, "header_login.login-btn-color").click()
        sleep(0.3)
        self.driver.find_element(By.ID, "usr_id").send_keys(self.id)
        sleep(0.3)
        self.driver.find_element(By.ID, "usr_pwd").send_keys(self.pw)
        sleep(0.3)

        self.driver.find_element(By.CLASS_NAME, "btntype").click()

        os.system('cls' if os.name in ('nt', 'dos') else 'clear')

        try:
            popup = self.driver.find_elements(By.NAME, "doneclose")  # 팝업창 다시 보지 않기 버튼 찾기
            for x in popup:
                x.click()  # 전부 누르기
        except:
            pass

    def Attendance(self):
        # to do list로 들어가기
        sleep(1)
        self.driver.find_element(By.XPATH, "//*[@id=\"header\"]/div[4]/div/fieldset/div/div[2]").click()
        sleep(1)
        # 온라인 강의 클릭
        self.driver.find_element(By.XPATH, "//*[@id=\"todo_pop\"]/div/div[1]/div[2]/div[1]").click()
        sleep(1)
        # 맨 위의 강의 클릭
        self.driver.find_element(By.CLASS_NAME, "todo_wrap.on").click()
        sleep(0.5)
        # 시간 측정
        lecture_elements = self.driver.find_elements(By.CLASS_NAME, "lecture-box")
        lectures = []
        for lec in lecture_elements:
            inner_lectures = []
            try:
                for i in range(1, 10):
                    lis_time, play_time = lec.find_element(By.XPATH,
                                                           f"div/ul/li[1]/ol/li[5]/div/div[{i}]/div[2]/div[3]").text.split(
                        '/')
                    print(f"들은 시간: {lis_time}, 남은 시간: {play_time}")
                    inner_lectures.append(time_converter(play_time) - time_converter(lis_time))
            finally:
                lectures.append(Lecture(inner_lectures))
                continue

        for idx, cur in enumerate(lectures):
            print(cur)
            # 학습 하기 버튼 클릭
            sleep(1)
            self.driver.find_elements(By.CLASS_NAME, "view")[idx].click()
            sleep(3)
            inner_count = len(cur.inner_lectures)

            while True:
                # 남은 시간이 0보다 클 때만 수강
                if cur.inner_lectures[cur.inner_idx] > 0:
                    # 영상 재생 iframe 안으로 이동
                    self.driver.switch_to.frame(self.driver.find_element(By.TAG_NAME, "iframe"))
                    sleep(0.3)
                    # 재생 버튼 클릭
                    self.driver.find_element(By.CLASS_NAME, "vc-front-screen-play-btn").click()
                    # 출석 시간 + 10초 만큼 잠들기
                    sleep(cur.inner_lectures[cur.inner_idx] + 10)

                # 강의 idx++
                cur.inner_idx += 1
                if cur.inner_idx == inner_count:  # 내부 강의를 다 들으면 종료
                    sleep(1)
                    break
                # iframe 빠져 나오기
                self.driver.switch_to.default_content()
                # 다음 강의로 이동 버튼 누르기
                self.driver.find_element(By.ID, "next_").click()
                sleep(1)

            # 출석(종료) 버튼 누르기
            self.driver.switch_to.default_content()
            self.driver.find_element(By.ID, "close_").click()


if __name__ == "__main__":
    a = AutomaticAttendance()
    a.Login()
    while True:
        a.Attendance()
        try:
            while True:
                a.Attendance()
        finally:
            a.EndProcess()
