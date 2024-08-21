from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView
from django.shortcuts import render, redirect
from .forms import UserSettingsForm, SignUpForm, ReviewForm, FeedBackForm, ImproveSettingsForm, ImproveForm, StoreNameForm
from .models import SatisfactionChoice, User, ReviewSetting, ShopReview, ImproveSetting, ImproveResult, UserProfile
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.contrib.auth import login
from django.utils import timezone
from django.contrib import messages
import urllib.parse
from django.urls import reverse
import requests
from django.http import JsonResponse

class KanriView(LoginRequiredMixin, TemplateView):
    template_name = 'QAS/kanri.html'
    login_url = 'login'
    model = ShopReview

    def dispatch(self, request, *args, **kwargs):
        self.store_code = kwargs.get('store_code')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_code = self.store_code
        try:
            user_profile = UserProfile.objects.get(store_code=store_code)
        except UserProfile.DoesNotExist:
            context['error_message'] = 'ストアコードが存在しません'
            context['redirect_url'] = reverse_lazy('name_setting')
            self.template_name = 'QAS/error.html'
            return context
        
        reviews = ShopReview.objects.filter(user=user_profile.user).order_by("-created_at")
        review_counts = {
            'very_satisfied': reviews.filter(rating=5).count(),
            'satisfied': reviews.filter(rating=4).count(),
            'neutral': reviews.filter(rating=3).count(),
            'dissatisfied': reviews.filter(rating=2).count(),
            'very_dissatisfied': reviews.filter(rating=1).count(),
        }
        context['review_counts'] = review_counts
        context['latest_reviews'] = reviews
        return context
    
    
class ReviewFormView(FormView):
    template_name = 'QAS/review.html'
    form_class = ReviewForm

    def dispatch(self, request, *args, **kwargs):
        self.store_code = kwargs.get('store_code')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_code = self.store_code

        try:
            user_profile = UserProfile.objects.get(store_code=store_code)
            review_setting = ReviewSetting.objects.get(user=user_profile.user)
            improve_setting = ImproveSetting.objects.get(user=user_profile.user)

            if not user_profile.store_name:
                context['error_message'] = '店舗名が入力されていません。'
                context['redirect_url'] = reverse_lazy('name_setting')
                self.template_name = 'QAS/error.html'
                return context

            if not user_profile.google_review_url:
                context['error_message'] = '店舗レビューURLが入力されていません。'
                context['redirect_url'] = reverse_lazy('name_setting')
                self.template_name = 'QAS/error.html'
                return context
            
            if not improve_setting.question_title or not improve_setting.question_text1:
                context['error_message'] = 'レビュー後の質問ページが設定されていません。'
                context['redirect_url'] = reverse_lazy('improve_settings')
                self.template_name = 'QAS/error.html'
                return context

            context['question_title'] = review_setting.question_title
            context['very_satisfied_label'] = review_setting.very_satisfied_label
            context['satisfied_label'] = review_setting.satisfied_label
            context['neutral_label'] = review_setting.neutral_label
            context['dissatisfied_label'] = review_setting.dissatisfied_label
            context['very_dissatisfied_label'] = review_setting.very_dissatisfied_label
            context['store_code'] = store_code
            context['store_name'] = user_profile.store_name

        except UserProfile.DoesNotExist:
            context['error_message'] = '店舗名、店舗レビューURLが入力されていません。'
            context['redirect_url'] = reverse_lazy('name_setting')
            self.template_name = 'QAS/error.html'
        except ReviewSetting.DoesNotExist:
            context['error_message'] = 'レビュー項目が入力されていません。'
            context['redirect_url'] = reverse_lazy('user_settings')
            self.template_name = 'QAS/error.html'
        except ImproveSetting.DoesNotExist:
            context['error_message'] = 'レビューがまだ存在しません。'
            context['redirect_url'] = reverse_lazy('user_settings')
            self.template_name = 'QAS/error.html'

        return context

    def form_valid(self, form):
        satisfaction = form.cleaned_data['satisfaction']
        store_code = self.store_code
        user_profile = UserProfile.objects.get(store_code=store_code)
        review_setting = ReviewSetting.objects.get(user=user_profile.user)

        rating_map = {
            'very_satisfied': 5,
            'satisfied': 4,
            'neutral': 3,
            'dissatisfied': 2,
            'very_dissatisfied': 1
        }
        text_map = {
            'very_satisfied': review_setting.very_satisfied_label,
            'satisfied': review_setting.satisfied_label,
            'neutral': review_setting.neutral_label,
            'dissatisfied': review_setting.dissatisfied_label,
            'very_dissatisfied': review_setting.very_dissatisfied_label
        }
        reviewtext = text_map.get(satisfaction, "不明")

        rating = rating_map.get(satisfaction, 0)
        ShopReview.objects.create(
            user=user_profile.user,
            rating=rating,
            review_text=reviewtext,
        )
        success_url = reverse('success', args=[store_code])

        if satisfaction == 'very_satisfied' and review_setting.very_satisfied_redirect_url == "google_review":
            return redirect(success_url)
        elif satisfaction == 'satisfied' and review_setting.satisfied_redirect_url == "google_review":
            return redirect(success_url)
        elif satisfaction == 'neutral' and review_setting.neutral_redirect_url == "google_review":
            return redirect(success_url)
        elif satisfaction == 'dissatisfied' and review_setting.dissatisfied_redirect_url == "google_review":
            return redirect(success_url)
        elif satisfaction == 'very_dissatisfied' and review_setting.very_dissatisfied_redirect_url == "google_review":
            return redirect(success_url)
        else:
            improve_url = f'/{store_code}/improve/'
            return redirect(improve_url)


    def render_error_page(self, message):
        return render(self.request, 'QAS/error.html', {'message': message})


class SuccessView(TemplateView):
    template_name = 'QAS/success.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.store_code = kwargs.get('store_code')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_code = self.store_code
        user_profile = UserProfile.objects.get(store_code=store_code)
        context['store_address'] = user_profile.google_review_url
        return context




class UserSettingsView(LoginRequiredMixin, UpdateView):
    model = ReviewSetting
    form_class = UserSettingsForm
    template_name = 'QAS/user_settings.html'
    success_url = '/settings/'
    login_url = 'login'

    def get_object(self, queryset=None):
        # ログインユーザーのReviewSettingを取得、存在しない場合は新規作成
        obj, created = ReviewSetting.objects.get_or_create(user=self.request.user)
        return obj
    def form_valid(self, form):
        messages.success(self.request, '設定が更新されました。')
        return super().form_valid(form)
    
class ImproveSettingsView(LoginRequiredMixin, UpdateView):
    form_class = ImproveSettingsForm
    template_name = 'QAS/improve_settings.html'
    success_url = '/improve_settings/'
    login_url = 'login'

    def get_object(self, queryset=None):
        obj, created = ImproveSetting.objects.get_or_create(user=self.request.user)
        return obj

    def form_invalid(self, form):
        # エラーページを表示
        return render(self.request, 'QAS/error.html', {'message': '必須項目が入力されていません。', 'form_errors': form.errors})

    def form_valid(self, form):
        messages.success(self.request, '設定が更新されました。')
        return super().form_valid(form)
    



class FeedbackView(FormView):
    template_name = 'QAS/feedback.html'
    form_class = FeedBackForm
    model = ShopReview
    

    def form_valid(self, form):
        review = form.save(commit=False)
        review.user = self.request.user
        review.save()
        return redirect(self.success_url)



class SignUpView(TemplateView):
    template_name = 'QAS/signup.html'

    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('kanri')  # ログイン後にリダイレクトするページ
        return render(request, self.template_name, {'form': form})

    def get(self, request, *args, **kwargs):
        form = SignUpForm()
        return render(request, self.template_name, {'form': form})
    

class CustomLoginView(LoginView):
    template_name = 'QAS/login.html'

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me', None)
        if remember_me:
            self.request.session.set_expiry(1209600)  # 2週間
        else:
            self.request.session.set_expiry(0)  # ブラウザを閉じるとセッションが失効
        return super().form_valid(form)



class ImproveFormView(FormView):
    template_name = 'QAS/improvepage.html'
    form_class = ImproveForm
    
    def dispatch(self, request, *args, **kwargs):
        self.store_code = kwargs.get('store_code')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_code = self.store_code
        user_profile = UserProfile.objects.get(store_code=store_code)
        improve_setting = ImproveSetting.objects.get(user=user_profile.user)
        context['question_text1'] = improve_setting.question_text1
        context['question_text2'] = improve_setting.question_text2
        context['question_text3'] = improve_setting.question_text3
        context['question_text4'] = improve_setting.question_text4
        context['question_text5'] = improve_setting.question_text5
        context['is_required1'] = improve_setting.is_required1
        context['is_required2'] = improve_setting.is_required2
        context['is_required3'] = improve_setting.is_required3
        context['is_required4'] = improve_setting.is_required4
        context['is_required5'] = improve_setting.is_required5

        return context

    def form_valid(self, form):
        response1 = form.cleaned_data['question1_response']
        response2 = form.cleaned_data['question2_response']
        response3 = form.cleaned_data['question3_response']
        response4 = form.cleaned_data['question4_response']
        response5 = form.cleaned_data['question5_response']
        store_code = self.store_code
        user_profile = UserProfile.objects.get(store_code=store_code)
        user=user_profile.user
        ImproveResult.objects.create(
            user=user,
            question_text1 = response1,
            question_text2 = response2,
            question_text3 = response3,
            question_text4 = response4,
            question_text5 = response5,
            created_at=timezone.now()
        )

        success_url = reverse('success', args=[store_code])
        return redirect(success_url)
    


class ImproveResultsView(LoginRequiredMixin, TemplateView):
    template_name = 'QAS/improve_result_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            improve_results = ImproveResult.objects.order_by('-created_at')
            improve_setting = ImproveSetting.objects.get(user=self.request.user)

            context['improve_results'] = improve_results
            context['improve_setting'] = improve_setting
        except:
            context['error_message'] = 'レビュー後の質問ページの質問項目を入力してください。'
            context['redirect_url'] = reverse_lazy('improve_settings')
            self.template_name = 'QAS/error.html'
            return context


        return context
    

class StoreNameUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = StoreNameForm
    template_name = 'QAS/store_name_update.html'

    def get_success_url(self):
        return self.request.path  # 現在のページにリダイレクト

    def get_object(self, queryset=None):
        # 現在のユーザーのUserProfileインスタンスを取得
        return UserProfile.objects.get(user=self.request.user)

    def form_valid(self, form):
        form.save()  # フォームデータを保存
        messages.success(self.request, '設定が更新されました。')
        return super().form_valid(form)


def get_place_id(request):
    store_name = request.GET.get('store_name')
    address = request.GET.get('store_address')
    api_key = 'AIzaSyCTGBvebknFJ5LOtbNSYGm7Gr0nTrCxQDI'
    search_query = f'{store_name} {address}'

    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={search_query}&inputtype=textquery&fields=place_id&key={api_key}"
    
    response = requests.get(url)
    data = response.json()
    if data['status'] == 'OK':
        return JsonResponse({'place_id': data['candidates'][0]['place_id']})
    else:
        return JsonResponse({'error': 'Place not found'}, status=400)