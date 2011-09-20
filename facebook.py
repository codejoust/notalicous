import urllib2, cgi, json, urllib, ConfigParser

class FacebookAPI():
    GRAPH_BASE = 'https://graph.facebook.com/'
    conf = {}
    def __init__(self,token=None):
        self.token = token
        configparser = ConfigParser.ConfigParser()
        configparser.read('notalicous.cfg')
        self.conf = dict(configparser.items('facebook'))
    def publish_note(self, profile_id, data = {}):
        call_graph('/%s/notes?' % profile_id, data)
    def is_friends(self, user1, user2):
        pass
    @classmethod
    def authorize_url(self):
        return '%soauth/authorize?client_id=%s&redirect_uri=%s&scope=create_note&display=popup' % (self.GRAPH_BASE, self.conf['application_id'], self.conf['redirect_uri'])
    def callback(self, code):
        out = cgi.parse_qs(self._call_graph('oauth/access_token', { 'client_id': str(self.conf['application_id']), 'redirect_uri': self.conf['redirect_uri'], 'client_secret': self.conf['client_secret'], 'code': code }))
        self.token = out['access_token'][0]
        return out
	def valid_token(self):
		return 'error' in json.loads(self._call_graph('176192742413831'))
    def publish_note(self, subject, message):
        return self._call_graph('me/notes', {}, {'access_token': self.token, 'subject': subject, 'message': message})
    def me(self):
        return json.loads(self._call_graph('me'))
    def _call_graph(self,path,urldata=None, postdata=None):
        query = ''
        if self.token is not None and urldata is not None:
            urldata['token'] = self.token
        if urldata is not None:
            query = '?' + '&'.join([a+'='+b for a,b in urldata.iteritems()])
        if self.token != None and urldata == None:
            query = '?access_token='+self.token
        url= self.GRAPH_BASE+path+query
        if postdata is None:
           return urllib2.urlopen(url).read()
        else:
           try: return urllib2.urlopen(url, urllib.urlencode(postdata)).read()
           except urllib2.URLError, e: return e.read()
               
           
