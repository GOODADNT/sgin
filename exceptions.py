class BBSAPIException(Exception):
    pass


class RegexMatchException(BBSAPIException):
    pass


class JSONParseException(BBSAPIException):
    pass
