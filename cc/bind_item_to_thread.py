from ccapp.views import *
from ccapp.models import *

#binds items to a thread's foreign key
def bind_item_to_thread():
  threads = Thread.objects.all()
  for thread in threads:
    if thread.post_deleted is False:
      ifs = ItemForSale.objects.get(id=thread.post_id)
      thread.item = ifs
      thread.save()
