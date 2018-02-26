import webapp2

from im_futuretest import register_test 
from im_task_webapp2 import addrouteforwebapp2
from im_futuretest_webapp2 import addroutes_futuretest_webapp2, _create_route
from im_task import PermanentTaskFailure, task
from im_future import GetFutureAndCheckReady, FutureReadyForResult
import time

import logging

class RootHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect(_create_route("ui/"))

routes = [
    ("/", RootHandler)
]

addrouteforwebapp2(routes)
addroutes_futuretest_webapp2(routes)

logging.info(routes)

app = webapp2.WSGIApplication(routes, debug=True)

# tests

@register_test
def firsttest(futurekey):
    pass

@register_test(tags=["fails"])
def secondtest(futurekey):
    raise PermanentTaskFailure("This test fails")


@register_test(description="This is a slow test...", tags=["fails"])
def slowtest(futurekey):
    time.sleep(20)
    return True

@register_test(description="Kicks off a task, which fires later and marks success", tags=["task"])
def slowtestusingtask(futurekey):
    @task(countdown=20)
    def SetResult():
        fut = GetFutureAndCheckReady(futurekey)
        fut.set_success(True)
        
    SetResult()
    raise FutureReadyForResult("waiting")

@register_test(description="slow with progress", tags=["task"])
def progresstest(futurekey):
    @task(countdown=1)
    def Tick(aProgress):
        fut = GetFutureAndCheckReady(futurekey)
        fut.set_localprogress(aProgress * 5)
        if aProgress < 20:
            Tick(aProgress+1)
        else:
            fut.set_success(aProgress)
        
    Tick(0)
    raise FutureReadyForResult("waiting")
