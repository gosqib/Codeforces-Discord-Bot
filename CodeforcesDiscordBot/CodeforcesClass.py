import time
from typing import Any, Callable, List, Literal, Tuple, Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from urllib.request import urlopen

opts = webdriver.ChromeOptions()
opts.headless = True
driver = webdriver.Chrome(options=opts)

WEBPAGE_SCREENSHOT = "Webpage Screenshot.png"
PROBLEM_STARTING_INFO = "Problem Info.png"
PROBLEM_STARTING_DESC = "Problem Desc.png"
OPENING_PICTURE = "Opening Picture.png"



class CodeforceProblem:
    def __init__(self, problem: str) -> None:
        self._PROBLEM_TYPES = list('ABCDEFGHI')
        self._SITE_CODE = [
            letter 
            for letter in problem 
            if letter in self._PROBLEM_TYPES
        ]
        self._SITE = f"https://codeforces.com/problemset/problem/{problem[:problem.find(self._SITE_CODE[0])]}/{problem[problem.find(self._SITE_CODE[0]):]}"
        driver.get(self._SITE)

        self._section_titles = driver.find_elements_by_xpath("//div[@class='section-title']")
        self._section_titles.append(driver.find_element_by_xpath("//div[@id='footer']"))
        self._HEADER = driver.find_element_by_xpath("//div[@class='header']")
        self._CF_PAGE_NUMBER_OF_SECTIONS = len(self._section_titles) - 1
        self._FOOTER_Y_LOCATION = self._section_titles[-1].location['y'] - 45 # with offset
        self._DESCRIPTION_Y_LOCATION = self._HEADER.location['y'] + self._HEADER.size['height']
        self._MAX_COMBINE_DISTANCE = 600

        self._X_START_ADJUSTMENT = -15
        self._Y_START_ADJUSTMENT = -3
        self._X_END_ADJUSTMENT = 25
        self._Y_END_ADJUSTMENT = -1

        self._take_webpage_screenshot()
        self._PAGE_SCREENSHOT = Image.open(WEBPAGE_SCREENSHOT)
        self._FIRST_SEC_TITLE = self._section_titles[0]
        self._SECOND_SEC_TITLE = self._section_titles[1]
        self._THIRD_SEC_TITLE = self._section_titles[2]
        self._FOURTH_SEC_TITLE = self._section_titles[3]
        
        self._CROP_REST_PAGE_FROM = {
            "section one": self._first,
            "section two": self._second,
            "section three": self._third,
            "section four": self._fourth
        }


    def _find_part_size(self, to_find: str) -> int:
        """scroll script to find and return the page screen's width or height"""

        return driver.execute_script("return document.body.parentNode.scroll" + to_find)


    def _take_webpage_screenshot(self) -> None:
        """set window size and take picture of webpage"""

        # width, height - letter case matters
        driver.set_window_size(self._find_part_size("Width"), self._find_part_size("Height"))

        # body; where CFs page starts
        driver.find_element_by_tag_name("body").screenshot(WEBPAGE_SCREENSHOT)
 
 
    def _combinable(self, combine_from: Any, combine_to: Any, desc=False, last_sec=False, desc_last_sec=False) -> bool:
        """checks if the space between 2 sections is small enough to combine into 1 picture"""

        # special case when working with description
        if desc:
            return combine_to.location['y'] + self._Y_END_ADJUSTMENT\
                - combine_from + self._Y_START_ADJUSTMENT < self._MAX_COMBINE_DISTANCE
        
        # special case when working with last section
        elif last_sec:
            return combine_to + self._Y_END_ADJUSTMENT - combine_from.location['y']\
                + self._Y_START_ADJUSTMENT < self._MAX_COMBINE_DISTANCE

        # special case when working with both
        elif desc_last_sec:
            return combine_to + self._Y_END_ADJUSTMENT - combine_from\
                + self._Y_END_ADJUSTMENT < self._MAX_COMBINE_DISTANCE

        return combine_to.location['y'] + self._Y_END_ADJUSTMENT -\
            combine_from.location['y'] + self._Y_START_ADJUSTMENT < self._MAX_COMBINE_DISTANCE

    
    def _cropped_images_storage(self, no_of_section_crops: int, *starting_crops: Tuple[str]) -> List[str]:
        """returns list of cropped images that will be sent to discord"""

        return [*starting_crops] + [f"CF SECTION {section + 1}.png" for section in range(no_of_section_crops)]


    def _crop_part(self, crop_from: Any, crop_to: Any, save_as: str, desc=False, last_sec=False, desc_last_sec=False) -> None:
        """crops from start of first argument to start of second argument"""

        # special crop when description included in crop
        if desc:
            self._PAGE_SCREENSHOT.crop((
                crop_to.location['x'] + self._X_START_ADJUSTMENT,
                crop_from + self._Y_START_ADJUSTMENT,
                crop_to.size['width'] + self._X_END_ADJUSTMENT,
                crop_to.location['y'] + self._Y_END_ADJUSTMENT
            )).save(save_as)

        # special crop while last section included in crop
        elif last_sec:
            self._PAGE_SCREENSHOT.crop((
                crop_from.location['x'] + self._X_START_ADJUSTMENT, 
                crop_from.location['y'] + self._Y_START_ADJUSTMENT, 
                crop_from.size["width"] + self._X_END_ADJUSTMENT, 
                crop_to + self._Y_END_ADJUSTMENT
            )).save(save_as)

        # special crop when both included in crop
        elif desc_last_sec:
            self._PAGE_SCREENSHOT.crop((
                self._HEADER.location['x'] + self._X_START_ADJUSTMENT,
                crop_from + self._Y_START_ADJUSTMENT,
                self._HEADER.size['width'] + self._X_END_ADJUSTMENT,
                crop_to + self._Y_END_ADJUSTMENT
            )).save(save_as)

        else:
            self._PAGE_SCREENSHOT.crop((
                crop_from.location['x'] + self._X_START_ADJUSTMENT,
                crop_from.location['y'] + self._Y_START_ADJUSTMENT,
                crop_from.size['width'] + self._X_END_ADJUSTMENT,
                crop_to.location['y'] + self._Y_END_ADJUSTMENT
            )).save(save_as)
    

    def _crop_one_by_one(self, loop_start, cropped: int, save_offset: int, *other_pictures: Tuple[str]) -> Callable[[int, str], Tuple[str]]:
        """crops each section individually starting from `loop_start` index"""

        for section in range(loop_start, self._CF_PAGE_NUMBER_OF_SECTIONS):
            # if no section after current to use as endpoint, crop using the footer as endpoint reference
            if section + 1 == self._CF_PAGE_NUMBER_OF_SECTIONS:
                self._crop_part(self._section_titles[section], self._FOOTER_Y_LOCATION, f"CF SECTION {section + save_offset}.png", last_sec=True)
            else:
                # crop using the next section coordinates as endpoint references
                self._crop_part(self._section_titles[section], self._section_titles[section + 1], f"CF SECTION {section + save_offset}.png")
        
        return self._cropped_images_storage(cropped, *other_pictures)


    def _first(self, *starting_pictures: Tuple[str]):
        """crops all rest of sections starting from first section title"""
        
        if self._combinable(self._FIRST_SEC_TITLE, self._FOOTER_Y_LOCATION, last_sec=True):
                self._crop_part(self._FIRST_SEC_TITLE, self._FOOTER_Y_LOCATION, "CF SECTION 1.png", last_sec=True)
                return self._cropped_images_storage(1, *starting_pictures)

        elif self._combinable(self._FIRST_SEC_TITLE, self._FOURTH_SEC_TITLE):
            self._crop_part(self._FIRST_SEC_TITLE, self._FOURTH_SEC_TITLE, "CF SECTION 1.png")
            self._crop_part(self._FOURTH_SEC_TITLE, self._FOOTER_Y_LOCATION, "CF SECTION 2.png", last_sec=True)
            return self._cropped_images_storage(2, *starting_pictures)

        elif self._combinable(self._FIRST_SEC_TITLE, self._THIRD_SEC_TITLE):
            self._crop_part(self._FIRST_SEC_TITLE, self._THIRD_SEC_TITLE, "CF SECTION 1.png")
                
            if self._combinable(self._THIRD_SEC_TITLE, self._FOOTER_Y_LOCATION, last_sec=True):
                return self._CROP_REST_PAGE_FROM["section three"](2, *starting_pictures)
                
            return self._crop_one_by_one(2, 3, 0, *starting_pictures)
        
        return self._crop_one_by_one(0, self._CF_PAGE_NUMBER_OF_SECTIONS, 1, *starting_pictures)
    
    def _second(self, start_loop: int, *starting_pictures: Tuple[str]) -> List[str]: 
        """crops all rest of sections starting from second section title"""

        if self._combinable(self._SECOND_SEC_TITLE, self._FOOTER_Y_LOCATION, last_sec=True):
            self._crop_part(self._SECOND_SEC_TITLE, self._FOOTER_Y_LOCATION, f"CF SECTION {start_loop}.png", last_sec=True)
            return self._cropped_images_storage(start_loop, *starting_pictures)

        elif self._combinable(self._SECOND_SEC_TITLE, self._FOURTH_SEC_TITLE):
            self._crop_part(self._SECOND_SEC_TITLE, self._FOURTH_SEC_TITLE, f"CF SECTION {start_loop}.png")
            
            return self._CROP_REST_PAGE_FROM["section four"](start_loop + 1, *starting_pictures)
    
    def _third(self, pic_num: int, *starting_pictures: Tuple[str]) -> List[str]:
        """crops all rest of sections starting from third section title"""

        self._crop_part(self._THIRD_SEC_TITLE, self._FOOTER_Y_LOCATION, f"CF SECTION {pic_num}.png", last_sec=True)
        return self._cropped_images_storage(pic_num, *starting_pictures)
    
    def _fourth(self, no_of_picture: int, *starting_pictures: Tuple[str]) -> List[str]: 
        """crops all rest of sections starting from fourth section title"""

        self._crop_part(self._FOURTH_SEC_TITLE, self._FOOTER_Y_LOCATION, f"CF SECTION {no_of_picture}.png", last_sec=True)
        return self._cropped_images_storage(no_of_picture, *starting_pictures)


    def crop_codeforce_problem(self) -> Tuple[str]:
        """crops main portions of codeforce problem"""

        # if possible, crop entire problem as first picture
        if self._combinable(self._HEADER, self._FOOTER_Y_LOCATION, last_sec=True):
            self._crop_part(self._HEADER, self._FOOTER_Y_LOCATION, OPENING_PICTURE, last_sec=True)
            return self._cropped_images_storage(0, OPENING_PICTURE)

        # if possible, crop from start of page to start of last section as first picture
        elif self._combinable(self._HEADER, self._FOURTH_SEC_TITLE):
            # crop first 4 sections, and 5th alone
            self._crop_part(self._HEADER, self._FOURTH_SEC_TITLE, OPENING_PICTURE)
            return self._CROP_REST_PAGE_FROM["section four"](1, OPENING_PICTURE)
        
        # if possible, crop from start of page to start of second last section as first picture
        elif self._combinable(self._HEADER, self._THIRD_SEC_TITLE):
            self._crop_part(self._HEADER, self._THIRD_SEC_TITLE, OPENING_PICTURE)
            if self._combinable(self._THIRD_SEC_TITLE, self._FOOTER_Y_LOCATION, last_sec=True):
                return self._CROP_REST_PAGE_FROM["section three"](1, OPENING_PICTURE)

            return self._crop_one_by_one(2, 2, -1, OPENING_PICTURE)

        # if possible, crop from start of page to start of third last section as first picture
        elif self._combinable(self._HEADER, self._SECOND_SEC_TITLE):
            self._crop_part(self._HEADER, self._SECOND_SEC_TITLE, OPENING_PICTURE)
            # check if case passed
            if self._second(1, OPENING_PICTURE):
                return self._CROP_REST_PAGE_FROM["section two"](1, OPENING_PICTURE)
            
            return self._crop_one_by_one(1, 3, 0, OPENING_PICTURE)

        # if possible, crop from start of page to start of first_section as first picture
        elif self._combinable(self._HEADER, self._FIRST_SEC_TITLE):
            self._crop_part(self._HEADER, self._FIRST_SEC_TITLE, OPENING_PICTURE)
            return self._CROP_REST_PAGE_FROM["section one"](OPENING_PICTURE)

        # if header can't be combined with anything, crop it by itself as first picture
        # take picture of header
        self._HEADER.screenshot(PROBLEM_STARTING_INFO)

        # attempt cropping out the next picture, starting from the problem description
        if self._combinable(self._DESCRIPTION_Y_LOCATION, self._FOOTER_Y_LOCATION, desc_last_sec=True):
            self._crop_part(self._DESCRIPTION_Y_LOCATION, self._FOOTER_Y_LOCATION, "CF SECTION 1.png", desc_last_sec=True)
            return self._cropped_images_storage(1, PROBLEM_STARTING_INFO)

        elif self._combinable(self._DESCRIPTION_Y_LOCATION, self._FOURTH_SEC_TITLE, desc=True):
            self._crop_part(self._DESCRIPTION_Y_LOCATION, self._FOURTH_SEC_TITLE, "CF SECTION 1.png", desc=True)
            return self._CROP_REST_PAGE_FROM["section four"](2, PROBLEM_STARTING_INFO)

        elif self._combinable(self._DESCRIPTION_Y_LOCATION, self._THIRD_SEC_TITLE, desc=True):
            self._crop_part(self._DESCRIPTION_Y_LOCATION, self._THIRD_SEC_TITLE, "CF SECTION 1.png", desc=True)
            if self._combinable(self._THIRD_SEC_TITLE, self._FOOTER_Y_LOCATION, last_sec=True):
                return self._CROP_REST_PAGE_FROM["section three"](2, PROBLEM_STARTING_INFO)

            return self._crop_one_by_one(2, 3, 0, PROBLEM_STARTING_INFO)

        elif self._combinable(self._DESCRIPTION_Y_LOCATION, self._SECOND_SEC_TITLE, desc=True):
            self._crop_part(self._DESCRIPTION_Y_LOCATION, self._SECOND_SEC_TITLE, "CF SECTION 1.png", desc=True)
            # check if case passed
            if self._CROP_REST_PAGE_FROM["section two"](2, PROBLEM_STARTING_INFO):
                return self._CROP_REST_PAGE_FROM["section two"](2, PROBLEM_STARTING_INFO)
            
            if self._combinable(self._SECOND_SEC_TITLE, self._FOOTER_Y_LOCATION, last_sec=True):
                self._crop_part(self._SECOND_SEC_TITLE, self._FOOTER_Y_LOCATION, "CF SECTION 2.png", last_sec=True)
                return self._cropped_images_storage(2, PROBLEM_STARTING_INFO)

            elif self._combinable(self._SECOND_SEC_TITLE, self._FOURTH_SEC_TITLE):
                self._crop_part(self._SECOND_SEC_TITLE, self._FOURTH_SEC_TITLE, "CF SECTION 2.png")
                return self._CROP_REST_PAGE_FROM["section four"](3, PROBLEM_STARTING_INFO)

            return self._crop_one_by_one(1, self._CF_PAGE_NUMBER_OF_SECTIONS, 1, PROBLEM_STARTING_INFO)

        # case where description is cropped alone as well, as second picture
        self._crop_part(self._DESCRIPTION_Y_LOCATION, self._FIRST_SEC_TITLE, PROBLEM_STARTING_DESC, desc=True)
        return self._CROP_REST_PAGE_FROM["section one"](PROBLEM_STARTING_INFO, PROBLEM_STARTING_DESC)


