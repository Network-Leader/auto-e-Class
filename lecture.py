from login_session import LoginSession
from bs4 import BeautifulSoup


def convert_time(time: str):
    hours, mins, secs = 0, 0, 0
    counters = time.split(":")
    if len(counters) == 3:
        hours, mins, secs = map(int, counters)
    elif len(counters) == 2:
        hours = 0
        mins, secs = map(int, counters)
    return hours * 3600 + mins * 60 + secs


class Lecture:
    HOST = "eclass.seoultech.ac.kr"
    PATH_TODOCONNECT = "/ilos/mp/todo_list_connect.acl"
    PATH_ONLINE_LIST = "/ilos/st/course/online_list.acl"

    def __init__(self, class_id: str, lecture_id: str, login: LoginSession):
        self.class_id = class_id
        self.lecture_id = lecture_id
        self.times = []

        res = login.session.get(self.get_baseurl())
        href = res.text.split('"')[1]
        queries = href.split("?")[1]
        query = dict(q.split("=") for q in queries.split("&"))
        self.week_no = int(query["WEEK_NO"])

        res = login.session.get(f"https://{self.HOST}{href}")
        soup = BeautifulSoup(res.text, "html.parser")
        self.class_name = soup.select("#subject-span")[0].text.strip()

        body = {
            "ud": login.studentid,
            "ky": class_id,
            "WEEK_NO": self.week_no,
            "encoding": "utf-8",
        }
        res = login.session.post(
            f"https://{self.HOST}{self.PATH_ONLINE_LIST}", data=body
        )
        soup = BeautifulSoup(res.text, "html.parser")
        timestamps = soup.select(f"div[id^=progressbar_{lecture_id}] + #per_text + div")
        for timestamp in timestamps:
            cur, tot = map(convert_time, timestamp.text.split("/"))
            self.times.append((cur, tot))

    def get_baseurl(self):
        params = {
            "SEQ": self.lecture_id,
            "gubun": "lecture_weeks",
            "KJKEY": self.class_id,
        }
        baseurl = f"https://{self.HOST}{self.PATH_TODOCONNECT}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        return baseurl


if __name__ == "__main__":
    from lecture_browser import LectureBrowser

    with LoginSession() as login:
        browser = LectureBrowser(login)
        lectures = browser.get_lectures()
        for lecture in lectures:
            print(lecture.class_id, lecture.lecture_id, lecture.times)
