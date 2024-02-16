from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from datetime import time, datetime, timezone, timedelta
from dotenv import load_dotenv
import requests
import os

load_dotenv()

# params
url = "https://gitlab.com/groups/gitlab-org/-/issues/?sort=created_date&state=opened&label_name%5B%5D=frontend&label_name%5B%5D=quick%20win&label_name%5B%5D=Community%20contribution&first_page_size=100"
unassigned_url = "https://gitlab.com/groups/gitlab-org/-/issues/?sort=created_date&state=opened&label_name%5B%5D=frontend&label_name%5B%5D=Community%20contribution&label_name%5B%5D=quick%20win&assignee_id=None&first_page_size=100"
options = Options()
options.add_argument("--headless")
options.page_load_strategy = "normal"
BOT_API_KEY = os.environ.get("BOT_API_KEY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
current_time = datetime.now()


def check_for_new_issue(url, current_time):
    recent_issue = False

    # access GitLab issue page
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )
    driver.get(url)

    # sleep 10 sec (until page elements load)
    sleep(10)

    # find the element containing when the ticket was issued
    issued_date_element = driver.find_element(
        By.XPATH,
        "//div[@class='issuable-main-info']/div[@class='issuable-info']/span[2]/span[2]/span",
    )

    # parse the HTML element to convert to datetime object
    issued_date_string = issued_date_element.get_attribute("title")

    # Month Day, Year format
    try:
        formatted_date_string = issued_date_string.split("A")[0]
        print(formatted_date_string)
        # convert string to datetime object
        issued_date_object = datetime.strptime(
            formatted_date_string, "%B %d, %Y at %I:%M:%S "
        )

    # Day Month Year format
    except ValueError:
        formatted_date_string = issued_date_string.split("G")[0]
        print(formatted_date_string)
        issued_date_object = datetime.strptime(
            formatted_date_string, "%d %B %Y at %H:%M:%S "
        )

    # check if first issue on page was issued within 24hrs
    if current_time - timedelta(hours=24) <= issued_date_object <= current_time:
        recent_issue = True
        return recent_issue


def check_for_unassigned_issue(unassigned_url):
    unassigned_issue = False

    # access GitLab issue page
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )
    driver.get(unassigned_url)

    sleep(10)

    # check if h1 element containing no result message rendered
    try:
        no_result_element = driver.find_element(By.TAG_NAME, "h1")
        no_result_text = no_result_element.text
        print(no_result_text)
    # if no h1 assume issues are shown
    except NoSuchElementException:
        unassigned_issue = True
        return unassigned_issue


def send_message():
    recent_issue = check_for_new_issue(url, current_time)
    unassigned_issue = check_for_unassigned_issue(unassigned_url)

    if recent_issue or unassigned_issue:
        message = "Found New GitLab Issue!!"
        telegram_message_url = f"https://api.telegram.org/bot{BOT_API_KEY}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
        print(requests.get(telegram_message_url).json())
    else:
        message = "No new tickets found"
        telegram_message_url = f"https://api.telegram.org/bot{BOT_API_KEY}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}"
        print(requests.get(telegram_message_url).json())


send_message()
