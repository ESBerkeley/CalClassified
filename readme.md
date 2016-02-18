# Prerequisites

# Mac Only

`xcode-select --install` 

and install Brew by following the instructions here http://brew.sh/ then

`brew install libxml2`

`brew install libxslt`

`brew link libxml2 --force`

`brew link libxslt --force`

# Install PIP and Python then run

`sudo pip install virtualenv`

`sudo pip install virtualenvwrapper`

`virtualenv env`

`source ./env/bin/activate`

`pip install -r requirements.txt`

# Migrate Database

`mkdir logs`

`cd cc`

`python manage.py createcachetable user_sessions`

`python manage.py syncdb`

### On Mac OS X...
`brew install elasticsearch`

### On Ubuntu...
`apt-get install elasticsearch`

### Starting ElasticSearch on Linux
`sudo service elasticsearch start`

### On Mac OS X
`ln -sfv /usr/local/opt/elasticsearch/*.plist ~/Library/LaunchAgents`

`launchctl load ~/Library/LaunchAgents/homebrew.mxcl.elasticsearch.plist`

### On Windows
Go to the elasticsearch folder and run 

`elasticsearch.bat`

# Generate database

`python manage.py testdbgen`

# Rebuild Index

`python manage.py rebuild_index`

# Start server

`python manage.py runserver`


### Additional Resources
http://groups.google.com/group/django-users/browse_thread/thread/712946dfabaa2ec1
http://stackoverflow.com/questions/5871730/need-a-minimal-django-file-upload-example
