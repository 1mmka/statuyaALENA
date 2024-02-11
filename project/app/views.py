from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate,login,logout
from django.http import Http404, HttpResponse, HttpResponseRedirect
from app.models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,ArchiveIndexView,View,DetailView,UpdateView
from app.models import Media,Genre,Review,Actor,Director
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from app.forms import UserProfileForm,PasswordChangeForm


@method_decorator(require_http_methods(["GET", "POST"]), name="dispatch")
class RegisterView(View):
    """
    
    Представление для регистрации пользователей.
    
    GET: 
    Если не переданы данные о пользователе и токене, отображает страницу регистрации.
    Если переданы данные, то активирует пользователя, проверяя токен.
    
    POST:
    При получении данных формы выполняет валидацию паролей и проверку email.
    В случае успешной регистрации, отправляет подтвеждение на указанный email.
    
    """
    
    def get(self,request,user_pk=None,token=None): 
        """
        Обработчик GET-запроса для регистрации.
        
        Args:
        request: Объект запроса Django.
        user_pk: Уникальный идентификатор пользователя.
        token: Токен для активации учетной записи пользователя.
        
        Returns:
        HTTP ответ с рендерингом страницы регистрации или редиректом на страницу входа.
        
        Raises:
        Http404: Если произошла ошибка при проверке пользователя и его токена.
        """
        
        if user_pk is None and token is None:
            return render(request,'register.html')
        
        user = get_object_or_404(CustomUser, pk = user_pk)
        
        try:
            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return HttpResponseRedirect(reverse('login'))
        except Http404:
            return render(request,'404.html')
    
    
    def post(self,request):
        """
        Обработчик POST запроса для регистрации
        
        Args:
        request: Объект запроса Django.
        
        Returns:
        HTTP ответы с ошибками или успешном создании учетной записи.
        """
        
        if request.POST['password'] != request.POST['password2']:
            return render(request,'400.html')

        hashed_password = make_password(password = request.POST['password'])
        
        check_email = request.POST['email']
        if CustomUser.objects.filter(email = check_email).exists():
            return render(request,'409.html')
        
        user = CustomUser.objects.create(
                    username=request.POST['username'],
                    email=check_email,
                    password=hashed_password,
                )
        user.is_active = False
        user.save()
        
        token = default_token_generator.make_token(user)
        verify_url = self.request.build_absolute_uri(f'/register/{user.pk}/{token}')
        
        message = """hi {client} перейдите по этой ссылке: {url}""".format(client = user.username, url = verify_url)
        subject = 'Подтверждение регистрации'
        from_email = 'randomusertestrandomuser@gmail.com'
        recipient_list = [user.email]
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
        )
        
        return render(request,'201.html')


class LoginView(View):
    """
    Представление для входа в систему.
    
    GET:
    Отображает страницу для входа.
    
    POST:
    Получает данные с формы входа, выполняет аутентификацию пользователя,
    и, если успешно, авторизует пользователя и перенаправляет на домашнюю страницу.
    В случае неудачной аутентификации отображает страницу с ошибкой 400
    """
    
    def get(self,request):
        """
        Обработчик GET-запроса для отображения страницы входа.

        Args:
        request: Объект запроса Django.
        
        Returns:
        HTTP ответ с рендерингом страницы для входа.
        """
        return render(request=request,template_name='login.html')
    
    def post(self,request):
        """
        Обработчик POST-запроса для аутентификации и авторизации пользователя.
        
        Args:
        request: Объект запроса Django.
        
        Returns:
        HTTP ответ с редиректом на домашнюю страницу в случае успешной аутентификации пользователя.
        Или отображает страницу с ошибкой 400 при неудачной аутентификации.
        """
        
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        
        user = authenticate(username = username, password = password)
        if user is not None:
            login(request = request, user = user)
            return HttpResponseRedirect(reverse('home'))
        else:
            return render(request,'400.html')


class LogOutView(View,LoginRequiredMixin):
    """
    Представление для выхода пользователя из системы.
    
    GET:
    Выходит из системы и перенаправляет на домашнюю страницу.
    Требует авторизованного пользователя для использования функционала.
    """
    
    def get(self,request):
        """
        Обработчик GET-запроса для выхода пользователя из системы.
        
        Args:
        request: Объект запроса Django.
        
        Returns:
        HTTP-ответ с перенаправлением на домашнюю страницу.
        """
        logout(request = request)
        return HttpResponseRedirect(reverse('home'))


@method_decorator(require_http_methods(["GET", "POST"]), name="dispatch")
class ResetPasswordView(View):
    """
    Представление для сброса и изменение пароля.
    
    GET:
    Проверяет на наличие идентификатора и токена пользователя и рендерит страницу для сброса пароля.
    При успешной проверке данных рендерится страница для ввода нового пароля, иначе вызывается ошибка.
    
    POST:
    Определение логики по двум условиям: проверка и отправка сообщения пользователю по указанному email.
    Изменение пароля при успешной валидации.
    """
    
    def get(self,request,user_pk=None,token=None):
        """
        Обработчик GET-запроса для проверки и рендеринга страница сброса пароля.
        
        Args:
        request: Объект запроса в Django.
        user_pk: Уникальный идентификатор пользователя.
        token: Уникальный токен пользователя
        
        Returns:
        Рендеринг страницы сброса пароля при первом запросе GET.
        Рендеринг двух шаблонов зависит от выполняемого условия.
        """
        
        if user_pk is None and token is None:
            return render(request = request, template_name = 'reset_pass.html')
        
        user = CustomUser.objects.get(pk = user_pk)
        
        if default_token_generator.check_token(user, token):
            return render(request = request, template_name='reset_pass_confirm.html')
        else:
            return render(request,'404.html')


    def post(self,request,user_pk=None,token=None):
        """
        Обработчик POST-запроса для отправки сообщения на email и изменение старого пароля на новый.
        
        Args:
        request: Объект запроса Django.
        user_pk: Уникальный идентификатор пользователя.
        token: Уникальный токен пользователя
        """
        
        if 'email' in request.POST:
            email = request.POST['email']
            user = CustomUser.objects.get(email = email)
        
            token = default_token_generator.make_token(user)
            verify_url = self.request.build_absolute_uri(f'/reset-pass/{user.pk}/{token}')
            message = f'Перейдите по ссылке чтобы изменить пароль: {verify_url}'
        
            send_mail('Изменить пароль',message,'',[email])
        
            return HttpResponseRedirect(reverse('home'))
        
        elif 'password' in request.POST:
            
            if request.POST['password'] != request.POST['password2']:
                return render(request,'400.html')

            user = get_object_or_404(CustomUser, pk = user_pk)
            new_password = request.POST['password']
            
            user.set_password(new_password)
            user.save()
            
            return HttpResponseRedirect(reverse('home'))


class HomePageMedia(ListView,ArchiveIndexView):
    """
    Представление для отображения медиа-файлов на домашней странице.
    
    model: Media - модель для отображения данных.
    template_name: 'home.html' - шаблон домашней страницы.
    date_field: 'created_at' - нужен для дальнейших фильтрации по дате медиа-файла.
    
    GET-параметры:
    m_type = 1: Для отображения фильмов
    m_type = 2: Для отображения сериалов
    """
    
    model = Media
    template_name = 'home.html'
    date_field = 'created_at'
    allow_empty = True
       
    def get_context_data(self,**kwargs):
        """
        Получение контекстных данных для передачи в шаблон home.html.
        
        Returns:
        context: Словарь с контекстными данными добавляемые до его возвращения.
        """
        
        if self.request.method == 'POST':
            print(self.request.POST['search-data'])
        
        context = super().get_context_data(**kwargs)
        
        current_time = timezone.now()
        time_threshold = current_time - timedelta(minutes = 10080)
        media = Media.objects.filter(created_at__gte = time_threshold).order_by('-created_at')
        
        if media:
            context['medias'] = media[0:9:1]
        else:
            media = Media.objects.all()[0:9:1]
            context['medias'] = media
        
        m_type = self.request.GET.get('m_type',1)
        if m_type == '2':
            serials = Media.objects.filter(m_type = 2)
            serial_filtred_lst = []
            for serial in serials:
                if len(serial_filtred_lst) == 12:
                    context['serials'] = serial_filtred_lst
                    break
                if serial.cover:
                    serial_filtred_lst.append(serial)
        else:
            films = Media.objects.filter(m_type = m_type)[0:12:1]
            
            if films:
                context['films'] = films
        
        return context
    

class MediaCatalog(ListView):
    """
    Представление для отображения каталога медиа-файлов с возможностью фильтрации.
    
    model: Media - модель для отображения данных.
    template_name: 'catalog.html' - шаблон страницы для отображения медиа-файлов.
    paginate_by: 6 - количество отображаемых элементов на одной странице.
    """
    
    model = Media
    template_name = 'catalog.html'
    paginate_by = 6
    
    def get_context_data(self,**kwargs):
        """
        Получение контекстных данных для передачи в шаблон catalog.html.
        
        Returns:
        context: Словарь с контекстными данными добавленными перед его возвращением.
        """
        context = super().get_context_data(**kwargs)
        media = None
        
        if self.kwargs:
            if self.kwargs['search_data']:
                media = Media.objects.filter(title__icontains = self.kwargs['search_data'])
        
        genre_id = self.request.session.get('genre_id',Genre.objects.all()[0].pk)
        start = self.request.session.get('start',None)
        end = self.request.session.get('end',None)
        start_year = self.request.session.get('start_year',None)
        end_year = self.request.session.get('end_year',None)
        
        if media is None:
            if genre_id is not None and start is not None and end is not None and start_year is not None and end_year is not None:
                media = Media.objects.filter(genre = genre_id).filter(rating__gte = start).filter(rating__lte = end).filter(year__gte = start_year).filter(year__lte = end_year)
            else:
                media = Media.objects.all()
        else:
             if genre_id is not None and start is not None and end is not None and start_year is not None and end_year is not None:
                media = Media.objects.filter(title__icontains=self.kwargs['search_data']).filter(genre = genre_id).filter(rating__gte = start).filter(rating__lte = end).filter(year__gte = start_year).filter(year__lte = end_year)
        
        
        genres = Genre.objects.all()
        tmp_selected_genre = Genre.objects.get(pk = genre_id)
        context['selected_genre'] = tmp_selected_genre
        genres = genres.exclude(genre_name = tmp_selected_genre.genre_name)
        
        context['genres'] = genres
        
        
        paginator = Paginator(media,self.paginate_by)
        page_number = int(self.request.GET.get('page',1))
        page = paginator.get_page(page_number)
        
        context['media'] = page
        
        all_pages = list()
        if page_number != paginator.num_pages:
            for page_num in range(page_number,page_number+3, 1):
                if page_num in [i for i in range(1,paginator.num_pages+1,1)]:
                    all_pages.append(str(page_num))
        elif page_number == 1 and page_number == paginator.num_pages:
            all_pages.append(str(page_number))
        else:
            for page_num in range(page_number,page_number-2,-1):
                all_pages.append(str(page_num))
                all_pages = all_pages[::-1]
                                        
                                    
        context['page_number'] = str(page_number)                                    
        context['all_pages'] = all_pages
        return context
    
    
    def post(self,request):
        """
        Обработчик POST-запроса для фильтрации медиа-файлов и сохранение полученных данных в сессии пользователя.
        
        Args:
        request: Объект запроса Django.
        
        Returns:
        Редирект на страницу каталога с учетом всех выбранных фильтров.
        """
        
        genre_id = Genre.objects.get(genre_name = request.POST['genre']).pk
        
        start = request.POST['rangeInput']
        end = request.POST['rangeInput2']
        
        start_year = request.POST['rangeInput3']
        end_year = request.POST['rangeInput4']
        
        
        request.session['genre_id'] = genre_id
        request.session['start'] = float(start)
        request.session['end'] = float(end)
        request.session['start_year'] = start_year
        request.session['end_year'] = end_year
        
        return redirect('catalog')
    

class ViewDetails(DetailView):
    """
    Это представление выполняет функции:
        1. Показ детальной информации фильма/сериала
        2. Показ фильмов/сериалов по такому же жанру
        3. Принятие отзывов пользователей и высчитывание средней оценки
    """
    
    model = Media
    template_name = 'details1.html'
    pk_url_kwarg = 'media_pk'
    context_object_name = 'media'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        search_data = kwargs.get('search_data')
        print(search_data)
        
        reviews = Review.objects.filter(media = self.kwargs['media_pk'])
        media = Media.objects.get(id = self.kwargs['media_pk'])
        
        paginator = Paginator(reviews,5)
        page_number = self.request.GET.get('show_page',1)
        page = paginator.get_page(page_number)
        
        context['reviews'] = page
        context['media_pk'] = self.kwargs['media_pk']
        
        alsoLikeMedias = Media.objects.filter(genre = media.genre)
        alsoLikeMedias = alsoLikeMedias[0:6:1]

        context['alsoLikeMedias'] = alsoLikeMedias
        
        actors = Actor.objects.filter(imdb = media.imdb)
        cast = ''
        for actor in actors:
            cast += f'{actor.surname} {actor.name}  '
        cast = cast.replace('  ',',').rstrip(',')
        context['actors'] = cast
        
        return context
    
    def post(self,request,media_pk):
        
        review = Review.objects.create(
            title = request.POST['title'],
            body = request.POST['body'],
            user = CustomUser.objects.get(id = self.request.user.pk),
            media = Media.objects.get(id = media_pk),
            rating = float(request.POST['rangeInput']),
        )
        
        media = Media.objects.get(id = media_pk)
        
        counter = 0
        temp_sum = 0
        for review in Review.objects.all():
            if review.media == media:
                temp_sum += review.rating
                counter += 1
        media.rating = temp_sum / counter
        media.save()
        
        review.save()
        return redirect('details',media_pk)


class ProfileHandler(View,LoginRequiredMixin):
    """
    Функции:
        1. Вывести текущие данные пользователя, принять и изменить их
        2. Отправка письма и вызов другого представления по роуту '/reset-pass/...' против дублирования кода
    """
    
    template_name = 'profile.html'
    
    def get(self,request,user_pk):
        try:
            profile = CustomUser.objects.get(id = user_pk)
        except CustomUser.DoesNotExist:
            return render(request,'404.html')
        
        user = request.user
        if user.is_authenticated and user.pk == user_pk:
            initial_data = {
                'username':user.username,
                'email':user.email,
            }
            user_profile_form = UserProfileForm(initial = initial_data)
            password_email_reset = PasswordChangeForm()
        
            reviews = Review.objects.filter(user = user_pk)
            return render(request,self.template_name,{'form':user_profile_form,'form2':password_email_reset,'reviews':reviews})
        else:
            return render(request,'400.html')
    
    def post(self,request,user_pk):
        user_profile_form = UserProfileForm(request.POST,request.FILES)
        password_email_reset = PasswordChangeForm(request.POST)
        
        if user_profile_form.is_valid():
            username = user_profile_form.cleaned_data['username']
            email = user_profile_form.cleaned_data['email']
            avatar = user_profile_form.cleaned_data['avatar']
            
            
            user = request.user
            user.username = username
            user.email = email
                
            if avatar:
                user.avatar = avatar
                    
            user.save()
        
        if password_email_reset.is_valid():
            email = password_email_reset.cleaned_data['password_reset_email']
            user = request.user
            
            if email == user.email:
                token = default_token_generator.make_token(user)
                verify_url = self.request.build_absolute_uri(f'/reset-pass/{user.pk}/{token}')
                message = f'Перейдите по ссылке чтобы изменить пароль: {verify_url}'
        
                send_mail('Изменить пароль',message,'',[email])
        return redirect('home')


def DeleteReview(request,review_id):
    """
    Удаление отзыва пользователя по review_id
    """
    if request.user.is_authenticated and Review.objects.get(id=review_id).user == request.user:
        lst = []
        for review in Review.objects.all():
            lst.append(review.pk)
        
        if review_id in lst:
            review = Review.objects.get(id = review_id)
            review.delete()
            return redirect('profile',request.user.pk)
        else:
            return render(request,'400.html')
    else:
        return render(request,'400.html')
    
def BaseSearchView(request):
    data = request.POST['search-data']
    return redirect('search_catalog',data)