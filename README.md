# Blacksheep Rate Limiter Middleware

This is a rate limiter middleware for the Asynchronous Web Framework [Blacksheep](https://github.com/Neoteroi/BlackSheep). It allows you to easily add rate limiting to your Blacksheep applications using decorators.

## Installation

Currently, the middleware requires only Blacksheep to function. Ensure you have Blacksheep installed in your environment:

```bash
pip install blacksheep
```

## Usage
To use the rate limiter middleware, you need to decorate your request handler functions with the provided decorators. Here are some examples to demonstrate how to use it:

## Basic Rate Limiting
This example shows how to limit requests to an endpoint to a maximum of 5 requests per minute.
```python
@app.router.get('/')
@rate_limit(limit=5, per=timedelta(minutes=1))
async def test(request: Request):
    return json({'success': True})
```

## Rate Limiting with Headers
This example demonstrates how to apply rate limiting based on a specific header, such as an Authorization header with a Bearer token.
```python
@app.router.get('/home')
@rate_limit_with_header(limit=15, per=timedelta(minutes=1), header_name="Authorization", header_value_regex=r'^Bearer\s.*')
async def home(application: Application, request: Request):
    code...
```

## Dynamic Rate Limiting
This example illustrates how to apply dynamic rate limiting based on custom logic, such as allowing 10 requesst every 1 second.
```python
@app.router.get('/dynamic')
@dynamic_rate_limit(max_requests=10, per_seconds=1)
async def dynamic(application: Application, request: Request):
    code...
```

## Custom Rate Limit Responses
This example shows how to provide a custom response when the rate limit is exceeded.
```python
async def custom_response():
    ...

@app.router.get('/custom')
@rate_limit(custom_ratelimit_response=custom_response)
async def custom_response(application: Application, request: Request):
    code...
```

# Running the Application
Since this is a middleware for a Blacksheep application, it can't be started by simply double-clicking the file. Use a command like the following to run your Blacksheep application:
```bash
uvicorn your_module_name:app --reload --workers {workers}
```
