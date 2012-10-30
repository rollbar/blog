import getpass
import os
import sys

from fabric.api import run, local, cd, env, roles, execute
import requests

CODE_DIR = '/home/deploy/www/blog'

env.roledefs = {
    'web': ['web1', 'web2', 'web3'],
}


def deploy():
    # pre-roll checks
    check_user()
    check_current_directory()

    # do a local git pull, so the revision # when we record the deploy is correct
    local("git pull")

    # do the roll.
    # execute() will call the passed-in function, honoring host/role decorators.
    execute(update_webs)


@roles('web')
def update_webs():
    with cd(CODE_DIR):
        run("git pull")


def check_user():
    if getpass.getuser() != 'deploy':
        print "This command should be run as deploy. Run like: sudo -u deploy fab deploy"
        sys.exit(1)


def check_current_directory():
    # check if we have production.ini. if not, we're in the wrong place.
    if not os.path.isfile('_config.yml'):
        print "This command should be run from the project root."
        sys.exit(1)
