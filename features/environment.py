from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from django.core.management import call_command
from django.db import connections

def before_all(context):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    context.browser = webdriver.Chrome(options=options)
    context.browser.implicitly_wait(5)

def before_scenario(context, scenario):
    call_command('loaddata', 'salas_iniciales.json')

def after_scenario(context, scenario):
    connections.close_all()

def after_all(context):
    context.browser.quit()