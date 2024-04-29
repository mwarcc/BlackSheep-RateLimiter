# blacksheep_ratelimiter
blacksheep_ratelimiter is a rate-limiting middleware designed for the asynchronous web framework BlackSheep. With this middleware, you can apply rate limits to any of the routers within your application

# How to apply ratelimit to a router

```python
@app.router.get('/')
@blacksheep_ratelimiter.rate_limit(limit=15, per=timedelta(minutes=1))
async def home(request: Request):
    return Response(200, content=Content(b"text/plain", b"Hello, World!"))
```
Here's how you can apply rate limiting to a router using BlackSheep-RateLimiter. In this example, we're setting a rate limit of 10 requests per minute for the '/' route. Any requests beyond this limit within the specified window will receive a response indicating that they've been rate-limited.

# How to apply ratelimit to a header

```python
@app.router.get('/')
@blacksheep_ratelimiter.rate_limit_with_header(limit=15, per=timedelta(minutes=1), header_name="Authorization", header_value_regex=r'^Bearer\s.*')
async def home(request: Request):
    return Response(200, content=Content(b"text/plain", b"Hello, World!"))
```
Here's how you can apply rate limiting to a rheaderr using BlackSheep-RateLimiter. In this example, we're setting a rate limit of 10 requests per minute for the '/' route. *header_value_regex*=r'^Bearer\s.*' specifies that the header value must start with 'Bearer' followed by a space and any characters.

# Return own API responses
You can return your own respones (html, json, Response..) by creating a function that will return the response.
```python
async def custom_response(request: Request):
    return Response(200, content=Content(b"application/json", json.dumps({"message": "Hello, World!"}).encode()))
```
Now, specify the 'custom_ratelimit_response' parameter in the decorator calling the function.

```python
@blacksheep_ratelimiter.rate_limit(custom_ratelimit_response=custom_response)
```

# Allow local IP addresses and Blacklist IPs (Deleted for now)
You can allow environment and blacklist IPS this way:
```python
@app.on_start
async def startup():
    blacksheep_ratelimiter.allow_environment()
    blacksheep_ratelimiter.add_blacklist(ips=["IPS"])
```
You can return own API responses aswell using 'custom_blacklisted_response'.
