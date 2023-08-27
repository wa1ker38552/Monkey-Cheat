from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from threading import Thread
import random
import time

# starts an internal time to check when test should be completed
# @param seconds: how long the test is
# @return: None
def start_internal_timer(seconds: int):
    global FINISHED_TEST
    for i in range(seconds+1):
        time.sleep(1)
    FINISHED_TEST = True

# fetch words by current batch that is displayed on the site (only about 50 words per batch)
# @param source: the page source
# @return words: the words scraped from source
def fetch_word_batch(source: str) -> list[str]:
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    words = soup.find_all('div', attrs={'class': 'word'})
    words = [e.get_text() for e in words]
    return words

# types all words in the list
# @param words: the list of words
# @param wait: the base time to wait for each word
# @return consecutive: the last three words in the list (used to index the next set of words)
def type_words(words: list[str], wait: float) -> list[str]:
    for word in words:
        if FINISHED_TEST: return
        if PER_WORD:
            actions.send_keys(word+" ").perform()
            time.sleep(wait-(len(word)*(REFERENCE_TEST/AVERAGE_CHARS)))
        else:
            computer_time_per_char = REFERENCE_TEST/AVERAGE_CHARS
            computer_time_for_word = (len(word)+1)*computer_time_per_char
            excess_time = wait-computer_time_for_word
            wait_per_char = excess_time/(len(word)+1)

            if ADD_VARIATION:
                variation = random.choice([excess_time/i for i in range(len(word), len(word)*2)])
            else:
                variation = 0

            for char in word:
                actions.send_keys(char).perform()
                time.sleep(wait_per_char)

            actions.send_keys(" ").perform()
            time.sleep(wait_per_char+variation)
    return words[-3:]

# completes a test on monkeytype
# @param seconds: which test to take
# @param wpm: the target wpm
# @return: None
def complete_test(seconds: int, wpm: int):
    global FINISHED_TEST
    driver.get('https://monkeytype.com/')
    time.sleep(1)

    # get index of div from seconds
    formatted_seconds = ["", "15", "30", "60", "120"].index(str(seconds))
    driver.find_element(By.XPATH, f'//*[@id="testConfig"]/div/div[5]/div[{formatted_seconds}]').click()
    time.sleep(1)

    characters = (wpm*(5*seconds))/60
    wait = seconds/(characters/5)

    FINISHED_TEST = False
    consec = None

    Thread(target=lambda: start_internal_timer(seconds)).start()

    while True:
        words = fetch_word_batch(driver.page_source)
        if consec:
            for i in range(len(words)-len(consec)):
                if words[i:i+len(consec)] == consec:
                    words = words[i+len(consec):]
                    break
        consec = type_words(words, wait)
        if not words: break

    wpm = driver.find_element(By.XPATH, DIV_WPM).text
    print(f'Finished test, typing: {wpm} wpm')

driver = webdriver.Chrome()
actions = ActionChains(driver)

# globals  :P
FINISHED_TEST = False

# constants
USERNAME = ''
PASSWORD = ''
AVERAGE_CHARS = 3864 # IMPORTAT, AMOUNT OF CHARS PER TEST
REFERENCE_TEST = 30 # IMPORTANT, TEST TIME USED TO GET AVERAGE_CHARS
PER_WORD = False # Types each character or word, word gets you closer to wpm
ADD_VARIATION = True # Add variation in time to the end of each word (SLOWS DOWN THE WPM BY ALOT)

# elements <tag_name>
INPUT_EMAIL = '//*[@id="pageLogin"]/div[3]/form/input[1]'
INPUT_PASSWORD = '//*[@id="pageLogin"]/div[3]/form/input[2]'
DIV_SIGNIN = '//*[@id="pageLogin"]/div[3]/form/div[2]'
DIV_COOKIEACCEPT = '//*[@id="cookiePopup"]/div[2]/div[2]/div[1]'
DIV_WPM = '//*[@id="result"]/div[1]/div[1]/div[2]'

# login
driver.get('https://monkeytype.com/login')
# accept cookies
try:
    driver.find_element(By.XPATH, DIV_COOKIEACCEPT).click()
except: pass
time.sleep(1)
driver.find_element(By.XPATH, INPUT_EMAIL).send_keys(USERNAME)
driver.find_element(By.XPATH, INPUT_PASSWORD).send_keys(PASSWORD)
driver.find_element(By.XPATH, DIV_SIGNIN).click()
time.sleep(1)

# finished logging in
# put anything you want here
while True:
    complete_test(15, 150)
  
