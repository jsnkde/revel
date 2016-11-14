def ExampleMiddleware(get_response):
	def middleware(request):
		request.full_host = request.get_full_path()
		response = get_response(request)
		return response

	return middleware