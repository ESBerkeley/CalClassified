from django import forms

class ImageForm(forms.Form):
	imgfile = forms.ImageField(
		label='Select a file',
		help_text='max. 10 megabytes')




