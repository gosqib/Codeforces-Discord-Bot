class SubmitProblem:
    def __init__(self, problem: str) -> None:
        self._PROBLEM_TYPES = list('ABCDEFGHI')
        self._SITE_CODE = [
            letter 
            for letter in problem 
            if letter in self._PROBLEM_TYPES
        ]
        
        self._SUBMIT_LINK = f"https://codeforces.com/problemset/problem/{problem[:problem.find(self._SITE_CODE[0])]}/{problem[problem.find(self._SITE_CODE[0]):]}#:~:text=→%20Submit%3F,Submit"


    def send_submit_link(self) -> str:
        """send link through function for consistency"""

        return self._SUBMIT_LINK


