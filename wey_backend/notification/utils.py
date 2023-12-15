from .models import Notification

from post.models import Post
from account.models import FriendshipRequest


# create_notification(request, 'post_like', '73udf-8weer-238ye-3je9')
def create_notification(request, type_of_notification, post_id=None, friendshiprequest_id=None):
    created_for = None

    if type_of_notification == 'post_like':
        body = f'{request.user.name} liked your post!'
        post = Post.objects.get(pk=post_id)
        created_for = post.created_by
    elif type_of_notification == 'post_comment':
        body = f'{request.user.name} commented your post!'
        post = Post.objects.get(pk=post_id)
        created_for = post.created_by
    elif type_of_notification == 'new_friendrequest':
        body = f'{request.user.name} sent you a friend request!'
        friendshiprequest = FriendshipRequest.objects.get(pk=friendshiprequest_id)
        created_for = friendshiprequest.created_for
    elif type_of_notification == 'accepted_friendrequest':
        body = f'{request.user.name} accepted your friend request!'
        friendshiprequest = FriendshipRequest.objects.get(pk=friendshiprequest_id)
        created_for = friendshiprequest.created_for
    elif type_of_notification == 'rejected_friendrequest':
        body = f'{request.user.name} rejected your friend request!'
        friendshiprequest = FriendshipRequest.objects.get(pk=friendshiprequest_id)
        created_for = friendshiprequest.created_for

    notification = Notification.objects.create(
        body=body,
        created_by=request.user,
        type_of_notification=type_of_notification,
        post_id=post_id,
        created_for=created_for
    )

    return notification
