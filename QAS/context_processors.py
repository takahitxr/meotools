from .models import UserProfile
import urllib.parse


def store_code_processor(request):
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return {'store_code': user_profile.store_code}
        except UserProfile.DoesNotExist:
            return {'store_code': None}
    return {'store_code': None}

def store_name_processor(request):
    store_name = "店舗名未設定"
    
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.store_name:
                store_name = user_profile.store_name
        except UserProfile.DoesNotExist:
            pass
    
    return {'store_name': store_name}

def store_address_processor(request):
    decoded_url = "https://www.google.com/"

    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.google_review_url:
                decoded_url = urllib.parse.unquote(user_profile.google_review_url)
        except UserProfile.DoesNotExist:
            pass
    
    return {'store_address': decoded_url}