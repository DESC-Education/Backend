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
    def login(self):
        email = f"{random.randint(1, 99999999999)}@mail.com"
        resp = self.client.post("http://193.233.20.226:4000/api/v1/users/login",
                                data=json.dumps({
                                    "email": "user@example.com",
                                    "password": "string"
                                }),
                                headers={"Content-Type": "application/json"})

        token = resp.json().get('tokens').get('accessToken')

        self.client.get("http://193.233.20.226:4000/api/v1/tasks/tasks",
                        headers={"Content-Type": "application/json"})

        self.client.post("http://193.233.20.226:4000/api/v1/profiles/phone/code",
                        data={
                            "phone": f"+{random.randint(1111111111, 9999999999999)}"
                        },

                        headers={"Content-Type": "application/json",
                                 "Authorization": f"Bearer {token}"})


