from django.contrib import admin
from django.urls import path
from QAS.views import ReviewFormView, KanriView, SuccessView, UserSettingsView, SignUpView, FeedbackView, \
    ImproveSettingsView, ImproveFormView,ImproveResultsView, StoreNameUpdateView, get_place_id, \
    ResponseSettingsView, ai_response_settings_view, ai_response_test_view,auto_response_list_view,delete_auto_response
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView

urlpatterns = [
    path('<str:store_code>/review/', ReviewFormView.as_view(), name='review_form'),
    path('<str:store_code>/success/', SuccessView.as_view(), name='success'),
    path('finish/', TemplateView.as_view(template_name='QAS/finish.html'), name='finish'),
    path('feedback/', FeedbackView.as_view(template_name='QAS/feedback.html'), name='feedback'),
    path('<str:store_code>/question_result/', KanriView.as_view(), name='question_result'),
    path('login/', LoginView.as_view(template_name='QAS/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', KanriView.as_view(template_name='QAS/kanri.html'), name='home'),
    path('user-signup/', SignUpView.as_view(), name='signup'),
    path('question_settings/', UserSettingsView.as_view(), name='question_settings'),
    path('improve_settings/', ImproveSettingsView.as_view(), name='improve_settings'),
    path('<str:store_code>/improve/', ImproveFormView.as_view(), name='improve_page'),
    path('improve_results/', ImproveResultsView.as_view(), name='improve_result_list'),
    path('name_setting/', StoreNameUpdateView.as_view(), name='name_setting'),
    path('response_list/', auto_response_list_view, name='response_list'),
    path('delete/<int:id>/', delete_auto_response, name='delete_auto_response'),
    path('get_place_id/', get_place_id, name='get_place_id'),
    path('aisettings/', ai_response_settings_view, name='aisettings'),
    path('settings/test/', ai_response_test_view, name='ai-response-test'),
]