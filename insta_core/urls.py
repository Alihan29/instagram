"""
URL configuration for insta_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from users.views import SignUpView, MakeRegistrationView,ReelsView, HomeView, ProfileView, LoginView, MakeLoginView, AddPublicationView, LikeManager, DeleteLike, Subscribe, Unsubscribe, AddComment, OtherProfileView, ChangeAvatar

urlpatterns = [
    path('admin/', admin.site.urls),
    # GET запросы
    path('',  HomeView.as_view(), name="home"),
    path('sign-up/', SignUpView.as_view(), name="create"),
    path('reels/', ReelsView.as_view(), name="reels"),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('login/', LoginView.as_view(), name="login"),
    path('other-profile/<int:user_id>/', OtherProfileView.as_view(), name="other_profile"),
    # POST запросы
    path('make-login/', MakeLoginView.as_view(), name="mk-log"),
    path('make-registration/', MakeRegistrationView.as_view(), name='mk-rg'),
    path('add-post/', AddPublicationView.as_view(), name='add-post'),
    path('like/', LikeManager.as_view(), name='like'),
    path('delete-like/', DeleteLike.as_view(), name='delete-like'),
    path('subscribe', Unsubscribe.as_view(), name="unsubscribe"),
    path('Unsubscribe', Subscribe.as_view(), name="subscribe"),
    path('add_comment', AddComment.as_view(), name="add-comment"),
    path('change-avatar', ChangeAvatar.as_view(), name="change-avatar")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
