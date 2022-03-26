from django import forms
from .models import Image
from urllib import request
from django.core.files.base import ContentFile
from django.utils.text import slugify
import certifi



# As you will notice in the preceding code, 
# this form is a ModelForm form built from 
# the Image model, including only the title, 
# url, and description fields. Users will not
# enter the image URL directly in the form. Instead,
# you will provide them with a JavaScript tool to choose 
# an image from an external site, and your form will receive 
# its URL as a parameter. You override the default widget of the 
# url field to use a HiddenInput widget. This widget is rendered as an HTML input element with 
# a type="hidden" attribute. You use this widget because you don't want this field to be visible to users.
class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title', 'url', 'description')
        widgets = {
            'url': forms.HiddenInput
        }

    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extensions = ['jpg', 'jpeg']
        extension = url.rsplit('.',1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError('The given URL does not match valid image extensions.')
        return url
    
    #6
    def save(self, force_insert=False, force_update=False,commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        name = slugify(image.title)
        extension = image_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{extension}'
        # download image from the given URL
        # response = request.urlopen(image_url)
        response = request.urlopen(image_url,cafile=certifi.where())
        image.image.save(image_name, ContentFile(response.read()), save=False)
        if commit:
            image.save()
        return image

