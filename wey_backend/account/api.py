from django.http import JsonResponse

from rest_framework.decorators import api_view, authentication_classes, permission_classes

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
        form.save()

        # Send verification email later!
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


@api_view(['POST'])
def send_friendship_request(request, pk):
    user = User.objects.get(pk=pk)

    # prevent multiple friendship requests

    check1 = FriendshipRequest.objects.filter(created_for=request.user).filter(created_by=user)
    check2 = FriendshipRequest.objects.filter(created_for=user).filter(created_by=request.user)

    if check1 or check2:
        return JsonResponse({'message': 'request already sent'})
    else:
        FriendshipRequest.objects.create(created_for=user, created_by=request.user)

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

