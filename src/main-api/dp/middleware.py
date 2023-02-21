class MyMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Allow-Methods"] = "GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS"
        response["Access-Control-Max-Age"] = "2000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        return response
