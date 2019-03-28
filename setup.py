from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from system import check_call


def initialize_scripts():
    with open('environment', 'w') as f:
        env_vars = [
            'GHOST_JUKEBOX_UNAME',
            'GHOST_JUKEBOX_PSWD',
            'GHOST_SPOTIFY_CLIENT',
            'GHOST_SPOTIFY_SECRET',
            'GHOST_HOST',
            'GHOST_DB_PATH',
            'GHOST_UPLOAD_DIR',
            'GHOST_HOST_IP'
        ]
        env = {}
        for var in env_vars:
            val = input('Value for "{}":\n'.format(var))
            env[var] = val
            f.write("{}={}\n".format(var, val))

    check_call('sudo mv environment /opt/ghost/environment'.split(' '))

    with open('infrastructure/ghost.nginx', 'r') as nginx, open('ghost.nginx', 'w') as nginx_write:
        for line in nginx.readlines():
            nginx_write.write(line.replace('HOST', env['GHOST_HOST']))
    check_call('sudo mv ghost.nginx /etc/nginx/sites-available/ghost'.split(' '))
    check_call('sudo mv infrastructure/ghost.service /etc/systemd/system'.split(' '))
    print('Now, all you need to do is to make a symlink in /etc/nginx/sites-enabled to enable it, and then do sudo systemctl ghost start')




class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        initialize_scripts()
        develop.run(self)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        initialize_scripts()
        install.run(self)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="Ghost-Jukebox",
    version="0.1",
    author="Nolan Hawkins",
    author_email="nolanhhawkins@gmail.com",
    description="A Raspberry Pi integrated music controller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/digitaltembo/ghost-jukebox/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Raspberry Pi",
    ],
    keywords="raspberry pi raspberrypi music jukebox picamera",
    
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    # dependency_links=['https://github.com/digitaltembo/python-qrcode/tarball/master#egg=package-1.0'],
    install_requires="""
        asn1crypto==0.24.0
        certifi==2018.11.29
        cffi==1.12.2
        chardet==3.0.4
        Click==7.0
        cryptography==2.6.1
        Flask==1.0.2
        Flask-HTTPAuth==3.2.4
        idna==2.8
        itsdangerous==1.1.0
        Jinja2==2.10
        MarkupSafe==1.1.1
        picamera==1.13
        Pillow==5.4.1
        pkg-resources==0.0.0
        pycparser==2.19
        pyOpenSSL==19.0.0
        pyzbar==0.1.8
        requests==2.21.0
        six==1.12.0
        urllib3==1.24.1
        Werkzeug==0.14.1
    """
)
