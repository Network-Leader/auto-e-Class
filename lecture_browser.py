from login_session import LoginSession
from lecture import Lecture

from bs4 import BeautifulSoup


class LectureBrowser:
    HOST = "eclass.seoultech.ac.kr"
    PATH_TODOLIST = "/ilos/mp/todo_list.acl"

    def __init__(self, login: LoginSession):
        self.login = login

    def get_lectures(self):
        lectures: list[Lecture] = []
        res = self.login.session.get(f"https://{self.login.HOST}{self.PATH_TODOLIST}")
        soup = BeautifulSoup(res.text, "html.parser")
        todo_wraps = soup.find_all("div", {"class": "todo_wrap"})
        for todo in todo_wraps:
            onclick = todo.get("onclick")
            if onclick is not None:
                class_id, lecture_id, todo_type = onclick.split("'")[1::2]
                if todo_type == "lecture_weeks":
                    lectures.append(
                        Lecture(
                            class_id=class_id, lecture_id=lecture_id, login=self.login
                        )
                    )
        return lectures


if __name__ == "__main__":
    from login_session import LoginSession

    with LoginSession() as login:
        browser = LectureBrowser(login)
        lectures = browser.get_lectures()
        for lecture in lectures:
            print(lecture.class_name, lecture.times)
