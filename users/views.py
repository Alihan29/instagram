from typing import Any
from .models import User, Publication, LikesPublication, Comment, Subscription
from django.contrib.auth.hashers import check_password
from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.urls import reverse

# Create your views here.
class HomeView(TemplateView):
    template_name = "home.html"

    def get(self, request, *args, **kwargs):
        curent_user = request.user
        if not curent_user.is_authenticated:
            # Перенаправляем анонимного пользователя на страницу входа
            return redirect(reverse('create'))  # Замените 'sign-in' на актуальное имя вашего URL

        # Если пользователь авторизован, продолжаем выполнение
        publications = Publication.objects.all().order_by('-date')  # Сортировка по полю date в порядке убывания
        publication_list = []
        for pub in publications:
            liked_by_current_user = LikesPublication.objects.filter(publication=pub, user=curent_user).exists()
            pub.liked_by_current_user = liked_by_current_user
            publication_list.append(pub)

        # Формируем контекст для шаблона
        context = {
            "publications": publication_list,
            "user": curent_user,
            "other_users": User.objects.exclude(Q(subscribers__subscriber=curent_user) | Q(id=curent_user.id)),
            "subscribes": User.objects.filter(subscribers__subscriber=curent_user).exclude(id=curent_user.id),
        }

        return self.render_to_response(context)



class SignUpView(TemplateView):
    template_name = "sign_up.html"

class ReelsView(TemplateView):
    template_name = "reels.html"

class ProfileView(TemplateView):
    template_name = "profile.html"

    def get_context_data(self, **kwargsy):
        curent_user = self.request.user

        context = {
            'publications': curent_user.user_publications.all()
        }

        return context

class LoginView(TemplateView):
    template_name = "login.html"

class OtherProfileView(TemplateView):
    template_name = "other_profile.html"

    def get(self, request, *args, **kwargs):
        id = kwargs['user_id']
        curent_user = request.user
        user = User.objects.get(id=id)
        publications = user.user_publications.all()
        followers = user.subscribers.all()
        following = user.subscriptions.all()

        if user == self.request.user:
            return redirect("profile")
        
        is_followed = False

        if Subscription.objects.filter(subscriber=curent_user, subscribed_to=user).exists():
            is_followed = True

        context = {
            'is_followed': is_followed,
            'the_user': user,
            'the_user_publications': publications,
            'the_user_posts_count': publications.count(),
            'the_user_followers_count': followers.count(),
            'the_user_following_count': following.count(),
        }

        return render(request, self.template_name, context)

class MakeLoginView(View):
    def post(self, request, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, template_name='sign_up.html', context={'error': 'User not found'})

        if check_password(password, user.password):
            login(self.request, user)
            return redirect('home')
        
        return render(request, template_name='sign_up.html', context={'error': 'Incorrect password'})

class MakeRegistrationView(View):
    def post(self, request, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, template_name='sign_up.html', context={'error': 'Username already taken'})

        user = User.objects.create_user(username=username, password=password)
        login(request, user)

        return redirect('home')


class AddPublicationView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, template_name='sign_up.html', context={'error': 'You must be logged in'})

        current_user = request.user
        title = request.POST.get('text')
        image = request.FILES.get('image')

        if not title or not image:
            return render(request, template_name='home.html', context={'error': 'Title and image are required'})

        Publication.objects.create(image=image, title=title, author=current_user)
        return redirect('home')


class LikeManager(View):
    def post(self, request, *args, **kwargs):
        try:
            publication = Publication.objects.get(id=request.POST['publication_id'])
        except Publication.DoesNotExist:
            return redirect("home")
        
        current_user = request.user
        if not current_user.is_authenticated:
            return redirect("create")
        
        # Check if like already exists
        if LikesPublication.objects.filter(user=current_user, publication=publication).exists():
            return redirect("home")
        
        LikesPublication.objects.create(user=current_user, publication=publication)
        publication.likes_count += 1
        publication.save()

        return redirect('home')

        

class DeleteLike(View):
    def post(self, request, *args, **kwargs):
        try:
            publication = Publication.objects.get(id=request.POST['publication_id'])
        except Publication.DoesNotExist:
            return redirect('home')
        
        curent_user = request.user

        if LikesPublication.objects.filter(publication=publication, user=curent_user).exists():
            LikesPublication.objects.filter(publication=publication, user=curent_user).delete()
            publication.likes_count -= 1
            publication.save()
        
        return redirect('home')

    
class Subscribe(View):
    def post(self, request, *args, **kwargs):
        subscriber = request.user
        user_id = request.POST.get("user_id")
        subscribed_to = User.objects.get(id=user_id)

        Subscription.objects.create(subscriber=subscriber, subscribed_to=subscribed_to)
        return redirect("other_profile",  user_id=user_id)
    
class Unsubscribe(View):
    def post(self, request, *args, **kwargs):
        subscriber = request.user
        user_id = request.POST.get("user_id")
        subscribed_to = User.objects.get(id=user_id)
        subscription = Subscription.objects.filter(subscriber=subscriber, subscribed_to=subscribed_to).first()
        
        if subscription:
            subscription.delete()

        return redirect("other_profile",  user_id=user_id)

class AddComment(View):
    def post(self, request, *args, **kwargs):
        current_user = request.user
        publication_id = request.POST.get('publication_id')

        try:
            publication = Publication.objects.get(id=publication_id)
        except Publication.DoesNotExist:
            return redirect('home')

        text = request.POST.get('comment_text')

        if not text:
            return redirect('home')

        Comment.objects.create(user=current_user, publication=publication, text=text)
        return redirect('home')

    
class ChangeAvatar(View):
    def post(self, request, *args, **kwargs):
        current_user = request.user
        avatar = request.FILES.get("avatar")

        if avatar:
            current_user.avatar = avatar
            current_user.save()
        else:
            return redirect('profile')

        return redirect('profile')
