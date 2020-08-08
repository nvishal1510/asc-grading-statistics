import time
from getpass import getpass
from pathlib import Path

from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.keys import Keys

courses_dir_path = './courses'
failed_attempts_dir_path = './failed_attempts'


def switch_to_left_frame(driver2):
    driver2.switch_to.frame(driver2.find_element_by_xpath('//frame[@src="redirect.jsp"]'))


def create_file_name(course_, year_, semester_):
    return './failed_attempts/' + course_ + 'year' + str(year_) + 'semester' + str(semester_) + '.png'


driver = Chrome()

# driver.implicitly_wait(10)

driver.maximize_window()

driver.get("https://asc.iitb.ac.in")

driver.switch_to.frame(driver.find_element_by_xpath('//frame[@id="right2"]'))
username_element = driver.find_element_by_xpath('//input[contains(@name, "UserName")]')

username_element.send_keys(input("Enter your roll no.: "))
password_element = driver.find_element_by_xpath('//input[contains(@name, "UserPassword")]')
password_element.send_keys(getpass())

password_element.send_keys(Keys.ENTER)

switch_to_left_frame(driver)

academic_element = driver.find_element_by_xpath('//a[@id="ygtvlabelel1"]')
academic_element.click()

all_about_courses_element = driver.find_element_by_xpath('//a[@id="ygtvlabelel7"]')
all_about_courses_element.click()

grading_statistics_element = driver.find_element_by_xpath('//a[@id="4_71_1"]')
grading_statistics_element.click()

driver.switch_to.default_content()
time.sleep(10)

right_frame = driver.find_element_by_xpath('//frame[@id="right2"]')
driver.switch_to.frame(right_frame)

courses_list_file = open('Courses.csv', 'r')
for line in courses_list_file.readlines():
    course = str(line).strip()
    print("Scraping for course " + course)
    course_text_element = driver.find_element_by_xpath('//input[@name="txtcrsecode"]')
    course_text_element.send_keys(Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE,
                                  Keys.BACKSPACE, course)

    dept_courses_dir_path = courses_dir_path + '/' + course[:2]
    Path(dept_courses_dir_path).mkdir(exist_ok=True, parents=True)

    file_path = dept_courses_dir_path + '/' + course + '.txt'
    file = open(file_path, 'w')
    file.write(course + '\n\n')

    for year in range(2019, 2015, -1):
        file.write("year: " + str(year) + '\n')
        year_element_number = 2021 - year
        year_element = driver.find_element_by_xpath(
            '/html/body/form/ul/li[1]/table/tbody/tr[2]/td[1]/center/select/option[' + str(year_element_number) + ']')
        year_element.click()

        for semester in range(1, 3):
            file.write("semester: " + str(semester) + '\n')
            semester_element = driver.find_element_by_xpath(
                '/html/body/form/ul/li[1]/table/tbody/tr[2]/td[2]/center/select/option[' + str(semester) + ']')
            semester_element.click()

            submit_button = driver.find_element_by_xpath('/html/body/form/ul/li[1]/table/tbody/tr[3]/td/input[1]')
            submit_button.click()

            try:
                rows = len(driver.find_elements_by_xpath('/html/body/form/center[3]/table[2]/tbody/tr'))
                for row in range(2, rows):  # ignoring first and last elements
                    grade_element = driver.find_element_by_xpath(
                        '/html/body/form/center[3]/table[2]/tbody/tr[' + str(row) + ']/td[1]/b')
                    num_students_element = driver.find_element_by_xpath(
                        '/html/body/form/center[3]/table[2]/tbody/tr[' + str(row) + ']/td[2]/b')
                    file.write(grade_element.text + " " + num_students_element.text + "\n")

            except Exception as e:
                Path('./failed_attempts').mkdir(exist_ok=True)
                driver.save_screenshot(create_file_name(course, year, semester))
                print(e)  # edit this
            finally:
                back_button = driver.find_element_by_xpath('/html/body/form/center[3]/input')
                back_button.click()
        file.write('\n')
    file.close()

courses_list_file.close()
