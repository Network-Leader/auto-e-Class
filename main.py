from login_session import LoginSession
from lecture_browser import LectureBrowser
from lecture_viewer import LectureViewer

if __name__ == "__main__":
    with LoginSession() as login, LectureViewer(login) as viewer:
        browser = LectureBrowser(login)
        lectures = browser.get_lectures()
        for lecture in lectures:
            viewer.view(lecture)
