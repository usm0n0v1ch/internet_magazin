# forms.py
from django import forms
from .models import Product, Brand, Category, Review


class AdvancedSearchForm(forms.Form):
    price_min = forms.DecimalField(required=False, label='Минимальная цена')
    price_max = forms.DecimalField(required=False, label='Максимальная цена')
    in_stock = forms.BooleanField(required=False, initial=True, label='Только в наличии')
    brands = forms.ModelMultipleChoiceField(queryset=Brand.objects.all(), required=False, label='Бренды')
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), required=False, label='Категории')
    has_reviews = forms.BooleanField(required=False, label='Товары с отзывами')
    average_rating_min = forms.DecimalField(required=False, label='Минимальный рейтинг')
    is_new = forms.BooleanField(required=False, label='Новинки')
    is_popular = forms.BooleanField(required=False, label='Популярные')
    is_on_sale = forms.BooleanField(required=False, label='Со скидкой')



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш отзыв...'}),
        }