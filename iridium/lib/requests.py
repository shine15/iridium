import requests
from .errors import HttpResponseError
from enum import Enum

session = requests.Session()


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


def request(url,
            method,
            headers,
            params,
            data,
            timeout=10):
    """

    :param url:
    :param method:
    :param headers:
    :param params:
    :param data:
    :param timeout:
    :return:
    """
    try:
        api_response = session.request(
            method.value,
            url,
            headers=headers,
            params=params,
            data=data,
            timeout=timeout
        )
    except Exception as error:
        raise error

    if 200 <= api_response.status_code < 300:
        return api_response.json()
    else:
        raise HttpResponseError(
            url=url,
            status_code=api_response.status_code,
            message=api_response.text
        )
