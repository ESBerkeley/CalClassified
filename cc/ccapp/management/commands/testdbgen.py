from django.core.management.base import BaseCommand, CommandError
import random
from django.core.files import File
from cc.ccapp.models import Post, Category, Circle, ItemForSale
from cc.multiuploader.models import MultiuploaderImage
from cc import settings
from django.db import transaction
from django_facebook.models import *



class Command(BaseCommand):
    args = ''
    help = 'make a fake database [TESTING ONLY]'

    @transaction.commit_manually    
    def handle(self, *args, **options):

        print("Stay calm this is going to take a while.")
        print("Deleting Everything, except users:")

        ItemForSale.objects.all().delete()
        Category.objects.all().delete()
        Circle.objects.all().delete()

        print("Generating new db...")

        cnames = ['Berkeley', 'Oakland', 'SF', 'Richmond', 'Walnut Creek']
        
        unamez = ['Abe','Teddy','George','Tom','Bill']

        cnamez = ['Apparel, Accessories', 'Appliances', 'Books', 'Electronics', 'Furniture', 'Housing', 'Movies, Music, Games', 'Sporting Goods', 'Tickets', 'Other']

        pnames = ['shoes 4 sale', 'rear axle', 'bag of ham', 'speaker system', '24 pack of coke',
                  'dead cat', 'beef jerkey', 'tv set', 'desk n chairs', 'top hat', 'suit and tie',
                  'pencil box', 'backpack', 'jars', 'tickets to the mets game', 'axe deoderant',
                  'laptop', 'tangled wires', 'monster energy drinks', 'concrete mix', 'keyboard',
                  'math 1a textbook', 'chemestry supplies', 'bio 4 book', 'some cereal',
        ]

        num_img = 30
        i=0
        n=0

        for x in cnames: # generate circles
            newc = Circle(name=x, is_public=True, is_city=True, url_key=str(i))
            newc.save()
            i=i+1

        users = User.objects.all()[1:len(User.objects.all())]
        
        print users
        
        if len(users) == 0:

            for x in unamez:
                n=n+1
                dude = User.objects.create_user(x, email=x+'@usa.us', password='1234')
                dude_profile = FacebookProfile(facebook_id = n, user=dude )  
                dude_profile.user_id = n+10
                dude_profile.save()
            users = User.objects.all()[1:len(User.objects.all())]
                
        

        for x in cnamez: # generate categories
            newc = Category(name=x)
            newc.save()

        for k in range(0,355):
            inum = random.randrange(1, num_img+1)

            image = MultiuploaderImage()
            image.filename = str(inum) + '.jpg'
         #   image.image=file  #File(file('/foleer/ham.jpg")
            image.image = File(file(settings.SITE_ROOT + '/test_images/' + image.filename))
           

            image.key_data = image.key_generate



            namenum = random.randrange(0, len(pnames))
            catnum  = random.randrange(0, len(cnamez)) + 1
            cnum    = random.randrange(0, len(cnames)) + 1

            catnum  = Category.objects.get(pk = catnum)
            cnum    = Circle.objects.get(pk = cnum)
            

            p = random.randint(1,100)
            own = users[random.randint(1,len(users))-1]
            nifs = ItemForSale(owner=own,price = p, category = catnum, title = pnames[namenum],
                body = "I've got a "+pnames[namenum]+" for sale, so buy it!", key_data=k)
            nifs.save()
            nifs.circles.add(cnum)
            nifs.save()
            
            image.post = nifs
            image.save()



        transaction.commit()

        for poast in ItemForSale.objects.all():
            x = poast.get_thumbnail_url()

        transaction.commit()
