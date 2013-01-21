from django import forms

class ImageForm(forms.Form):
	imgfile = forms.ImageField(
		label='Select a file',
		help_text='max. 10 megabytes')

class EmailForm(forms.Form):
    # this will not be the username as well for a facebook account
    email = forms.EmailField()

class FeedbackForm(forms.Form):
    email = forms.EmailField(label="Email")
    message = forms.CharField(label="Feedback", required=True, widget=forms.Textarea(attrs={
        'placeholder':'e.g. I had a hard time selling my item, because the buyer flaked on me :('
    }))