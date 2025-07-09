_stop_requested = False

def request_stop():
    global _stop_requested
    _stop_requested = True

def clear_stop():
    global _stop_requested
    _stop_requested = False

def is_stop_requested():
    return _stop_requested
