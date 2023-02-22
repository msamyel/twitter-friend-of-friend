###
### Because TwitterAPI imposes limits on how many requests can be sent, we need a wrapper
### for out API client, that will wait before executing consequent requests.
###
import os
import time
from dotenv import load_dotenv
from TwitterAPI import TwitterAPI


class PatientApiClient:
    api_client_inner: TwitterAPI = None
    current_request_count: dict = dict()
    MAX_REQUEST_NUM: dict = dict()
    WAIT_MINUTES: int = 16  # add one extra minute just in case

    is_authenticated: bool = False

    def __init__(self):
        load_dotenv()

        self.MAX_REQUEST_NUM["following"] = 15
        self.MAX_REQUEST_NUM["username"] = 300
        self.reset_request_count()

        self.api_client_inner = TwitterAPI(os.getenv("TWITTER_API_KEY"),
                                           os.getenv("TWITTER_API_SECRET"),
                                           os.getenv("TWITTER_ACCESS_TOKEN"),
                                           os.getenv("TWITTER_ACCESS_SECRET"),
                                           api_version='2')

        if self.api_client_inner is not None:
            self.is_authenticated = True

    def reset_request_count(self):
        self.current_request_count["following"] = 0
        self.current_request_count["username"] = 0

    def handle_request_json(self, request_type, request, params=None):
        assert (request_type in ["following", "username"])
        if self.current_request_count[request_type] >= self.MAX_REQUEST_NUM[request_type]:
            print(f"Reached API limit, sleeping for {self.WAIT_MINUTES} minutes...")
            time.sleep(self.WAIT_MINUTES * 60)
            print(f"Sleep finished, resuming work...")
            self.reset_request_count()

        self.current_request_count[request_type] += 1
        response = self.api_client_inner.request(request, params)
        return response.json()
