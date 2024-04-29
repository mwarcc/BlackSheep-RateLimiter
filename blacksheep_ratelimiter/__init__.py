from functools import wraps
from datetime import datetime, timedelta
from blacksheep import Application, Request, Response, Content
from blacksheep.server.responses import json
from collections import defaultdict
import json as json_module
import re



def rate_limit(limit: int, per: timedelta, custom_ratelimit_response=None):
    storage = defaultdict(lambda: {"count": 0, "reset_time": None})

    def decorator(func):
        @wraps(func)
        async def wrapper(app: Application, request: Request) -> Response:
            remote_addr = request.client_ip
            now = datetime.utcnow()

            if storage[remote_addr]["reset_time"] is None or now > storage[remote_addr]["reset_time"]:
                storage[remote_addr] = {"count": 1, "reset_time": now + per}
                remaining_seconds = per.total_seconds()
            else:
                remaining_seconds = (storage[remote_addr]["reset_time"] - now).total_seconds()
                storage[remote_addr]["count"] += 1

            response = None
            if storage[remote_addr]["count"] > limit:
                response = custom_ratelimit_response(request) if custom_ratelimit_response else json({"error": "Rate limit exceeded"}, status=429)
            else:
                response = await func(app, request)

            response.headers.add(b"X-RateLimit-Remaining", str(int(remaining_seconds)).encode())
            return response

        return wrapper

    return decorator


def rate_limit_with_header(limit: int, per: timedelta, header_name: str, header_value_regex=None, custom_ratelimit_response=None, custom_header_missing_response=None, custom_header_value_mismatch_response=None):
    storage = defaultdict(lambda: {"count": 0, "reset_time": None})

    def decorator(func):
        @wraps(func)
        async def wrapper(app: Application, request: Request) -> Response:
            header_name_bytes = header_name.encode('utf-8')
            header_value_tuple = request.headers.get(header_name_bytes)
            header_value = header_value_tuple[0] if header_value_tuple else None

            if header_value is None or header_value == "" or header_value == '':
                if custom_header_missing_response is not None:
                    return await custom_header_missing_response(request)
                
                if custom_ratelimit_response is not None:
                    return await custom_ratelimit_response(request)
                
                return json({"error": "Header value is missing"}, status=400)

            if header_value_regex is not None:
                header_value_regex_bytes = header_value_regex.encode('utf-8')

                if not re.match(header_value_regex_bytes, header_value):
                    if custom_header_value_mismatch_response is not None:
                        return await custom_header_value_mismatch_response(request)
                    
                    return json({"error": "Header value does not match required pattern"}, status=400)

            remote_addr = f"{request.client_ip}-{header_value}"
            now = datetime.utcnow()

            if storage[remote_addr]["reset_time"] is None or now > storage[remote_addr]["reset_time"]:
                storage[remote_addr] = {"count": 1, "reset_time": now + per}
                remaining_seconds = per.total_seconds()
            else:
                remaining_seconds = (storage[remote_addr]["reset_time"] - now).total_seconds()
                storage[remote_addr]["count"] += 1

            if storage[remote_addr]["count"] > limit:
                response = custom_ratelimit_response(request) if custom_ratelimit_response else json({"error": "Rate limit exceeded"}, status=429)
                response.headers.add(b"X-RateLimit-Remaining", str(int(remaining_seconds)).encode())
            else:
                response = await func(app, request)
             
            return response

        return wrapper

    return decorator
