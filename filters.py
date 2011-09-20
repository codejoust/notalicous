import cherrypy
def allow_post():
	if cherrypy.request.method.upper() != 'POST':
		cherrypy.response.headers['Allow'] = 'POST'
		raise cherrypy.HTTPError(405)

def allowed_methods(methods=['GET','POST']):
	method = cherrypy.request.method.upper()
	if method not in methods:
		cherrypy.response.headers['Allow'] = ", ".join(methods)
		raise cherrypy.HTTPError(405)

#jinja autoescape
def guess_autoescape(template_name):
	if template_name is None or '.' not in template_name:
		return False
	ext = template_name.rsplit('.', 1)[1]
	return ext in ('html','htm','xml')
