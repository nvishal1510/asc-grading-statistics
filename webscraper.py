import time
from getpass import getpass
from pathlib import Path

from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys

COURSES_LIST_FILE_PATH = 'Courses.csv'
COURSE_DIR_PATH = './courses'
FAILED_ATTEMPTS_DIR_PATH = './failed_attempts'

SITE_URL = "https://asc.iitb.ac.in"

LEFT_FRAME_XPATH = '//frame[@src="redirect.jsp"]'
RIGHT_FRAME_XPATH = '//frame[@id="right2"]'

USER_NAME_ELEMENT_XPATH = '//input[contains(@name, "UserName")]'
PASSWORD_ELEMENT_XPATH = '//input[contains(@name, "UserPassword")]'

ACADEMIC_ELEMENT_XPATH = '//a[@id="ygtvlabelel1"]'
ALL_ABOUT_COURSES_ELEMENT_XPATH = '//a[@id="ygtvlabelel7"]'
GRADING_STASTISTICS_ELEMENT_XPATH = '//a[@id="4_71_1"]'

YEAR_ELEMENT_OPTIONS_BASE_XPATH = '/html/body/form/ul/li[1]/table/tbody/tr[2]/td[1]/center/select/option'
SEMESTER_ELEMENT_OPTIONS_BASE_XPATH = '/html/body/form/ul/li[1]/table/tbody/tr[2]/td[2]/center/select/option'
COURSE_TEXT_ELEMENT_XPATH = '//input[@name="txtcrsecode"]'
SUBMIT_BUTTON_XPATH = '/html/body/form/ul/li[1]/table/tbody/tr[3]/td/input[1]'

GRADES_TABLE_ROW_ELEMENT_BASE_XPATH = '/html/body/form/center[3]/table[2]/tbody/tr'
TABLE_FIRST_COLUMN_END_XPATH = '/td[1]/b'
TABLE_SECOND_COLUMN_END_XPATH = '/td[2]/b'
BACK_BUTTON_XPATH = '/html/body/form/center[3]/input'


def switch_to_left_frame(d):
    d.switch_to.frame(d.find_element_by_xpath(LEFT_FRAME_XPATH))


def switch_to_right_frame(d):
    d.switch_to.frame(d.find_element_by_xpath(RIGHT_FRAME_XPATH))


def create_file_name(course_, year_, semester_):
    return './failed_attempts/' + course_ + 'year' + str(year_) + 'semester' + str(semester_) + '.png'


driver = Chrome()
driver.maximize_window()

driver.get(SITE_URL)
driver.switch_to.frame(driver.find_element_by_xpath(RIGHT_FRAME_XPATH))

roll_no = input("Enter your roll no.: ")
username_element = driver.find_element_by_xpath(USER_NAME_ELEMENT_XPATH)
username_element.send_keys(roll_no)
password_element = driver.find_element_by_xpath(PASSWORD_ELEMENT_XPATH)
password_element.send_keys(getpass(), Keys.ENTER)

switch_to_left_frame(driver)
driver.find_element_by_xpath(ACADEMIC_ELEMENT_XPATH).click()
driver.find_element_by_xpath(ALL_ABOUT_COURSES_ELEMENT_XPATH).click()
driver.find_element_by_xpath(GRADING_STASTISTICS_ELEMENT_XPATH).click()

driver.switch_to.default_content()

# Without this sleep command before switching to the right frame, makes the selenium framework grab the initial
# frame which is seen after login. I tried using the selenium's inbuilt WebDriverWait package for a more robust
# solution, but it has no effect. So I had to stick with this workaround.
time.sleep(10)

switch_to_right_frame(driver)

courses_list_file = open(COURSES_LIST_FILE_PATH, 'r')
for line in courses_list_file.readlines():
    course = str(line).strip()
    print("Scraping for course " + course)
    course_text_element = driver.find_element_by_xpath(COURSE_TEXT_ELEMENT_XPATH)
    course_text_element.send_keys(Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE,
                                  Keys.BACKSPACE, course)

    dept_courses_dir_path = COURSE_DIR_PATH + '/' + course[:3]
    Path(dept_courses_dir_path).mkdir(exist_ok=True, parents=True)

    file_path = dept_courses_dir_path + '/' + course + '.txt'
    file = open(file_path, 'w')
    file.write(course + '\n\n')

    for year in range(2019, 2015, -1):
        file.write("year: " + str(year) + '\n')
        year_element_number = 2021 - year
        year_element = driver.find_element_by_xpath(
            YEAR_ELEMENT_OPTIONS_BASE_XPATH + '[' + str(year_element_number) + ']')
        year_element.click()

        for semester in range(1, 3):
            file.write("semester: " + str(semester) + '\n')
            semester_element = driver.find_element_by_xpath(
                SEMESTER_ELEMENT_OPTIONS_BASE_XPATH + '[' + str(semester) + ']')
            semester_element.click()

            driver.find_element_by_xpath(SUBMIT_BUTTON_XPATH).click()

            try:
                grades_table_row_elements = driver.find_elements_by_xpath(GRADES_TABLE_ROW_ELEMENT_BASE_XPATH)
                rows = len(grades_table_row_elements)
                for row in range(2, rows):  # ignoring first and last elements
                    grade_element = driver.find_element_by_xpath(
                        GRADES_TABLE_ROW_ELEMENT_BASE_XPATH + '[' + str(row) + ']' + TABLE_FIRST_COLUMN_END_XPATH)
                    num_students_element = driver.find_element_by_xpath(
                        GRADES_TABLE_ROW_ELEMENT_BASE_XPATH + '[' + str(row) + ']' + TABLE_SECOND_COLUMN_END_XPATH)
                    file.write(grade_element.text + " " + num_students_element.text + "\n")

            except Exception as e:
                Path('./failed_attempts').mkdir(exist_ok=True)
                driver.save_screenshot(create_file_name(course, year, semester))
                print(e)
                print("Could not scrape data for " + course + " year " + str(year) + " semester " + str(semester))
                print("Check the captured screenshot in failed_attempts dir for more information")
            finally:
                back_button = driver.find_element_by_xpath(BACK_BUTTON_XPATH)
                back_button.click()
        file.write('\n')
    file.close()

courses_list_file.close()
