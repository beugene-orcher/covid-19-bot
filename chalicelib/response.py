from json import dumps as json_dumps

from chalice import Response


class CustomJSONResponse(Response):
    """Covering chalice.Response object for inner usage"""
    headers = {'Content-Type': 'application/json'}

    def __init__(self, body, code):
        self.body, self.code = body, code
        self.__validate()
        super().__init__(
            body=json_dumps(self.body),
            status_code=self.code,
            headers=self.headers
        )

    def __validate(self):
        """Validate set attrs"""
        if not isinstance(self.body, dict):
            raise CustomResponseError(
                f'body must be dict, given {type(self.body)}'
            )
        if not self.body.get('message'):
            raise CustomResponseError(
                f'body must include message key'
            )
        if not isinstance(self.code, int):
            raise CustomResponseError(
                f'code must be int, given {type(self.code)}'
            )


class CustomResponseError(Exception):

    def __init__(self, message):
        super().__init__(message)
