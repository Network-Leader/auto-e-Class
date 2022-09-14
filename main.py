from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep


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
        return str(self.inner_lectures)


class AutomaticAttendance:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get("https://eclass.seoultech.ac.kr/ilos/main/main_form.acl")
        self.driver.implicitly_wait(time_to_wait=3)
        self.id: str
        self.pw: str

    def EndProcess(self):
        self.driver.close()

    def Login(self):
        self.id = input("ID를 입력하세요: ")
        self.pw = input("비밀번호를 입력하세요: ")

        # login
        self.driver.find_element(By.CLASS_NAME, "header_login.login-btn-color").click()

        self.driver.find_element(By.ID, "usr_id").send_keys(self.id)
        self.driver.find_element(By.ID, "usr_pwd").send_keys(self.pw)

        self.driver.find_element(By.CLASS_NAME, "btntype").click()

    def Attendance(self):
        # to do list로 들어가기
        self.driver.find_element(By.XPATH, "//*[@id=\"header\"]/div[4]/div/fieldset/div/div[2]").click()
        # 온라인 강의 클릭
        self.driver.find_element(By.XPATH, "//*[@id=\"todo_pop\"]/div/div[1]/div[2]/div[1]").click()
        # 맨 위의 강의 클릭
        self.driver.find_element(By.CLASS_NAME, "todo_wrap.on").click()
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
                    print(lis_time, play_time)
                    inner_lectures.append(time_converter(play_time) - time_converter(lis_time))
            finally:
                lectures.append(Lecture(inner_lectures))
                continue

        for idx, cur in enumerate(lectures):
            print(cur)
            # 학습 하기 버튼 클릭
            self.driver.find_elements(By.CLASS_NAME, "view")[idx].click()
            sleep(3)
            inner_count = len(cur.inner_lectures)
            while True:
                # 남은 시간이 0보다 클 때만 수강
                if cur.inner_lectures[cur.inner_idx] > 0:
                    # 영상 재생 iframe 안으로 이동
                    self.driver.switch_to.frame(self.driver.find_element(By.TAG_NAME, "iframe"))
                    # 재생 버튼 클릭
                    self.driver.find_element(By.CLASS_NAME, "vc-front-screen-play-btn").click()
                    # 출석 시간 + 10초 만큼 잠들기
                    sleep(cur.inner_lectures[cur.inner_idx] + 200)

                # 강의 idx++
                cur.inner_idx += 1
                if cur.inner_idx == inner_count:  # 내부 강의를 다 들으면 종료
                    break
                # iframe 빠져 나오기
                self.driver.switch_to.default_content()
                # 다음 강의로 이동 버튼 누르기
                self.driver.find_element(By.CLASS_NAME, "contents-view-btn.contents-view-btn-right").click()

            # 내부 강의 개수 만큼 뒤로 가기
            for i in range(inner_count):
                self.driver.back()


if __name__ == "__main__":
    a = AutomaticAttendance()
    a.Login()
    try:
        while True:
            a.Attendance()
    finally:
        a.EndProcess()
