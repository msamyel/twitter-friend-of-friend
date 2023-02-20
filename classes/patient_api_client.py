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
    current_request_count: int = 0
    MAX_REQUEST_NUM: int = 15
    WAIT_MINUTES: int = 16  # add one extra minute just in case
    
    is_authenticated: bool = False

    def __init__(self):
        load_dotenv()
        self.api_client_inner = TwitterAPI(os.getenv("TWITTER_API_KEY"),
                                           os.getenv("TWITTER_API_SECRET"),
                                           os.getenv("TWITTER_ACCESS_TOKEN"),
                                           os.getenv("TWITTER_ACCESS_SECRET"),
                                           api_version='2')
        
        if self.api_client_inner is not None:
            self.is_authenticated = True

    def handle_request_json(self, request, params):
        if self.current_request_count >= self.MAX_REQUEST_NUM:
            time.sleep(self.WAIT_MINUTES * 60)
            self.current_request_count = 0

        self.current_request_count += 1
        response = self.api_client_inner.request(request, params)
        return response.json()
