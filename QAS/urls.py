from django.contrib import admin
from django.urls import path
from QAS.views import ReviewFormView, KanriView, CustomLoginView, UserSettingsView, SignUpView, FeedbackView, ImproveSettingsView, ImproveFormView,ImproveResultsView, StoreNameUpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView

urlpatterns = [
    path('<str:store_code>/review/', ReviewFormView.as_view(), name='review_form'),
    path('success/', TemplateView.as_view(template_name='QAS/success.html'), name='success'),
    path('fail/', TemplateView.as_view(template_name='QAS/fail.html'), name='fail'),
    path('feedback/', FeedbackView.as_view(template_name='QAS/feedback.html'), name='feedback'),
    path('kanri/', KanriView.as_view(), name='kanri'),
    path('login/', LoginView.as_view(template_name='QAS/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', LoginView.as_view(template_name='QAS/kanri.html'), name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('settings/', UserSettingsView.as_view(), name='user_settings'),
    path('improve_settings/', ImproveSettingsView.as_view(), name='improve_settings'),
    path('<str:store_code>/improve/', ImproveFormView.as_view(), name='improve_page'),
    path('improve_results/', ImproveResultsView.as_view(), name='improve_result_list'),
    path('name_setting/', StoreNameUpdateView.as_view(), name='name_setting'),
]