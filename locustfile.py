
from locust import HttpUser, task, between

#Custom metrics storage
login_failures = 0
slow_requests = 0


class ReqResUser(HttpUser):
    host = "https://reqres.in"
    wait_time = between(1, 3)

    @task(7)
    def get_users(self):
        with self.client.get(
            "/api/users?page=2",
            catch_response=True
        ) as response:

            if response.status_code != 200:
                response.failure("Failed to load user list")

            elif response.elapsed.total_seconds() > 1.5:
                global slow_requests
                slow_requests += 1
                response.failure("Response too slow (>1.5s)")

            else:
                response.success()

    @task(2)
    def get_single_user(self):
        with self.client.get(
            "/api/users/2",
            catch_response=True
        ) as response:

            if response.status_code != 200:
                response.failure("Failed to load single user")

    @task(1)
    def login(self):
        global login_failures

        with self.client.post(
            "/api/login",
            json={
                "email": "eve.holt@reqres.in",
                "password": "cityslicka"
            },
            catch_response=True
        ) as response:

            if response.status_code != 200:
                login_failures += 1
                response.failure("Login failed")

            elif "token" not in response.json():
                login_failures += 1
                response.failure("No token returned")

            else:

                response.success()
