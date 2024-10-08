from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView,UpdateView
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserSettingsForm, SignUpForm, ReviewForm, FeedBackForm, ImproveSettingsForm, ImproveForm, StoreNameForm, ResponseSettingsForm,AiResponseForm,AiResponseTestForm,AutoResponseForm
from .models import SatisfactionChoice, User, ReviewSetting, ShopReview, ImproveSetting, ImproveResult, UserProfile, AutoResponse, AiResponse
from django.contrib.auth import login
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse
import requests
from django.http import JsonResponse
from datetime import datetime
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from .apiset import chatGPTtest


class KanriView(LoginRequiredMixin, TemplateView):
    template_name = 'QAS/question_result.html'
    login_url = 'login'
    
    def dispatch(self, request, *args, **kwargs):
        self.store_code = kwargs.get('store_code')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_code = self.store_code
        try:
            user_profile = UserProfile.objects.get(store_code=store_code)
            reviews = ShopReview.objects.filter(user=user_profile.user).order_by("-created_at")

            preset_range = self.request.GET.get('preset_range', '12months')
            start_date = None
            end_date = None

            if preset_range:
                now = timezone.now()
                
                if preset_range == '1week':
                    start_date = now - timedelta(weeks=1)
                elif preset_range == '1month':
                    start_date = now - timedelta(days=30)
                elif preset_range == '3months':
                    start_date = now - timedelta(days=90)
                elif preset_range == '6months':
                    start_date = now - timedelta(days=180)
                elif preset_range == '12months':
                    start_date = now - timedelta(days=365)
                end_date = now

                if preset_range == 'custom':
                    date_range = self.request.GET.get('date_range', None)
                    if date_range:
                        date_range = date_range.split(" から ")
                        if len(date_range) == 2:
                            start_date = parse_date(date_range[0].replace('/', '-').strip())
                            end_date = parse_date(date_range[1].replace('/', '-').strip())
                            if start_date:
                                start_date = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
                            if end_date:
                                end_date = timezone.make_aware(datetime.combine(end_date, datetime.min.time())) + timedelta(days=1)

            if start_date and end_date:
                reviews = reviews.filter(created_at__gte=start_date, created_at__lt=end_date)

            # レビュー数の集計
            review_counts = {
                'very_satisfied': reviews.filter(rating=5).count(),
                'satisfied': reviews.filter(rating=4).count(),
                'neutral': reviews.filter(rating=3).count(),
                'dissatisfied': reviews.filter(rating=2).count(),
                'very_dissatisfied': reviews.filter(rating=1).count(),
            }

            context['review_counts'] = review_counts
            context['latest_reviews'] = reviews

        except UserProfile.DoesNotExist:
            context['error_message'] = 'ストアコードが存在しません'
            context['redirect_url'] = reverse_lazy('name_setting')
            self.template_name = 'QAS/error.html'
            return context

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
            context['redirect_url'] = reverse_lazy('question_settings')
            self.template_name = 'QAS/error.html'
        except ImproveSetting.DoesNotExist:
            context['error_message'] = 'レビューがまだ存在しません。'
            context['redirect_url'] = reverse_lazy('question_settings')
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
    template_name = 'QAS/question_settings.html'
    success_url = '/question_settings/'
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
            return redirect('question_result')  # ログイン後にリダイレクトするページ
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
        context['question_title'] = improve_setting.question_title
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
        finish_url = reverse('finish')
        return redirect(finish_url)
    


class ImproveResultsView(LoginRequiredMixin, TemplateView):
    template_name = 'QAS/improve_result_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            improve_setting = ImproveSetting.objects.get(user=self.request.user)
            months = ImproveResult.objects.filter(user=self.request.user)\
                .annotate(month=TruncMonth('created_at'))\
                .values('month')\
                .distinct()\
                .order_by('-month')
            
            context['months'] = months

            selected_month = self.request.GET.get('month')

            if selected_month:
                start_date = parse_date(f"{selected_month}-01")
                end_date = datetime(start_date.year, start_date.month + 1, 1)
                improve_results = ImproveResult.objects.filter(user=self.request.user, created_at__gte=start_date, created_at__lt=end_date).order_by("-created_at")
            else:
                improve_results = ImproveResult.objects.filter(user=self.request.user).order_by("-created_at")

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
    


class ResponseSettingsView(LoginRequiredMixin, UpdateView):
    form_class = ResponseSettingsForm
    template_name = 'QAS/response_settings.html'
    success_url = '/response_settings/'
    login_url = 'login'

    def get_object(self, queryset=None):
        obj, created = AutoResponse.objects.get_or_create(user=self.request.user)
        return obj

    def form_invalid(self, form):
        return render(self.request, 'QAS/error.html', {'message': '必須項目が入力されていません。', 'form_errors': form.errors})

    def form_valid(self, form):
        messages.success(self.request, '設定が更新されました。')
        return super().form_valid(form)
    
def auto_response_list_view(request):

    auto_responses = AutoResponse.objects.filter(user=request.user)
    if request.method == 'POST':
        if 'save_changes' in request.POST:
            auto_responses = AutoResponse.objects.filter(user=request.user)
            for auto_response in auto_responses:
                prefix = str(auto_response.id)
                form = AutoResponseForm(request.POST, instance=auto_response, prefix=prefix)
                if form.is_valid():
                    form.save()
            return redirect('response_list')
        else:
            if auto_responses.count() >= 10:
                messages.error(request, 'パターンの登録上限は10件です。')
            else:
                form = AutoResponseForm(request.POST)
                if form.is_valid():
                    auto_response = form.save(commit=False)
                    auto_response.user = request.user
                    auto_response.save()
                    return redirect('response_list')
    else:
        form = AutoResponseForm()

    form_pairs = [(AutoResponseForm(instance=auto_response, prefix=str(auto_response.id)), auto_response) for auto_response in auto_responses]
    
    return render(request, 'QAS/response_list.html', {
        'form': form, 
        'form_pairs': form_pairs,
    })

def delete_auto_response(request, id):
    auto_response = get_object_or_404(AutoResponse, id=id, user=request.user)
    auto_response.delete()
    return redirect('response_list')




class AiSettingsView(LoginRequiredMixin, UpdateView):
    form_class = AiResponseForm
    template_name = 'QAS/aisettings.html'
    login_url = 'login'

    def get_object(self, queryset=None):
        obj, created = AiResponse.objects.get_or_create(user=self.request.user)
        return obj

    def form_valid(self, form):
        messages.success(self.request, 'プロンプト設定が更新されました。')
        return super().form_valid(form)
    


def ai_response_settings_view(request):
    user = request.user
    ai_response, created = AiResponse.objects.get_or_create(user=user)

    if request.method == 'POST' and 'save_settings' in request.POST:
        settings_form = AiResponseForm(request.POST, instance=ai_response)
        if settings_form.is_valid():
            settings_form.save()
            messages.success(request, '設定が保存されました。')
            return redirect('aisettings')

    else:
        settings_form = AiResponseForm(instance=ai_response)

    test_form = AiResponseTestForm()
    return render(request, 'QAS/aisettings.html', {
        'settings_form': settings_form,
        'test_form': test_form,
        'preview_text': None
    })






def ai_response_test_view(request):
    user = request.user
    ai_response = get_object_or_404(AiResponse, user=user)

    if request.method == 'POST' and 'run_test' in request.POST:
        test_form = AiResponseTestForm(request.POST)
        if test_form.is_valid():
            response_text = test_form.cleaned_data['response_text']
            Aisettings = AiResponse.objects.filter(user=request.user).first()
            if Aisettings:
                shoptype = Aisettings.business_type
                tone_level = Aisettings.tone_level
                match_language = Aisettings.match_language
                restemplate = Aisettings.response_text

                prompt = create_prompt(shoptype, tone_level, match_language)
                question = create_question(restemplate, response_text)


                generated_text = chatGPTtest(question, prompt)

                return render(request, 'QAS/aisettings.html', {
                    'settings_form': AiResponseForm(instance=ai_response),
                    'test_form': test_form,
                    'preview_text': generated_text
                })

    return redirect('aisettings')



def create_prompt(shoptype, tone_level, match_language):
    prompt = f"あなたは{shoptype}の店長です。" if shoptype else ""
    prompt += f"口調は{tone_level}にしてください。"

    if match_language:
        prompt += "レビューと同じ言語を使ってください。"
    else:
        prompt += "日本語で返事してください。"

    return prompt

def create_question(restemplate, response_text):
    if restemplate:
        return f"{restemplate}/この部分より前の情報を考慮して次のレビューに返信してください。{response_text}"
    else:
        return f"以下のレビューに返信してください。{response_text}"