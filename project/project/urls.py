from django.contrib import admin
from django.urls import path
from app.views import HomePageMedia,RegisterView,LoginView,LogOutView,ResetPasswordView,MediaCatalog,ViewDetails,ProfileHandler,DeleteReview,BaseSearchView
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',HomePageMedia.as_view(),name='home'),
    path('faq', TemplateView.as_view(template_name='faq.html'), name='faq'),
    path('about', TemplateView.as_view(template_name='about.html'),name='about'),
    path('catalog',MediaCatalog.as_view(),name='catalog'),
    
    path('catalog/<str:search_data>',MediaCatalog.as_view(),name='search_catalog'),
    
    path('<int:media_pk>',ViewDetails.as_view(),name='details'),
    path('delete-reviews/<int:review_id>',DeleteReview,name='del-review'),
    path('search',BaseSearchView,name='base-search'),
    
    # регистрация
    path('register',RegisterView.as_view(),name='register'),
    path('register/<int:user_pk>/<str:token>',RegisterView.as_view(),name='register-confirm'),
    
    # авторизация, выход
    path('login',LoginView.as_view(),name='login'),
    path('logout', LogOutView.as_view(), name='logout'),
    path('profile/<int:user_pk>',ProfileHandler.as_view(),name='profile'),
    
    # изменить профиль, восстановление пароля
    path('reset-pass',ResetPasswordView.as_view(),name='reset-pass'),
    path('reset-pass/<int:user_pk>/<str:token>',ResetPasswordView.as_view(),name='reset-pass-confirm'),

]

urlpatterns += static(settings.STATIC_URL,document_root=settings.STATICFILES_DIRS[0])