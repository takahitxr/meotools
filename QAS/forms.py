from django import forms
from .models import UserProfile, ReviewSetting, ShopReview, ImproveSetting, AutoResponse, AiResponse
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
        'question_title': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '(例) ご来店ありがとうございました。本日は満足していただけましたでしょうか？'}),
        'very_satisfied_label' : forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '(例) 非常に満足'}),
        'satisfied_label' : forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '(例) 満足'}),
        'neutral_label' : forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '(例) 普通'}),
        'dissatisfied_label' : forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '(例) 不満'}),
        'very_dissatisfied_label' : forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '(例) 非常に不満'}),
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
            'question_title': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '(例) 感想を教えてください。'}),
            'question_text1': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '(例) 料理はいかがでしたか？'}),
            'is_required1': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'question_text2': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '(例) 接客態度はいかがでしたか？'}),
            'is_required2': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'question_text3': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '(例) 改善したほうがいいと思う点を教えてください。'}),
            'is_required3': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'question_text4': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '(例) 改善したほうがいいと思う点を教えてください。'}),
            'is_required4': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'question_text5': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '(例) 改善したほうがいいと思う点を教えてください。'}),
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
        fields = ['store_name','store_address' , 'google_review_url']
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '店舗名'}),
            'store_address': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '住所'}),
            'google_review_url' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'レビューURL'})
        }


class AutoResponseForm(forms.ModelForm):
    class Meta:
        model = AutoResponse
        fields = ['pattern_name', 'filter_text', 'response_text', 'bool_text', 'is_auto']
        widgets = {
            'pattern_name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'filter_text': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'bool_text': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'response_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'required': 'required'}),
            'is_auto': forms.CheckboxInput(attrs={'class': 'custom-switch'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        pattern_name = cleaned_data.get("pattern_name")
        filter_text = cleaned_data.get("filter_text")
        bool_text = cleaned_data.get("bool_text")
        response_text = cleaned_data.get("response_text")

        if not pattern_name or not filter_text or not bool_text or not response_text:
            raise forms.ValidationError("全てのフィールドに入力が必要です。")


class ResponseSettingsForm(forms.ModelForm):
    class Meta:
        model = AutoResponse
        fields = [
            'response_text',
            'is_auto',
        ]
        widgets = {
            'response_text': forms.TextInput(attrs={'class': 'custom-textbox inline'}),
            'is_auto': forms.CheckboxInput(attrs={'class': 'custom-switch'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        required_fields = [
            ('response_text', 'is_auto'),
        ]

        for question_field, required_field in required_fields:
            if cleaned_data.get(required_field) and not cleaned_data.get(question_field):
                self.add_error(question_field, f"{self.fields[question_field].label}は必須です。")

class AiResponseForm(forms.ModelForm):
    class Meta:
        model = AiResponse
        fields = ['tone_level', 'business_type', 'match_language']
        widgets = {
            'business_type': forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '例：レストラン/焼肉屋など'}),
            'tone_level': forms.Select(attrs={'class': 'tone-form inline'}),
            'match_language': forms.CheckboxInput(attrs={'class': 'required-label'}),
        }

class AiResponseTestForm(forms.Form):
    response_text = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control inline', 'placeholder': '定食が安くておいしかった。'}),
        label='返信テンプレート'
    )