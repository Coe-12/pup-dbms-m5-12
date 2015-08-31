import webapp2
from google.appengine.ext import ndb
import jinja2
import os
import logging
import json
import urllib
from google.appengine.api import users



JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)

class Thesis(ndb.Model):
    year = ndb.StringProperty(indexed=True)
    thesisTitle = ndb.StringProperty(indexed=True)
    abstract = ndb.StringProperty(indexed=True)
    adviser = ndb.StringProperty(indexed=True)
    section = ndb.StringProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    userName = ndb.StringProperty(indexed=False)
    userId = ndb.StringProperty(indexed=False)

class User(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    phone_number = ndb.StringProperty()
    created_date = ndb.DateTimeProperty(auto_now_add=True)

class CreateThesis(webapp2.RequestHandler):
    
    def get(self):
        thesis = Thesis.query().order(-Thesis.date).fetch()
        thesis_list = []

        for t in thesis:
            creatorId = t.userId
            created_by = ndb.Key('User', creatorId)
            thesis_list.append({
                    'year' : t.year,
                    'thesisTitle' : t.thesisTitle,
                    'abstract' : t.abstract,
                    'adviser' : t.adviser,
                    'section' : t.section,
                    'id' : t.key.id(),
                    'userName' : t.userName,
                    'first_name' : created_by.get().first_name,
                    'last_name' : created_by.get().last_name
                })
        #return list to client
        response = {
            'result' : 'OK',
            'data' : thesis_list
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

    def post(self):
        user = users.get_current_user()
        t = Thesis()
        t.thesisTitle = self.request.get('thesisTitle')
        t.abstract = self.request.get('abstract')
        t.adviser = self.request.get('adviser')
        t.year = self.request.get('year')
        t.section = self.request.get('section')
        t.userName = user.nickname()
        t.userId = user.user_id()
        t.put()

        creatorId = t.userId
        created_by = ndb.Key('User', creatorId)

        self.response.headers['Content-Type'] = 'application/json'
        response = {
            'result' : 'OK',
            'data': {
                'year' : t.year,
                'thesisTitle' : t.thesisTitle,
                'abstract' : t.abstract,
                'adviser' : t.adviser,
                'section' : t.section,
                'id' : t.key.id(),
                'userName' : t.userName,
                'first_name' : created_by.get().first_name,
                'last_name' : created_by.get().last_name
            }
        }
        self.response.out.write(json.dumps(response))

class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'

        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            template = JINJA_ENVIRONMENT.get_template('main.html')
            self.response.write(template.render(template_data))
        else:
            self.redirect('/login')
            #self.redirect(users.create_login_url(self.request.uri))

class deleteThesis(webapp2.RequestHandler):
    def get(self, thesisId):
        d = Thesis.get_by_id(int(thesisId))
        d.key.delete()
        self.redirect('/')

class login(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render())
        user = users.get_current_user()
        if user:
            template = JINJA_ENVIRONMENT.get_template('main.html')
            self.response.write(template.render(template_data))

class loginurl(webapp2.RequestHandler):
    def get(self):

        user = users.get_current_user()
        url = users.create_logout_url('/login')
        url_linktext = 'Logout'

        template_data = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        if user:
            self.redirect('/register')
        else:
            #self.redirect('/login')
            self.redirect(users.create_login_url(self.request.uri))


class register(webapp2.RequestHandler):
    def get(self):
        loggedin_user = users.get_current_user()
        if loggedin_user:
            user_key = ndb.Key('User',loggedin_user.user_id())
            user = user_key.get()
            if user:
                self.redirect('/home')
            else:
                if loggedin_user:
                    template = JINJA_ENVIRONMENT.get_template('register.html')
                    logout_url = users.create_logout_url('/login')
                    template_value = {
                        'logout_url' : logout_url
                    }
                    self.response.write(template.render(template_value))
                else:
                            login_url = users.create_login_url('/register')
                            self.redirect(login_url)
        else:
            self.redirect('/login')

    def post(self):
        loggedin_user = users.get_current_user()
        user =  User(id=loggedin_user.user_id(), email=loggedin_user.email(), first_name=self.request.get('first_name'), last_name=self.request.get('last_name'), phone_number=self.request.get('phone_number'))
        user.put()

class editThesis(webapp2.RequestHandler):
    def get(self, thesisId):
        thesis = Thesis.get_by_id(int(thesisId))
        user = users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        template_value = {
            'thesis' : thesis,
            'user' : user,
            'url' : url
        }
        template = JINJA_ENVIRONMENT.get_template('edit.html')
        self.response.write(template.render(template_value))

    def post(self,thesisId):
        thesis = Thesis.get_by_id(int(thesisId))      
        thesis.year = self.request.get('year')
        thesis.thesisTitle = self.request.get('thesisTitle')
        thesis.abstract = self.request.get('abstract')
        thesis.adviser = self.request.get('adviser')
        thesis.section = self.request.get('section')
        thesis.put()
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/home', MainPageHandler),
    ('/', MainPageHandler),
    ('/api/thesis', CreateThesis),
    ('/thesis/delete/(.*)', deleteThesis),
    ('/login', login),
    ('/loginurl', loginurl),
    ('/register', register),
    ('/thesis/edit/(.*)',editThesis)

], debug=True)