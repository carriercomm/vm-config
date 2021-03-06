from util import *

config = load_config()
json_data = config['mysql'] if 'mysql' in config else dict()

user = json_data['user'] if 'user' in json_data else 'root'
password = json_data['root_password'] if 'root_password' in json_data else '1qazxsdw23edc'
root_password = json_data['root_password'] if 'root_password' in json_data else password

version = json_data['version'] if 'version' in json_data else '5.6'

os_user = json_data['os_user'] if 'os_user' in json_data else 'mysql'
os_group = json_data['os_group'] if 'os_group' in json_data else os_user

# Configure mysql
call('echo "mysql-server mysql-server/root_password password %s" | debconf-set-selections' % root_password)
call('echo "mysql-server mysql-server/root_password_again password %s" | debconf-set-selections' % root_password)

# Install packages from manager
install('mysql-server-%(v)s mysql-client-%(v)s' % {'v': version})

# Post config mysql
echo('Post installation configuring MySQL...')
replace('/etc/mysql/my.cnf', 'bind-address', '#ba:')

add_group(os_group)
add_user(os_user, os_group)
chown('/etc/mysql/my.cnf', os_user, os_group)
call('/etc/init.d/mysql restart')

if not user == 'root':
    # TODO: Add user
    print 'User creation not implemented'

queries = [
    'create user %(user)s@10.0.2.2 identified by "%(password)s";',
    'grant all privileges on *.* to %(user)s@10.0.2.2 with grant option;',
    'flush privileges;',

    'select user, host from mysql.user where user="%(user)s";'
]

for query in queries:
    call("mysql -uroot -p%(password)s -e '%(query)s'" % {
        "password": root_password,
        "query": query % {"user": user, "password": password}
    })

echo('... Done')
