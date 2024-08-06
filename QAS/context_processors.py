from .models import UserProfile

def store_code_processor(request):
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            return {'store_code': user_profile.store_code}
        except UserProfile.DoesNotExist:
            print("ダメ")
            return {'store_code': None}
    print("ダメダメ")
    return {'store_code': None}