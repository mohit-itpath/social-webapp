from django.contrib.auth import authenticate
from django.db.models import Count, Q, Prefetch
from rest_framework.response import Response
from rest_framework.views import APIView
from .custompermission import MyPermission
from .serializers import CustomUserSerializer, PostSerializer, CommentSerializer, \
    ChangePasswordSerializer, SendResetLinkSerializer, PasswordResetConfirmSerializer, ProfileSerializer
from rest_framework.generics import CreateAPIView
from myapp.models import CustomUser, PostModel, LikesModel, CommentModel
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken


# Create your views here.
class CreateView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def validateEmail(email):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


class LoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        response = {}
        if email and password:
            if validateEmail(email):
                user = authenticate(request, email=email, password=password)
                if user:
                    return Response({'data': get_tokens_for_user(user)}, status=status.HTTP_200_OK)
                return Response({'errors': 'Credential is not valid'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'errors': {'Email': 'This Field not Valid'}}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            response["email"] = ["This field is required"]
        if not password:
            response["password"] = ["This field is required"]
        return Response({"errors": response})


class ProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        user_serializer = ProfileSerializer(user)
        posts = PostModel.objects.filter(user_id=request.user.id).order_by('-id').annotate(
            like=Count('likesmodel')).values()
        for post in posts:
            post['comments'] = CommentModel.objects.filter(post_id=post['id']).values()
        context = {
            'user': user_serializer.data,
            'posts': posts
        }
        return Response({'data': context}, status=status.HTTP_200_OK)

    def put(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        user_serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({'message': 'Updated Successfully'}, status=status.HTTP_200_OK)
        return Response({'errors': user_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        user.delete()
        return Response({'message': 'Delete Successfully'}, status=status.HTTP_200_OK)


class UserChangePassword(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        change_password_serializer = ChangePasswordSerializer(data=request.data, context={'user': request.user})
        if change_password_serializer.is_valid(raise_exception=True):
            return Response({'msg': 'Change Password Successfully.'}, status=status.HTTP_200_OK)
        return Response({'errors': change_password_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SendResetLinkView(APIView):
    def post(self, request):
        restlinkserailizer = SendResetLinkSerializer(data=request.data)
        if restlinkserailizer.is_valid():
            return Response({'msg': 'Reset Link is Sent To Your Email.'}, status=status.HTTP_200_OK)
        return Response({'errors': restlinkserailizer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    def post(self, request, uid, token):
        resetserializer = PasswordResetConfirmSerializer(data=request.data, context={'uid': uid, 'token': token})
        if resetserializer.is_valid():
            return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)
        return Response({'errors': resetserializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PostAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.data['user'] = request.user.pk
        post_serializer = PostSerializer(data=request.data)
        if post_serializer.is_valid():
            post_serializer.save()
            return Response({'data': post_serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'data': post_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UpdateDeletePost(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [MyPermission]

    def delete(self, request, pk):
        post = PostModel.objects.filter(pk=pk).first()
        if post:
            self.check_object_permissions(request, post)
            post.delete()
            return Response({'msg': 'Deleted Successfully'}, status=status.HTTP_200_OK)
        return Response({"msg": "No Post Found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        post = PostModel.objects.filter(pk=pk).first()
        if post:
            self.check_object_permissions(request, post)
            post_serializer = PostSerializer(post, data=request.data, partial=True)
            if post_serializer.is_valid():
                post_serializer.save()
                return Response({'msg': 'updated Successfully'}, status=status.HTTP_200_OK)
            return Response({'errors': post_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"msg": "No Post Found"}, status=status.HTTP_404_NOT_FOUND)


class CommentAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        post_id = request.data.get('post_id')
        comment = request.data.get('comment_val')
        response = {}
        if post_id and comment:
            post_obj = PostModel.objects.filter(id=post_id).first()
            if post_obj:
                new_comment = CommentModel.objects.create(post=post_obj, user_id=request.user.id, comment=comment)
                context = {
                    "comment_id": new_comment.id,
                    "comment_content": new_comment.comment,
                    "comment_created_at": new_comment.created_at
                }
                return Response({"data": context})
            response["post_id"] = ["Post Is Not Found"]
            return Response({'errors': response})
        if not post_id:
            response["post_id"] = ["This field is required"]
        if not comment:
            response["comment"] = ["This field is required"]
        return Response({"errors": response})


class CommentUpdateDeleteAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [MyPermission]

    def put(self, request, comm_pk):
        comment = CommentModel.objects.filter(id=comm_pk).first()
        if comment:
            self.check_object_permissions(request, comment)
            comm_serializer = CommentSerializer(comment, data=request.data, partial=True)
            if comm_serializer.is_valid():
                comm_serializer.save()
                return Response({'msg': 'updated Successfully'}, status=status.HTTP_200_OK)
            return Response({'errors': comm_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'errors': 'No Comment Found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, comm_pk):
        comment = CommentModel.objects.filter(id=comm_pk).first()
        if comment:
            self.check_object_permissions(request, comment)
            comment.delete()
            return Response({'msg': 'deleted successfully'}, status=status.HTTP_200_OK)
        return Response({'errors': 'No Comment Found'}, status=status.HTTP_404_NOT_FOUND)


class LikeAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        post_id = request.data.get('post_id')
        if post_id:
            post = PostModel.objects.filter(id=post_id).first()
            if post:
                like = LikesModel.objects.filter(post__id=post_id, user=request.user).first()
                if like:
                    like.delete()
                    return Response({'msg': 'dislike successfully'}, status=status.HTTP_200_OK)
                like = LikesModel(post=post, user=request.user)
                like.save()
                return Response({'msg': 'liked Successfully'}, status=status.HTTP_200_OK)
            return Response({'errors': 'Post is Not Found'}, status=status.HTTP_404_NOT_FOUND)
        error = {}
        if post_id is None:
            error["post_id"] = "This is Field Required"
        else:
            error["post_id"] = "This is Field Can't Be Empty"
        return Response({'errors': error})


class HomeAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = PostModel.objects.all().values("id", "caption", "post_image", "created_at", "updated_at", "user_id",
                                               "user__first_name", "user__last_name", "user__email", "user__image")
        user = CustomUser.objects.filter(id=request.user.id).values('id', 'first_name', 'last_name', 'email',
                                                                    'image').first()
        for post in posts:
            post['comments'] = CommentModel.objects.filter(post_id=post['id']).values("id", "user__first_name",
                                                                                      "user_id", "user__last_name",
                                                                                      "user__email", "user__image",
                                                                                      "post_id", "comment",
                                                                                      "created_at", "updated_at")
            post['like'] = LikesModel.objects.filter(post_id=post['id']).count()
            context = {
                'posts': posts,
                'user': user
            }
        return Response({'data': context}, status=status.HTTP_200_OK)


class SearchUserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get('q')
        if query:
            users = CustomUser.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__istartswith=query))[
                    :4].values(
                'id', 'first_name', 'last_name', 'image')
            if users:
                payload = [user for user in users]
                if payload:
                    payload.append({'showAll': True, 'input': query})
                return Response({'data': payload}, status=status.HTTP_200_OK)
            return Response({'msg': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'data': []}, status=status.HTTP_200_OK)


class SearchAllUserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get('q')
        users = CustomUser.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__istartswith=query))
        if users:
            context = {
                'users': users
            }
            return Response({'data': context}, status=status.HTTP_200_OK)
        return Response({'msg': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)


class ProfileRetrieveAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = CustomUser.objects.filter(id=pk).first()
        if user:
            user_serializer = ProfileSerializer(user)
            posts = PostModel.objects.filter(user_id=user.id).order_by('-id').annotate(
                like=Count('likesmodel')).values()
            for post in posts:
                post['comments'] = CommentModel.objects.filter(post_id=post['id']).values()
            context = {
                'user': user_serializer.data,
                'posts': posts
            }
            return Response({'data': context}, status=status.HTTP_200_OK)
        return Response({'msg': 'Not Found'}, status=status.HTTP_404_NOT_FOUND)
