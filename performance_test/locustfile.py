from locust import HttpUser, task, between
import random
import json


class WebsiteTestUser(HttpUser):
    wait_time = between(1.0, 3.0)

    def on_start(self):
        pass
    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        pass

    @task(1)
    def register(self):
        email = f"{random.randint(1, 99999999999)}@mail.com"
        resp = self.client.post("http://193.233.20.226:4000/api/v1/users/registration",
                                data=json.dumps({
                                    "email": email,
                                    "password": "123456"
                                }),
                                headers={"Content-Type": "application/json"})




