from oauth import oauth
from urlparse import urlparse
import typepad
from django.conf import settings
from typepadapp import models, signals


# settings:
#     POPULAR_FAVORITE_COUNT = 5
#     POPULAR_COMMENT_COUNT = 10
#     POPULAR_USER = ('user_url_id', 'key', 'secret')

def utility_user(user_info):
    user_id, key, secret = user_info
    user = typepad.User.get_by_url_id(user_id)

    typepad.client.consumer = (settings.OAUTH_CONSUMER_KEY, settings.OAUTH_CONSUMER_SECRET)
    typepad.client.token = (key, secret)

    return user


def favorite(user, asset, group):
    token = typepad.client.token
    user = utility_user(user)
    fav = models.Favorite()
    fav.in_reply_to = asset.asset_ref
    user.favorites.post(fav)
    signals.favorite_created.send(sender=favorite, instance=fav, parent=asset,
        group=group)
    typepad.client.token = token


def unfavorite(user, asset, group):
    token = typepad.client.token
    user = utility_user(user)
    fav = models.Favorite.get_by_user_asset(user.url_id, asset.url_id)
    try:
        fav.delete()
        signals.favorite_deleted.send(sender=favorite, instance=fav,
            parent=asset, group=group)
    except:
        pass
    typepad.client.token = token


if hasattr(settings, 'POPULAR_FAVORITE_COUNT'):
    def favorite_created(sender, instance, group=None, parent=None, **kwargs):
        # we don't care about our own favoriting
        if sender == favorite: return

        if parent.favorite_count + 1 == settings.POPULAR_FAVORITE_COUNT:
            favorite(settings.POPULAR_USER, parent, group)
        else:
            # do we follow the user that made this favorite? if so, lets favorite it!
            typepad.client.batch_request()
            rels = typepad.User.get_by_url_id(settings.POPULAR_USER[0]).relationships.filter(
                by_user=instance.author.url_id)
            typepad.client.complete_batch()
            if rels and rels.total_results > 0 and \
                rels.entries[0].target.url_id == instance.author.url_id:
                favorite(settings.POPULAR_USER, parent, group)

    def favorite_deleted(sender, instance, group=None, parent=None, **kwargs):
        # we don't care about our own favoriting
        if sender == unfavorite: return

        if parent.favorite_count == settings.POPULAR_FAVORITE_COUNT:
            unfavorite(settings.POPULAR_USER, parent, group)

    signals.favorite_created.connect(favorite_created)
    signals.favorite_deleted.connect(favorite_deleted)


if hasattr(settings, 'POPULAR_COMMENT_COUNT'):
    def asset_created(sender, instance, group=None, parent=None, **kwargs):
        if not isinstance(instance, typepad.Comment):
            return
        if parent.comment_count + 1 == settings.POPULAR_COMMENT_COUNT:
            favorite(settings.POPULAR_USER, parent)

    def asset_deleted(sender, instance, group=None, parent=None, **kwargs):
        if not isinstance(instance, typepad.Comment):
            return
        if parent.comment_count == settings.POPULAR_COMMENT_COUNT:
            favorite(settings.POPULAR_USER, parent)

    signals.asset_created.connect(asset_created)
    signals.asset_deleted.connect(asset_deleted)
