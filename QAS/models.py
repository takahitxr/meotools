# models.py
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator,MaxValueValidator

class SatisfactionChoice(models.Model):
    
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=100, blank=True, null=True)
    store_code = models.CharField(max_length=100, blank=True, null=True)
    google_review_url = models.URLField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return str(self.user)

class ReviewSetting(models.Model):
    question_title = models.CharField(max_length=100, default="ご来店ありがとうございました。本日は満足していただけましたでしょうか？")
    very_satisfied_label = models.CharField(max_length=100, default="非常に満足")
    satisfied_label = models.CharField(max_length=100, default="満足")
    neutral_label = models.CharField(max_length=100, default="普通")
    dissatisfied_label = models.CharField(max_length=100, default="不満")
    very_dissatisfied_label = models.CharField(max_length=100, default="非常に不満")
    very_satisfied_redirect_url = models.CharField(max_length=100, blank=True, null=True)
    satisfied_redirect_url = models.CharField(max_length=100, blank=True, null=True)
    neutral_redirect_url = models.CharField(max_length=100, blank=True, null=True)
    dissatisfied_redirect_url = models.CharField(max_length=100, blank=True, null=True)
    very_dissatisfied_redirect_url = models.CharField(max_length=100, blank=True, null=True)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)
    
class ImproveSetting(models.Model):
    question_title = models.CharField(max_length=100, blank=True)
    question_text1 = models.CharField(max_length=100, blank=True)
    is_required1 = models.BooleanField(default=False, blank=True)
    question_text2 = models.CharField(max_length=100, blank=True)
    is_required2 = models.BooleanField(default=False, blank=True)
    question_text3 = models.CharField(max_length=100, blank=True)
    is_required3 = models.BooleanField(default=False, blank=True)
    question_text4 = models.CharField(max_length=100, blank=True)
    is_required4 = models.BooleanField(default=False, blank=True)
    question_text5 = models.CharField(max_length=100, blank=True)
    is_required5 = models.BooleanField(default=False, blank=True)
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)
    

class ShopReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
    
class ImproveResult(models.Model):
    question_text1 = models.CharField(max_length=100, blank=True)
    question_text2 = models.CharField(max_length=100, blank=True)
    question_text3 = models.CharField(max_length=100, blank=True)
    question_text4 = models.CharField(max_length=100, blank=True)
    question_text5 = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return str(self.user)
    