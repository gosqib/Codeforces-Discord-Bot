from random import randrange
from typing import List
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import random



class RandomProblem:
    def __init__(self, link: str) -> None:
        self._BASE_URL = link
        self._BASE_HTML = urlopen(self._BASE_URL).read().decode("utf-8")
        self._SOUP_OBJ = BeautifulSoup(self._BASE_HTML, "html.parser")

        # search for URL filters for reference later
        self._URL_TAGS_RECORD = self._BASE_URL[self._BASE_URL.index('?') : ]\
                                if self._BASE_URL.find('?') != -1\
                                else ''


    def _remove_quotes_and_link(self, problems: List[str]) -> List[str]:
        """removes quotes and link that were added in regex process for clarity"""

        return [_[1:-1].replace("/problemset/problem/", "") for _ in problems]


    def _gather_problem_code(self) -> str:
        """finds the problem codes on current page and sends a random one"""

        # opens page and records all problem's codes
        self._PAGE_HTML = urlopen(self._STARTING_PAGE).read().decode("utf-8")

        # find all problems on page
        self._RAW_PROBLEMS_ON_PAGE = re.findall('"/problemset/problem/.*/.*"', self._PAGE_HTML)
        self._PROBLEMS_ON_PAGE = self._remove_quotes_and_link(self._RAW_PROBLEMS_ON_PAGE)
        return random.choice(self._PROBLEMS_ON_PAGE).replace('/', '')


    def give_problem(self) -> str:
        """analyzes page to find a random page of problems to start from, and a random problem to give"""

        # pagination is codeforce term for scrollwheel for pages of problems
        PAGINATION = self._SOUP_OBJ.find_all("span", class_="page-index")
        if PAGINATION:
            self._LAST_CODEFORCE_PAGE = PAGINATION[-1]
            self._RAW_PAGINATION = re.findall('pageindex=".*?"', str(self._LAST_CODEFORCE_PAGE))
            self._TOTAL_CODEFORCE_PROBLEM_PAGES = int(re.findall('".*"', self._RAW_PAGINATION[0])[0][1:-1])

            # go to a random page and open that and look for problem codes
            self._STARTING_PAGE = f"https://codeforces.com/problemset/page/{randrange(1, self._TOTAL_CODEFORCE_PROBLEM_PAGES) + 1}{self._URL_TAGS_RECORD}"
            return self._gather_problem_code()

        # else here
        self._STARTING_PAGE = self._BASE_URL
        return self._gather_problem_code()


