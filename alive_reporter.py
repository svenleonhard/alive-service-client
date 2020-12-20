import schedule
import time
import logging
import requests
from datetime import datetime

BASE_URL="https://alive-service.7lofficial.de"
REGISTER_PATH="/api/register-messages"
ALIVE_PATH="/api/alive-messages"
CREDENTIALS={'username':'user','password':'user'}
DO_REGISTER_NEXT_TIME=False

id_token=""

def auth():
    global id_token
    try:
      r = requests.post(BASE_URL + "/api/authenticate",json = CREDENTIALS)
      if r.status_code == 200:
        id_token = r.json()['id_token']
      return r.status_code
    except Exception as e:
        logging.error(e)

def tryAuth():
    retryCount = 0
    success = False
    while success == False and retryCount < 11:
        retryCount = retryCount + 1
        if auth() == 200:
            success = True
            logging.info("Auth Successful")
            return True
        if retryCount == 10:
            logging.info("Auth not possible")
            return False

def postRequestWithRetry(payload, url):
    retryCount = 0
    success = False
    payload['retrycount'] = retryCount
    while success == False and retryCount < 11:
        payload['retrycount'] = retryCount
        logging.info(id_token)
        r = requests.post(url,json = payload, headers={"Authorization": "Bearer "+ id_token})
        logging.info("request send")
        logging.info(r)
        if r.status_code == 201 or r.status_code == 200:
            success = True
            logging.info("Post Successful")
            DO_REGISTER_NEXT_TIME=False
            return True
        if retryCount == 10:
            logging.info("Post not possible")
            DO_REGISTER_NEXT_TIME=True
            return False

def doPost(url):
    if tryAuth() == True:
        registerData = {
            "sendtime":datetime.now().astimezone().isoformat()
        }
        postRequestWithRetry(registerData, url)

def job():
    logging.info("Start Job")
    if DO_REGISTER_NEXT_TIME:
        logging.info("Try to register again")
    doPost(BASE_URL + ALIVE_PATH)

logging.basicConfig(level=logging.DEBUG)
logging.info("Start config")
doPost(BASE_URL + REGISTER_PATH)
schedule.every(30).seconds.do(job)
logging.info("End config")

while 1:
    schedule.run_pending()
    time.sleep(1)
