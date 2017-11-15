# external imports
import operator
from json import dumps, loads

import jinja2
from google.appengine.ext import db
from google.appengine.api import memcache, users
import logging
import webapp2
from os.path import join, dirname
# appengine_config.py
from google.appengine.ext import vendor

# Add any libraries install in the "lib" folder.
vendor.add('lib')
from oauth2client.contrib.appengine import OAuth2DecoratorFromClientSecrets

foldername = dirname(__file__)

decorator = OAuth2DecoratorFromClientSecrets(join(foldername, 'client_secrets.json'),
  'https://www.googleapis.com/auth/drive.metadata.readonly')


def require_profile(func):
    def wrap(clss, *args, **kwargs):
        contents = open(join(foldername, 'token'), "r").read(-1)
        logging.info("tokens %s %s "% (contents, clss.request.headers.get('token')))
        token = clss.request.headers.get('token') == contents
        profile = users.get_current_user()
        logging.info(str(token)+" "+str(profile))
        if profile or token:
            return func(clss, *args, **kwargs)
        elif not profile:
            clss.redirect(users.create_login_url(clss.request.uri))
        else:
            clss.error(405)
    return wrap


class PageHandler(webapp2.RequestHandler):
    """Serves the instruments page"""

    @require_profile
    def get(self):
        self.write_html_file(self.page)

    def write_html_file(self, filename, add_profile=True, inject_header=True):
        #folder = os.path.dirname(os.path.realpath(__file__))
        html_folder = foldername# os.path.join(folder, '')
        file_path = join(html_folder, filename)
        with open(file_path, 'r') as f:
            html = f.read()
        # todo: add profiles
        '''
        if inject_header:  # also adds profile html also
            try:
                profile = self.get_profile_dict()
                html = self._inject_header(html, profile)
                html = self._add_profile_html(html, profile)
            except:
                pass
        elif add_profile:
            try:
                profile = self.get_profile_dict()
                html = self._add_profile_html(base_html=html,
                                              profile=profile,
                                              html_folder=html_folder)
            except:
                pass
        '''
        self.response.out.write(html)


class DrawPage(PageHandler):
    page = "index.html"


class Drawing(db.Model):
    data = db.TextProperty()
    time = db.DateTimeProperty(auto_now_add=True)

class SavePXON(webapp2.RequestHandler):
    @require_profile
    def post(self):
        pix_data = self.request.body
        pd = Drawing(data=pix_data)
        pd.put()
        memcache.set('latest', pix_data)

    @require_profile
    def get(self):
        pix_data = memcache.get('latest')
        if pix_data:
            logging.info(pix_data)
            self.response.out.write(pix_data)
        else:
            pix_data = Drawing().all().order('-time').get().data
            self.response.out.write(pix_data)


app = webapp2.WSGIApplication([
    (decorator.callback_path, decorator.callback_handler()),
    ('/', DrawPage),
    ('/save', SavePXON)
], debug=False)  # change to True to get responses w/out error.html
