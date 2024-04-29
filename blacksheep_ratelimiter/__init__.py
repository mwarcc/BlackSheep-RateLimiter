from typing import Callable, List
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta
from blacksheep.server.responses import json
from blacksheep.server import application
from blacksheep import Request
import re

blacklisted_ips: List[str] = []
whitelisted_ips: List[str] = []

def add_blacklist(ips: List[str]):
    """
    Add IP addresses to the blacklist.
    
    Args:
        ips (list): List of IP addresses to be added to the blacklist.
    """
    global blacklisted_ips
    blacklisted_ips.extend(ips)

def add_whitelist(ips: List[str]):
    """
    Add IP addresses to the whitelist.
    
    Args:
        ips (list): List of IP addresses to be added to the whitelist.
    """
    global whitelisted_ips
    whitelisted_ips.extend(ips)

def allow_environment():
    """
    Allow local IP addresses based on environment.
    """
    local_ips = ["127.0.0.1", "::1", ":1"]
    add_whitelist(local_ips)

def rate_limiter(limit: int, window: timedelta, custom_ratelimit_response: Callable = None, custom_blacklisted_response: Callable = None) -> Callable:
    """
    A decorator function to limit the rate of incoming requests to a given API endpoint.

    Args:
        limit (int): The maximum number of requests allowed within the specified window.
        window (timedelta): The time window within which the requests are counted.
        custom_response (Callable): A custom response function to be called when the rate limit is exceeded.

    Returns:
        Callable: The decorator function.

    Example:
        @server.router.get("/example")
        @rate_limiter(limit=10, window=timedelta(minutes=1), custom_response=None)
        async def example_handler(request: Request):
            return json({"message": "Hello, World!"})
    """
    request_counts = defaultdict(list)
    
    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        async def wrapped(request: Request, *args, **kwargs):
            global blacklisted_ips
            ip_address = request.client_ip

            if ip_address in whitelisted_ips:
                return await handler(request, *args, **kwargs)

            if ip_address in blacklisted_ips:
                if custom_blacklisted_response:
                    return await custom_blacklisted_response(request)
                
                return json(data={
                    "status": 403, "description": "Forbidden"
                }, status=403)

            current_time = datetime.now()
            request_counts[ip_address] = [timestamp for timestamp in request_counts[ip_address] if current_time - timestamp <= window]

            if len(request_counts[ip_address]) >= limit:
                if custom_ratelimit_response:
                    return await custom_ratelimit_response(request)
                else:
                    retry_after = int((request_counts[ip_address][0] + window - current_time).total_seconds() if request_counts[ip_address] else 0)
                    return json({
                        "error": "Rate limit exceeded", "message": "You have exceeded the rate limit. Please try again later.",
                        "retry_after": retry_after
                    }, status=429)
            
            request_counts[ip_address].append(current_time)
            return await handler(request, *args, **kwargs)
        
        return wrapped
    
    return decorator


def rate_limiter_with_header(limit: int, window: timedelta, header_name: str, require_not_empty: bool = False, header_value_regex: str = None, custom_ratelimit_response: Callable = None, custom_blacklisted_response: Callable = None, custom_empty_header_response: Callable = None, custom_invalid_value_response: Callable = None) -> Callable:
    """
    A decorator function to limit the rate of incoming requests to a given API endpoint based on a specific header.

    Args:
        limit (int): The maximum number of requests allowed within the specified window.
        window (timedelta): The time window within which the requests are counted.
        header_name (str): The name of the header to check for rate limiting.
        require_not_empty (bool): Whether the header value must not be empty.
        header_value_regex (str): Regex pattern to match against the header value.
        custom_ratelimit_response (Callable): A custom response function to be called when the rate limit is exceeded.
        custom_blacklisted_response (Callable): A custom response function to be called when the IP address is blacklisted.
        custom_empty_header_response (Callable): A custom response function to be called when the header is empty.
        custom_invalid_value_response (Callable): A custom response function to be called when the header value is invalid.

    Returns:
        Callable: The decorator function.
    """
    request_counts = defaultdict(list)
    
    header_name_bytes = header_name.encode('utf-8')
    
    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        async def wrapped(request: Request, *args, **kwargs):
            ip_address = request.client_ip

            if ip_address in whitelisted_ips:
                return await handler(request, *args, **kwargs)

            if ip_address in blacklisted_ips:
                if custom_blacklisted_response:
                    return await custom_blacklisted_response(request)
                
                return json({"status": 403, "description": "Forbidden"}, status=403)

            current_time = datetime.now()

            header_value_tuple = request.headers.get(header_name_bytes)
            header_value = header_value_tuple[0] if header_value_tuple else None
            
            if header_value is not None:
                header_value = header_value.decode('utf-8')
                
                if require_not_empty and not header_value.strip():
                    if custom_empty_header_response:
                        return await custom_empty_header_response(request)
                    else:
                        return json({"error": "Header value cannot be empty"}, status=400)

                if header_value_regex and not re.match(header_value_regex, header_value):
                    if custom_invalid_value_response:
                        return await custom_invalid_value_response(request)
                    else:
                        return json({"error": "Invalid header value"}, status=400)

                request_counts[(ip_address, header_value)] = [
                    timestamp for timestamp in request_counts[(ip_address, header_value)]
                    if current_time - timestamp <= window
                ]

                if len(request_counts[(ip_address, header_value)]) >= limit:
                    if custom_ratelimit_response:
                        return await custom_ratelimit_response(request)
                    else:
                        retry_after = int(
                            (request_counts[(ip_address, header_value)][0] + window - current_time).total_seconds()
                            if request_counts[(ip_address, header_value)]
                            else 0
                        )
                        return json({
                            "error": "Rate limit exceeded", 
                            "message": "You have exceeded the rate limit. Please try again later.",
                            "retry_after": retry_after
                        }, status=429)
            
                request_counts[(ip_address, header_value)].append(current_time)
            else:
                pass

            return await handler(request, *args, **kwargs)
        
        return wrapped
    
    return decorator