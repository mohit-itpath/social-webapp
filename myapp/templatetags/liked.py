from django import template
from myapp.models import LikesModel, CommentModel

register = template.Library()


@register.filter
def check(id, user):
    likes = LikesModel.objects.filter(post__id=id)
    if likes:
        for like in likes:
            if like.user == user:
                return True
    return False
