# Popularity for Motion

[TypePad Motion][] provides a nice community site out of the box, but one thing it is currently missing that I wanted to see was a "popular" page that shows posts that are getting a lot of favorites or comments. The TypePad API doesn't have direct support for that sort of thing, so I built it myself on top of existing TypePad APIs.

The approach I took was to create a new TypePad user that is used solely to track things that are becoming popular in the community. This makes it possible to follow popular posts without the need for a local database table, and it has an added benefit that others can follow this special user so they will see new popular content in the group on their TypePad dashboard and also on their Motion "Following" page. All of this is done without having to modify the Motion application itself.

## Installation

To try this out for yourself, we'll need to install Popularity. You will eventually be able to add this to an existing Motion community, but as this relies on a development version of TypePad Motion, I'll just document how to install to a new site for now.

I'll be using virtualenv to create the Python project and a [TypePad Group API key][apikey], you can obtain for free. You can read up on our [Contribute to Motion][contribute] guide to learn how to install Motion with virtualenv, but I'll walk you through it here. The following instructions assume you already have the virtualenv Python module installed.

First, create a parent directory for the virtualenv and project:

    $ mkdir motion-popularity
    $ cd motion-popularity

Create the environment and activate it:

    $ virtualenv env
    $ source env/bin/activate

Now lets install the Motion codebase and everything it needs:

    (env)$ pip -E $VIRTUAL_ENV install --ignore-installed \
               -r http://github.com/bradchoate/motion-popularity/raw/master/requirements.txt

Next, we'll create a typepadproject Django project called "mymotion":

    (env)$ django-admin.py typepadproject mymotion --settings=motion.settings
    (env)$ cd mymotion

Run the Django "syncdb" command to initialize your database (configuring it first in the settings.py module, unless you're fine with the defaults which is to use SQLite):

    (env)$ python manage.py syncdb

(Note that if you do not have the library installed for your database, you may need to do that for the above command to succeed.)

Now, fire up your application using the Django "runserver" management command:

    (env)$ python manage.py runserver

This will start a web server running your project, at the address http://127.0.0.1:8000/

Once you access that URL, you will find that you still need to configure some settings. Click the link provided to get an application key. Once you have created an API key (choose to create a "Community" API key), select the information show in the "API Key:" portion of the page and copy that to your clipboard. Return to the http://127.0.0.1:8000/ address, and paste that into the text field, then click the "Save keys" button. Finally, click the "Continue" button and you should then see a mostly empty page for your new community. You should be able to sign into the group and start posting.

To enable the popularity app, you'll have to append it to the list of `INSTALLED_APPS` in the `settings.py` module for your Django project:

    (env)$ echo 'INSTALLED_APPS = INSTALLED_APPS + ("popularity",)' >> settings.py

Finally, lets also add these settings to enable the "popularity" app. You can put these in the `local_settings.py` module, since `POPULAR_USER` contains sensitive information (in practice we typically do not version control the `local_settings.py` file; at least not for a public project).

    POPULAR_USER           = ('user_id', 'key', 'secret')
    POPULAR_FAVORITE_COUNT = 5
    POPULAR_COMMENT_COUNT  = 10

You can experiment with the numbers here -- it will vary depending on how active your community is. As the community becomes more active, the higher these numbers generally need to be, otherwise you will get too many "popular" posts.

The `POPULAR_USER` setting is pretty important. Basically, it identifies a TypePad user that will be used to track the popular posts. You'll need to create a new TypePad user for this very purpose. It should not be your regular user account. Just sign out of typepad.com and then register as a new user. Once you've done this, join your Motion group with this new user. After doing that, we need to identify the OAuth token key and secret for that user. Once you've joined this user to the group, view the source of the home page and look for a tag like this:

(Note: the following ugly, involved process will be simplified in the near future because this information should be much easier to obtain.)

<pre><code>&lt;script type="text/javascript" language="javascript" src="https://www.typepad.com/secure/services/api/<strong>6pxxxxxxxxxxxxxxxx</strong>/session-sync?....<strong>session_sync_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</strong>...."&gt;&lt;/script&gt;</code></pre>

The `6pxxxxxxxxxxxxxxxx` part of the URL is the unique id for the logged-in TypePad user. The `session_sync_token` value in that URL is a value we'll use to look up the OAuth token key and secret for this user (I'm using SQLite in this example, but the SQL here will work for any database engine):

    (env)$ python manage.py dbshell
    sqlite> select key, secret from typepadapp_token
       ...> where session_sync_token='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';
    yyyyyyyyyyyyyyyy|zzzzzzzzzzzzzzzz

(Your results will vary.)

With the TypePad user id, key and secret, we can write the setting for `POPULAR_USER`:

    POPULAR_USER = ('6pxxxxxxxxxxxxxxxx', 'yyyyyyyyyyyyyyyy', 'zzzzzzzzzzzzzzzz')

At this point, we have done everything we need to do to enable the popularity app to track community posts that are collecting the favorite and comments desired to deem them as popular posts. The popularity app will automatically have our custom TypePad user favorite these posts and that activity can be viewed on that user's TypePad profile. You can even follow that TypePad user so those posts will show up on your TypePad dashboard. These favorites are also viewable within the group, on the user's own group profile page.

You'll need to edit your project's urlconf (`mymotion/urls.py`) to include the urls needed for the popularity app. The `urlpatterns` assignment should look something like this now:

    urlpatterns = patterns('',
        (r'^', include('typepadapp.urls')),
        (r'^', include('motion.urls')),
        (r'^popular', include('popularity.urls')),
    )

Once that's done, your Motion app should be all configured. Try creating some posts and have different members favorite them -- once a post has received enough favorites or comments (depending on your POPULAR\_FAVORITE\_COUNT and POPULAR\_COMMENT\_COUNT settings), you should start seeing those posts become favorited by the "popular" user.


[TypePad Motion]: http://www.typepad.com/go/motion/
[apikey]: http://www.typepad.com/account/access/developer
[contribute]: http://developer.typepad.com/motion/contribute-to-motion.html
