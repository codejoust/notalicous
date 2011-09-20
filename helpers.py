from jinja2 import Template, FileSystemLoader, Environment
import os

env = Environment(loader=FileSystemLoader('views'))

def tpl(path, ttype='html'):
	return env.get_template('%s.tpl.%s' % (path,ttype))

def conf(name):
	pass

def allow_post():
	if cherrypy.request.method.upper() != 'POST':
		cherrypy.response.headers['Allow'] = 'POST'
		raise cherrypy.HTTPError(405)

def allowed_methods(methods=['GET','POST']):
	method = cherrypy.request.method.upper()
	if method not in methods:
		cherrypy.response.headers['Allow'] = ", ".join(methods)
		raise cherrypy.HTTPError(405)
