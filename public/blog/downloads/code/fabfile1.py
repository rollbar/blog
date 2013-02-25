import sys

from fabric.api import run, local, cd, env, roles, execute
import requests

env.hosts = ['web1', 'web2']


def deploy():
    # pre-roll checks
    check_user()

    # do the roll.
    update_and_restart()

    # post-roll tasks
    rollbar_record_deploy()


def update_and_restart():
    code_dir = '/home/deploy/www/mox'
    with cd(code_dir):
        run("git pull")
        run("pip install -r requirements.txt")
        run("supervisorctl restart web1")
        run("supervisorctl restart web2")


def check_user():
    if local('whoami', capture=True) != 'deploy':
        print "This command should be run as deploy. Run like: sudo -u deploy fab deploy"
        sys.exit(1)


def rollbar_record_deploy():
    # read access_token from production.ini
    access_token = local("grep 'rollbar.access_token' production.ini | sed 's/^.* = //g'", 
        capture=True)

    environment = 'production'
    local_username = local('whoami', capture=True)
    revision = local('git log -n 1 --pretty=format:"%H"', capture=True)

    resp = requests.post('https://api.rollbar.com/api/1/deploy/', {
        'access_token': access_token,
        'environment': environment,
        'local_username': local_username,
        'revision': revision
    }, timeout=3)

    if resp.status_code == 200:
        print "Deploy recorded successfully"
    else:
        print "Error recording deploy:", resp.text
