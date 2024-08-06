from django import forms
from .models import UserProfile, ReviewSetting, ShopReview, ImproveSetting
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.username = self.cleaned_data['email']  # メールアドレスをユーザー名として使用
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            if not UserProfile.objects.filter(user=user).exists():
                UserProfile.objects.create(user=user)  # プロファイルを作成
        return user
        
class ReviewForm(forms.Form):
    satisfaction = forms.ChoiceField(
        choices=[
            ('very_satisfied', '非常に満足'),
            ('satisfied', '満足'),
            ('neutral', '普通'),
            ('dissatisfied', '不満'),
            ('very_dissatisfied', '非常に不満')
        ],
        widget=forms.RadioSelect
    )


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = ReviewSetting
        fields = [
            'question_title',
            'very_satisfied_label',
            'satisfied_label',
            'neutral_label',
            'dissatisfied_label',
            'very_dissatisfied_label',
            'very_satisfied_redirect_url',
            'satisfied_redirect_url',
            'neutral_redirect_url',
            'dissatisfied_redirect_url',
            'very_dissatisfied_redirect_url'
        ]
        widgets = {
        'question_title': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '店舗名'}),
        'very_satisfied_label' : forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': 'レビューURL'})
    }


class ImproveSettingsForm(forms.ModelForm):
    class Meta:
        model = ImproveSetting
        fields = [
            'question_title',
            'question_text1',
            'is_required1',
            'question_text2',
            'is_required2',
            'question_text3',
            'is_required3',
            'question_text4',
            'is_required4',
            'question_text5',
            'is_required5',
        ]
        widgets = {
            'question_title': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '感想を教えてください。'}),
            'question_text1': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '料理はいかがでしたか？'}),
            'is_required1': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'question_text2': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '接客態度はいかがでしたか？'}),
            'is_required2': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'question_text3': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '改善したほうがいいと思う点を教えてください。'}),
            'is_required3': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'question_text4': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '改善したほうがいいと思う点を教えてください。'}),
            'is_required4': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'question_text5': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '改善したほうがいいと思う点を教えてください。'}),
            'is_required5': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        required_fields = [
            ('question_text1', 'is_required1'),
            ('question_text2', 'is_required2'),
            ('question_text3', 'is_required3'),
            ('question_text4', 'is_required4'),
            ('question_text5', 'is_required5'),
        ]

        for question_field, required_field in required_fields:
            if cleaned_data.get(required_field) and not cleaned_data.get(question_field):
                self.add_error(question_field, f"{self.fields[question_field].label}は必須です。")

        
class FeedBackForm(forms.ModelForm):
    class Meta:
        model = ShopReview
        fields = ['rating', 'review_text']
        
        rating = forms.IntegerField(widget=forms.HiddenInput())


class ImproveForm(forms.Form):
    question1_response = forms.CharField(required=False)
    question2_response = forms.CharField(required=False)
    question3_response = forms.CharField(required=False)
    question4_response = forms.CharField(required=False)
    question5_response = forms.CharField(required=False)

class StoreNameForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['store_name', 'google_review_url']
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '店舗名'}),
            'google_review_url' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'レビューURL'})
        }
