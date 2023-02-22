from django_user_agents.utils import get_user_agent

from client.models import ActivityLog

import json
import re

from appointment_api.settings import ACTIVATE_LOGS, LOG_AUTHENTICATED_USERS_ONLY, IP_ADDRESS_HEADERS


API_URLS = ["/api/", "/o/to"]

url = r"^/api/([v1,v2]*)/(\w{0,20})/?$"
url1 = r"^/api/([v1,v2]*)/(\w{0,20})/(\w{0,20})/?$"
url2 = r"^/api/([v1,v2]*)/(\w{0,20})/([0-9]+)/?$"
url3 = r"^/api/([v1,v2]*)/(\w{0,20})/([0-9]+)/(\w{0,50})/?$"
patterns = [
    {"values": ["version", "resources", "extra_resource"], "pattern":url1},
    {"values": ["version", "resources"], "pattern":url},
    {"values": ["version", "resources", "id"], "pattern": url2},
    {"values": ["version", "resources", "id", "extra_resource"], "pattern": url3}
]


def get_ip_address(request):
    for header in IP_ADDRESS_HEADERS:
        addr = request.META.get(header)
        if addr:
            return addr.split(',')[0].strip()


class UserLoggerMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before the view (and later middleware) are called.
        response = self.get_response(request)

        # Code to be executed for each request/response after the view is called.

        # Confirm logging is enabled
        if not ACTIVATE_LOGS:
            return response

        if LOG_AUTHENTICATED_USERS_ONLY and not request.user.is_authenticated:
            return response

        if request.path[:5] not in API_URLS:
            return response

        # Update user activity
        if request.user.is_authenticated:
            getattr(request.user, 'update_last_activity', lambda: 1)()

        # Add log for the user
        user = request.user.id
        self.writelog(user, request, response)

        return response

    def writelog(self, user, request, response):
        os_br_dev = self.get_browser_os_device(request)
        ActivityLog.objects.create(
            user_id=user,
            request_url=request.build_absolute_uri()[:255],
            request_method=request.method,
            response_code=response.status_code,
            ip_address=get_ip_address(request),
            extra_data=self.parse_url(request.path),
            os=os_br_dev["os"],
            device=os_br_dev["device"],
            browser=os_br_dev["browser"]
        )

    def get_action_message(self, request, response):
        pass

    def get_models_from_urls(self):
        '''
        api/v1/stuffs
        api/v1/stuffs/id
        api/v1/stufffs/id/sutff
        :return:
        '''
        test_url = "/api/v1/stuffs"
        test_url2 = "/api/v1/stuffs/2"
        test_url3 = "/api/v1/stufffs/3/sutff"
        tests = [test_url, test_url2, test_url3]
        for test_urla in tests:
            print(self.parse_url(test_urla))

    def parse_url_by_value(self, value, transaction):
        pattern = re.compile(value, flags=re.IGNORECASE)
        return pattern.findall(transaction)

    def parse_url(self, url):
        results_all = [{"results": self.parse_url_by_value(d["pattern"], url), "name": d["values"]} for d in patterns]
        results = filter(lambda x: len(x["results"]) > 0, results_all)
        # print(dir(results))
        try:
            if len(results) > 0:
                res = results[0]
                return json.dumps({res["name"][i]: k for i, k in enumerate(res["results"][0])})

            return None
        except Exception:
            return None

    def parse_result_as_string(self, res):
        pass

    def get_browser_os_device(self, request):
        user_agent = get_user_agent(request)
        return {"os": user_agent.os, "browser": user_agent.browser, "device": str(user_agent)}
