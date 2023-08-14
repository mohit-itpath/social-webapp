from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('', views.HomeAPIView.as_view(), name="home"),
    path('users/signup/', views.CreateView.as_view(), name="signup"),
    path('users/login/', views.LoginAPIView.as_view(), name="login"),
    path('users/profile/', views.ProfileAPIView.as_view(), name="profile"),
    path('users/changepassword/', views.UserChangePassword.as_view(), name='user_change_password'),
    path('users/password_reset_sent/', views.SendResetLinkView.as_view(), name='password_reset_sent'),
    path('users/reset/<uid>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('posts/', views.PostAPIView.as_view(), name="add_post"),
    path('posts/<int:pk>/', views.UpdateDeletePost.as_view(), name='Update_Delete_post'),
    path('comments/', views.CommentAPIView.as_view(), name="add_comment"),
    path('comments/<int:comm_pk>/', views.CommentUpdateDeleteAPIView.as_view(), name="Update_Delete_comment"),
    path('likes/', views.LikeAPIView.as_view(), name="likes"),
    path('search/', views.SearchUserAPIView.as_view(), name='search'),
    path('search/users/', views.SearchAllUserAPIView.as_view(), name='search_all'),
    path('users/profile/<int:pk>/', views.ProfileRetrieveAPIView.as_view(), name='profile_retrieve'),
]
