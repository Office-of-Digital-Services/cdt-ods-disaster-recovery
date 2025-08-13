app_name = "vital_records"


class Routes:
    index = "index"
    login = "login"
    request_start = "request_start"
    request_statement = "request_statement"
    birth_request_name = "birth_request_name"
    birth_request_county = "birth_request_county"
    birth_request_dob = "birth_request_dob"
    birth_request_parents = "birth_request_parents"
    request_order = "request_order"
    request_submit = "request_submit"
    request_submitted = "request_submitted"
    unverified = "unverified"

    @staticmethod
    def app_route(route_name):
        return f"{app_name}:{route_name}"
