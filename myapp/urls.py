from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView

from . import views
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView, \
    PasswordResetDoneView

urlpatterns = [
                  path('signup/', views.SignupView.as_view(), name='signup'),
                  path('login/', views.LoginView.as_view(), name='login'),
                  path('', views.HomeView.as_view(), name='home'),
                  path('logout/', views.LogoutView.as_view(), name='logout'),
                  path('profile/', views.ProfileView.as_view(), name='profile'),
                  path('edit/<int:pk>/', views.EditView.as_view(), name='edit'),
                  path("delete-profile/<int:pk>/", views.DeleteProfileView.as_view(), name="delete_profile"),
                  path('changepassword/', views.ChangePasswordView.as_view(), name='changepassword'),
                  path("password_reset/", views.ResetPasswordView.as_view(), name="password_reset"),
                  path("password_reset_sent/", TemplateView.as_view(template_name='myapp/passwordresetdone.html')),
                  path("reset/<uidb64>/<token>/", views.ResetPasswordConfirmView.as_view(),
                       name="password_reset_confirm"),
                  path("add-post/", views.AddPostView.as_view(), name="add_post"),
                  path("edit-post/<int:pk>/", views.EditPostView.as_view(), name="edit_post"),
                  path("delete-post/<int:pk>/", views.DeletePostView.as_view(), name="delete_post"),
                  path("likepost/", views.LikeView.as_view(), name="like_post"),
                  path("createcomment/", views.CommentCreateView.as_view(), name="createcomment"),
                  path("commentdelete/", views.CommentDeleteView.as_view(), name="commentdelete"),
                  path("commentupdate/", views.CommentUpdateView.as_view(), name="commentupdate"),

                  path('search/', views.SearchUser.as_view(), name='search'),
                  path('search/users/', views.SearchAllUser.as_view(), name='search_all'),
                  path('profile/<int:pk>/', views.ProfileRetrieve.as_view(), name='profile_retrieve'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
