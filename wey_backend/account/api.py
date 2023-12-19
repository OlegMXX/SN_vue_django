from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.http import JsonResponse

from rest_framework.decorators import api_view, authentication_classes, permission_classes

from notification.utils import create_notification

from .forms import SignupForm, ProfileForm
from .models import FriendshipRequest, User
from .serializers import UserSerializer, FriendshipRequestSerializer



@api_view(['GET'])
def me(request):
    try:
        return JsonResponse({
            'id': request.user.id,
            'name': request.user.name,
            'email': request.user.email,
            'avatar': request.user.get_avatar()
        })
    except Exception as e:
        print(e)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def signup(request):
    data = request.data
    message = 'success'

    form = SignupForm({
        'email': data.get('email'),
        'name': data.get('name'),
        'password1': data.get('password1'),
        'password2': data.get('password2'),
    })

    if form.is_valid():
        user = form.save()
        user.is_active = False
        user.save()

        url = f'{settings.WEBSITE_URL}/activateemail/?email={user.email}&id={user.id}'

        send_mail(
            "Please verify your email",
            f"Here is the link to activate your account: {url}",
            "noreply@vuerules.com",
            [user.email],
            fail_silently=False,
        )

    else:
        message = form.errors.as_json()

    return JsonResponse({'message': message}, safe=False)

@api_view(['GET'])
def friends(request, pk):
    user = User.objects.get(pk=pk)
    requests = []

    if user == request.user:
        requests = FriendshipRequest.objects.filter(created_for=request.user, status=FriendshipRequest.SENT)

    friends = user.friends.all()

    return JsonResponse({
        'user': UserSerializer(user).data,
        'friends': UserSerializer(friends, many=True).data,
        'requests': FriendshipRequestSerializer(requests, many=True).data
    }, safe=False)


@api_view(['GET'])
def my_friendsdhip_suggestions(request):
    serializer = UserSerializer(request.user.people_you_may_know.all(), many=True)

    return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
def send_friendship_request(request, pk):
    user = User.objects.get(pk=pk)

    # prevent multiple friendship requests

    check1 = FriendshipRequest.objects.filter(created_for=request.user).filter(created_by=user)
    check2 = FriendshipRequest.objects.filter(created_for=user).filter(created_by=request.user)

    if check1 or check2:
        return JsonResponse({'message': 'request already sent'})
    else:
        friendsrequest = FriendshipRequest.objects.create(created_for=user, created_by=request.user)
        notifiaction = create_notification(request, 'newfriendrequest', friendshiprequest_id=friendsrequest.id)

        return JsonResponse({'message': 'friendship request created'})


@api_view(['POST'])
def handle_request(request, pk, status):
    user = User.objects.get(pk=pk)
    friendship_request = FriendshipRequest.objects.filter(created_for=request.user).get(created_by=user)
    friendship_request.status = status
    friendship_request.save()

    user.friends.add(request.user)
    user.friends_count += 1
    user.save()

    request_user = request.user
    request_user.friends_count += 1
    request_user.save()

    notifiaction = create_notification(request, 'accepted_friendrequest', friendshiprequest_id=friendship_request.id)

    return JsonResponse({'message': 'friendship request updated'})


@api_view(['POST'])
def editprofile(request):
    user = request.user
    email = request.data.get('email')

    if User.objects.exclude(id=user.id).filter(email=email).exists():
        return JsonResponse({'message': 'email already exists'})
    else:
        form = ProfileForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()

        serializer = UserSerializer(user)

        return JsonResponse({'message': 'information updated', 'user': serializer.data})


@api_view(['POST'])
def editpassword(request):
    user = request.user

    form = PasswordChangeForm(data=request.POST, user=user)
    if form.is_valid():
        form.save()

        return JsonResponse({'message': 'success'})
    else:
        return JsonResponse({'message': form.errors.as_json()}, safe=False)

