from django.contrib import admin
from .models import UserProfile, ReviewSetting, ShopReview, ImproveSetting, ImproveResult

admin.site.register(UserProfile)
admin.site.register(ShopReview)
admin.site.register(ReviewSetting)
admin.site.register(ImproveSetting)
admin.site.register(ImproveResult)