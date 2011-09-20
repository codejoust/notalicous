import cherrypy
import database as db
import cgi, json, jinja2, os, urllib2, re
from filters import *
from facebook import FacebookAPI as FBApi
cherrypy.tools.allow = cherrypy.Tool('on_start_resource', allowed_methods)
cherrypy.tools.allow_post = cherrypy.Tool('on_start_resource', allow_post)

env = jinja2.Environment(autoescape=guess_autoescape,
						 loader=jinja2.FileSystemLoader('views'),
						 extensions=['jinja2.ext.autoescape'])
current_dir = os.path.dirname(os.path.abspath(__file__))

class FacebookConnect:
	@cherrypy.expose
	def connect(self):
		raise cherrypy.HTTPRedirect(FBApi.authorize_url())
	@cherrypy.expose
	def register(self, sessionid):
		return ''
	@cherrypy.expose
	def callback(self, error=None, error_reason=None, error_description=None, code=None):
		if error and error_reason == 'user_denied': return 'Please authorize!'
		if not code: return 'Error from facebook'
		fbapi = FBApi(None)
		out = fbapi.callback(code)
		obj = db.loadUser(token=fbapi.token, fb=fbapi.me())
		cookie = cherrypy.response.cookie
		cookie['session_id'] = obj.id
		cookie['session_id']['max-age'] = int(out['expires'][0])
		cookie['session_id']['path'] = '/'
		cookie['session_key'] = obj.code
		cookie['session_key']['max-age'] = int(out['expires'][0])
		cookie['session_key']['path'] = '/'
		return '''Logged in! Loading... 
			<script type="text/javascript">
				if (window.opener){
					window.opener.login_evt();
				}
				setTimeout(window.close, 300);
			</script>
		'''
class MainStart:
	fb = FacebookConnect()
	@cherrypy.expose
	def index(self, **params):
		return env.get_template('welcome.tpl.html').render(top_notes=db.Note.objects.only('permalink','taken', 'name').order_by('-taken')[:8])
	@cherrypy.expose
	def new(self, **params):
		return env.get_template('create.tpl.html').render()
	@cherrypy.expose
	def view(self,permalink,**params):
		return env.get_template('view.tpl.html').render(note=db.Note.objects.get(permalink=permalink))
	@cherrypy.expose
	def note(self,permalink,**params):
		return env.get_template('view.tpl.html').render(note=db.Note.objects.get(permalink=permalink))
	@cherrypy.tools.allow_post()
	@cherrypy.expose
	def submit_note(self, note_id, **params):
		note = db.Note.objects.with_id(note_id)
		groups_ans = []
		for gidx, group in enumerate(note.question_groups):
			if ('pn-%i' % (gidx + 1)) in params:
				answers = []
				groups_ans.append({'name': group.header, 'type': group.qtype.key, 'answers': answers})
				for qidx, question in enumerate(group.questions):
					key = 'pn-%iq%i' % (gidx+1, qidx+1)
					if key in params:
						answers.append((question, params[key]))
					elif group.qtype.key=='yes-no':
						answers.append((question, False))
		note_content = env.get_template('publish.tpl.html').render(answers=groups_ans, note=note)
		if 'format' in params:
			if params['format']=='json':
				return json.dumps({'data':groups_ans,'html':note_content})
			elif params['format'] == 'html':
				return note_content
		else:
			if ('session_id' not in cherrypy.request.cookie.keys()):
				raise cherrypy.HTTPRedirect(FBApi.authorize_url())
			else:
				fbapi = FBApi(str(cherrypy.request.cookie['session_key'].value))
				db.Note.objects(id=note.id).update_one(inc__taken=1)
				out = json.loads(fbapi.publish_note(note.name, ' '.join(note_content.split())))
				if 'id' in out:
					raise cherrypy.HTTPRedirect('/done?note_id='+out['id'])
				else:
					return 'Something went wrong... Email the developers to get this fixed.'
	@cherrypy.expose
	def done(self, note_id):
		out = {'id': int(note_id)}
		return env.get_template('done.tpl.html').render(fbpub=out)
	@cherrypy.expose
	def take(self,permalink,**params):
		note = db.Note.objects.get(permalink=permalink)
		return env.get_template('view.tpl.html').render(note=note)
	@cherrypy.expose
	def notes(self, **params):
		return env.get_template('notes.tpl.html').render(notes=db.Note.objects[:20])
	@cherrypy.expose
	@cherrypy.tools.allow_post()
	def submit(self,data=None):
		err = False
		if (data is None and len(data) == 0): err = 'No data!'#raise cherrypy.HTTPError(502)
		if ('session_id' not in cherrypy.request.cookie.keys()): err = 'Login Error'#raise cherrypy.HTTPError(503)
		if (err):
			return json.dumps({'success':False, 'error': err})
		newnote = json.loads(data)
		note = db.createNote(newnote, cherrypy.request.cookie['session_id'].value)
		return json.dumps({'permalink':note.permalink, 'success': True})

# for wsgi deployment.
application = cherrypy.tree.mount(MainStart())
#app = cherrypy.quickstart(MainStart(), '/', 'app.conf')
