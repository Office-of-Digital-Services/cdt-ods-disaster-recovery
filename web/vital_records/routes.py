app_name = "vital_records"


class Routes:
    index = "index"
    login = "login"
    request_start = "request_start"
    request_type = "request_type"
    request_statement = "request_statement"
    request_name = "request_name"
    request_county = "request_county"
    request_dob = "request_dob"
    request_parents = "request_parents"
    request_order = "request_order"
    request_submit = "request_submit"
    request_submitted = "request_submitted"
    unverified = "unverified"

    @staticmethod
    def app_route(route_name):
        return f"{app_name}:{route_name}"
