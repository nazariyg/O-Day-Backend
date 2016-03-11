def get_bool_query_str_param(param_value):
    param_value = param_value.strip()
    param_value = param_value.lower()
    return param_value in ["1", "true", "on", "yes"]


def get_request_ip(request):
    return request.META["REMOTE_ADDR"]
