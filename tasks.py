from time import sleep
from invoke import task
from pebble import concurrent
import os

@task
def build(c,ip=None):
    if ip:
        ip_addr = ip
    else:
        ip_addr = None
    @concurrent.thread
    def runserver(c):
        if ip_addr:
            c.run(f'python manage.py runserver {ip_addr}:8091')
        else:
            c.run('python manage.py runserver')
        sleep(3)
                    
    @concurrent.thread
    def start():
        with open('build.txt','w') as file:
            file.write("Build done")
        c.run('python home/tests/functional_test.py')
    
    build_future = runserver()
    start_future = start()
    
    build_done = False
    while not build_done:
        sleep(1)
        try:
            with open('build.txt', 'r') as file:
                content = file.read()
                if 'Build done' in content:
                    build_future.cancel()
                    build_done = True
        except:
            pass
    os.remove('build.txt')
    start_future.result()