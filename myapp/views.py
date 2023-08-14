from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.base import View
from django.views.generic.edit import CreateView, UpdateView, FormView
from .forms import SignupForm, LoginForm, EditForm, AddPostForm
from .models import CustomUser, PostModel, LikesModel, CommentModel
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.http.response import JsonResponse, HttpResponse, Http404


# Create your views here.
class SignupView(SuccessMessageMixin, CreateView):
    form_class = SignupForm
    template_name = 'myapp/signup.html'
    model = CustomUser
    success_url = reverse_lazy('login')
    success_message = 'Signup Successfully'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('profile'))
        return super().get(request, *args, **kwargs)


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('profile'))
        form = LoginForm()
        return render(request, 'myapp/login.html', {'form': form})

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login Successfully ')
            return redirect(reverse_lazy('home'))
        else:
            messages.error(request, 'Email or Password Incorrect !')
        return redirect(reverse_lazy('login'))


class HomeView(LoginRequiredMixin, ListView):
    template_name = 'myapp/home.html'
    model = PostModel
    context_object_name = 'posts'
    paginate_by = 3
    paginate_orphans = 0

    def get_queryset(self):
        posts = PostModel.objects.all().order_by('-id').annotate(like=Count('likesmodel')).values()
        for post in posts:
            post['comments'] = CommentModel.objects.filter(post_id=post['id'])
            post['user'] = CustomUser.objects.get(pk=post['user_id'])
        return posts

    def get_context_data(self, *args, object_list=None, **kwargs):
        try:
            return super().get_context_data()
        except Http404:
            self.kwargs['page'] = 1
            return super().get_context_data()


class LogoutView(LoginRequiredMixin, View):

    def get(self, request):
        logout(request)
        messages.success(request, 'Logout Successfully ')
        return redirect(reverse_lazy('login'))


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        posts = PostModel.objects.filter(user__id=request.user.id).order_by('-id').annotate(
            like=Count('likesmodel')).values()
        for post in posts:
            post['comments'] = CommentModel.objects.filter(post_id=post['id'])
            post['user'] = CustomUser.objects.get(pk=post['user_id'])
        context = {
            'user': user,
            'posts': posts
        }
        return render(request, 'myapp/profile.html', context)


class EditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = EditForm
    template_name = 'myapp/edit.html'
    success_url = reverse_lazy('profile')
    success_message = 'Edit Successfully'

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk', None) != request.user.pk:
            return redirect(reverse_lazy('edit', kwargs={'pk': request.user.pk}))
        return super().get(request, args, kwargs)


class ChangePasswordView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    model = CustomUser
    template_name = 'myapp/change_password.html'
    success_url = reverse_lazy('login')
    success_message = 'Password is updated !'


class ResetPasswordView(PasswordResetView):
    template_name = 'myapp/passwordreset.html'
    success_url = reverse_lazy('login')
    email_template_name = 'myapp/password_reset_email.html'
    subject_template_name = 'myapp/password_reset_subject.txt'

    def form_valid(self, form):
        messages.success(self.request, 'Password Reset Link Sent To Email')
        return super().form_valid(form)


class ResetPasswordConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'myapp/passwordresetconfirm.html'
    success_url = reverse_lazy('login')
    success_message = 'Password Reset Successfully'


class AddPostView(LoginRequiredMixin, FormView):
    template_name = 'myapp/add_post.html'
    form_class = AddPostForm
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        caption = form.cleaned_data['caption']
        post_image = form.cleaned_data['post_image']
        post = PostModel.objects.create(caption=caption, post_image=post_image, user=self.request.user)
        messages.success(self.request, 'Post Added Successfully')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Something Went Wrong')
        return super().form_invalid()


class EditPostView(LoginRequiredMixin, UpdateView):
    model = PostModel
    fields = ['caption', 'post_image']
    template_name = 'myapp/editpost.html'
    success_url = reverse_lazy('profile')


class DeletePostView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        PostModel.objects.get(pk=kwargs['pk']).delete()
        return redirect(reverse_lazy('profile'))


class DeleteProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        CustomUser.objects.get(pk=kwargs['pk']).delete()
        messages.success(request, 'Profile Deleted Successfully')
        return redirect(reverse_lazy('login'))


class LikeView(LoginRequiredMixin, View):
    def post(self, request):
        post_id = request.POST['post_id']
        post = PostModel.objects.get(id=post_id)
        like = LikesModel.objects.filter(post__id=post_id, user=request.user).first()
        if like:
            like.delete()
            return HttpResponse(202)
        like = LikesModel(post=post, user=request.user)
        like.save()
        return HttpResponse(201)


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request):
        comment_id = request.POST.get('comment_id')
        post_id = request.POST['post_id']
        comment = request.POST['comment_val']
        if comment:
            if comment_id:
                new_comment = CommentModel.objects.get(id=comment_id)
                new_comment.comment = comment
                new_comment.save()
            else:
                new_comment = CommentModel.objects.create(post_id=post_id, user=request.user, comment=comment)
            context = {
                "comment_id": new_comment.id,
                "comment_content": new_comment.comment,
                "comment_created_at": new_comment.created_at
            }
            return JsonResponse(context, safe=True)
        return JsonResponse({"errors": "This is Field Required"})


class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        comment_id = request.POST['comment_id']
        comment = CommentModel.objects.get(id=comment_id)
        comment.delete()
        return HttpResponse(200)


class CommentUpdateView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        comment_id = request.GET['comment_id']
        comment_obj = CommentModel.objects.get(id=comment_id)
        context = {
            "comment_id": comment_id,
            "comment_content": comment_obj.comment,
            "post_id": comment_obj.post.id
        }
        return JsonResponse(context, safe=True)


class SearchUser(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q')
        if query:
            users = CustomUser.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__istartswith=query))[
                    :4].values(
                'id', 'first_name', 'last_name', 'image')

            payload = [user for user in users]
            if payload:
                payload.append({'showAll': True, 'input': query})
            return JsonResponse({'status': 200, 'data': payload})
        return JsonResponse({'status': 200, 'data': []})


class SearchAllUser(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q')
        users = CustomUser.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__istartswith=query))
        context = {
            'users': users
        }
        return render(request, 'myapp/searchalluser.html', context)


class ProfileRetrieve(LoginRequiredMixin, DetailView):
    model = CustomUser
    context_object_name = 'user'
    template_name = 'myapp/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = CustomUser.objects.get(id=context['user'].id)
        posts = PostModel.objects.filter(user__id=user.id).order_by('-id').annotate(
            like=Count('likesmodel')).values()
        for post in posts:
            post['comments'] = CommentModel.objects.filter(post_id=post['id'])
            post['user'] = CustomUser.objects.get(pk=post['user_id'])
        context = {
            'user': user,
            'posts': posts
        }
        return context
