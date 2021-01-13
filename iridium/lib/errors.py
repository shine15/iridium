class HttpResponseError(Exception):
    """
    Http Response Generic Error
    """
    def __init__(self, url, status_code, message):
        self.url = url
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return "Http response error - URL: {}, Status Code: {}, Message: {}".\
            format(self.url, self.status_code, self.message)
