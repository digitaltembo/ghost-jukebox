from flask_httpauth import HTTPBasicAuth
from ghost_jukebox import conf
from functools import wraps

# put straightforward httpbasic auth on each page, just cause I don't want undue traffic really
# might remove this eventually, who knows
basic_auth = HTTPBasicAuth()

# Just going to do a one user system for now, with username and password configured in environment variables
users = {conf.username: conf.password}

# I am ok with this as a super insecure authentication method so long as I am the only user
@basic_auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
        return None

# make it so that you have to be connected to my home network to do the important bits
def is_home(request):
    request_ip = request.environ['HTTP_X_FORWARDED_FOR']
    return request_ip == conf.host_ip

def home_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_home(request):
            return f(*args, **kwargs)
        else:
            abort(403)
    return decorated_function
        

