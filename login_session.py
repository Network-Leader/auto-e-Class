from getpass import getpass
import requests


class LoginSession:
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36"
    HOST = "eclass.seoultech.ac.kr"
    PATH_MAIN = "/ilos/main/main_form.acl"
    PATH_LOGIN = "/ilos/lo/login.acl"
    PATH_LOGOUT = "/ilos/lo/logout.acl"

    def __init__(
        self,
        studentid: str | None = None,
        wmonid: str | None = None,
        sessionid: str | None = None,
    ):
        self.studentid = studentid
        self.wmonid = wmonid
        self.sessionid = sessionid
        self.session: requests.Session | None = None

    def __enter__(self):
        if self.wmonid is None:
            self.wmonid = self.get_wmonid()
        if self.sessionid is None:
            self.sessionid = self.get_sessionid()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logout()

    def get_wmonid(self):
        if self.wmonid is None:
            res = requests.get(f"https://{self.HOST}{self.PATH_MAIN}")
            self.wmonid = res.cookies.get("WMONID")
        return self.wmonid

    def get_sessionid(self):
        if self.sessionid is None:
            self.login()
        return self.sessionid

    def is_login(self):
        return self.sessionid and self.session

    def login(self):
        if self.is_login():
            self.logout()
        while self.sessionid is None:
            studentid = input("Enter your student ID: ")
            pw = getpass("Enter your password: ")

            cookies = {"WMONID": self.get_wmonid()}
            body = {"usr_id": studentid, "usr_pwd": pw}
            res = requests.post(
                f"https://{self.HOST}{self.PATH_LOGIN}", cookies=cookies, data=body
            )
            lms_sessionid = res.cookies.get("LMS_SESSIONID")
            if lms_sessionid is not None:
                self.studentid = studentid
                self.sessionid = lms_sessionid
            else:
                print("Login failed. Try again.")
        print("Login successful.")
        self.session = requests.Session()
        self.session.cookies.set("WMONID", self.wmonid, domain=self.HOST)
        self.session.cookies.set("LMS_SESSIONID", self.sessionid, domain=self.HOST)
        self.session.headers.update({"user-agent": self.USER_AGENT})

    def logout(self):
        if self.session is not None:
            self.session.get(f"https://{self.HOST}{self.PATH_LOGOUT}")
            self.session.close()
            self.session = None
        self.sessionid = None
