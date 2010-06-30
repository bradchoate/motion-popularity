from django.conf import settings
from django.core.urlresolvers import reverse

import typepad
from typepadapp.views.base import TypePadView
from typepadapp.models.users import User


class Popular(TypePadView):
    """Provides a view of posts that have been favorited by the designated "popular" user.

    """
    paginate_by = settings.EVENTS_PER_PAGE
    template_name = 'popularity/popular.html'

    def select_from_typepad(self, request, page=1, view='popular', *args, **kwargs):
        self.paginate_template = reverse('popular') + '/page/%d'
        user = User.get_by_url_id(settings.POPULAR_USER[0])
        self.context['favorites'] = user.favorites.filter(
            start_index=self.offset, max_results=self.limit)
        self.context['following'] = user.following(group=request.group)

    def get(self, request, page=1, view='popular', *args, **kwargs):
        # we have to re-swizzle the stream returned as favorites and produce and object_list
        entries = []
        typepad.client.batch_request()
        for f in self.context['favorites']:
            entries.append({
                'actor': f.in_reply_to.author,
                'object': typepad.Asset.get_by_url_id(f.in_reply_to.url_id),
                'verb': 'NewAsset',
                'url_id': 'foo',
                'published': f.published,
            })
        typepad.client.complete_batch()
        self.context.update({'favorites': entries})
        return super(Popular, self).get(request, page, view, *args, **kwargs)
