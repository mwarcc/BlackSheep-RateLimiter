# blacksheep_ratelimiter
blacksheep_ratelimiter is a rate-limiting middleware designed for the asynchronous web framework BlackSheep. With this middleware, you can apply rate limits to any of the routers within your application

# How to apply ratelimit to a router

```python
@app.router.get('/')
@blacksheep_ratelimiter.rate_limiter(limit=10, window=timedelta(minutes=1))
async def home(request: Request):
    return Response(200, content=Content(b"text/plain", b"Hello, World!"))
```
Here's how you can apply rate limiting to a router using BlackSheep-RateLimiter. In this example, we're setting a rate limit of 10 requests per minute for the '/' route. Any requests beyond this limit within the specified window will receive a response indicating that they've been rate-limited.

# How to apply ratelimit to a header

```python
@app.router.get('/')
@blacksheep_ratelimiter.rate_limiter_with_header(limit=10, window=timedelta(minutes=1), header_name='Authorization', require_not_empty=True, header_value_regex=r'^Bearer\s.*')
async def home(request: Request):
    return Response(200, content=Content(b"text/plain", b"Hello, World!"))
```
Here's how you can apply rate limiting to a header using BlackSheep-RateLimiter. In this example, we're setting a rate limit of 10 requests per minute for the '/' route. *require_not_empty*=True ensures the header value must not be empty, while *header_value_regex*=r'^Bearer\s.*' specifies that the header value must start with 'Bearer' followed by a space and any characters.

