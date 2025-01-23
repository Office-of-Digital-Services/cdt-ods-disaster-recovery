class Routes:
    def route(route_fragment: str):
        return f"oauth:{route_fragment}"

    AUTHORIZE = route("authorize")
    CANCEL = route("cancel")
    LOGIN = route("login")
    LOGOUT = route("logout")
    POST_LOGOUT = route("post_logout")
    SUCCESS = route("success")
