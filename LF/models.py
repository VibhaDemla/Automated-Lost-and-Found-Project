from django.db import models
import datetime
import os

# Create your models here.
class user_data(models.Model):
	user_email =  models.CharField(max_length = 50,unique = True)
	user_name = models.CharField(max_length = 50)
	user_phone = models.CharField(max_length = 10)
	user_type = models.CharField(max_length = 50,default = "u")

def filepath(request, filename):
    old_filename = filename
    print(old_filename)
    timeNow = datetime.datetime.now().strftime('%Y%m%d%H:%M:%S')
    filename = "%s%s" % (timeNow, old_filename)
    return os.path.join('static/Item_Images/', filename)

class found_items_table(models.Model):
	item_img = models.ImageField(upload_to=filepath, null=False, blank=True , default = "null")	
	item_type = models.CharField(max_length=30 , null=False, blank=True , default = "null")
	date_found = models.DateField(null=False, blank=True , default = "2000-01-01")
	item_status = models.CharField(max_length=30 , null=False, blank=True , default = "unclaimed")
	found_by_id = models.CharField(max_length=30 , null=False, blank=True , default = "null")
	found_by_name = models.CharField(max_length=30 , null=False, blank=True , default = "null")
	found_by_email = models.CharField(max_length=50 , null=False, blank=True , default = "null")
	found_by_contact = models.CharField(max_length=12 , null=False, blank=True , default = "null")

	q1 = models.TextField(null=False, blank=True , default = "null")
	a1 = models.TextField(null=False, blank=True , default = "null")

	q2 = models.TextField(null=False, blank=True , default = "null")
	a2 = models.TextField(null=False, blank=True , default = "null")

	q3 = models.TextField(null=False, blank=True , default = "null")
	a3 = models.TextField(null=False, blank=True , default = "null")

	q4 = models.TextField(null=False, blank=True , default = "null")
	a4 = models.TextField(null=False, blank=True , default = "null")

	q5 = models.TextField(null=False, blank=True , default = "null")
	a5 = models.TextField(null=False, blank=True , default = "null")

	q6 = models.TextField(null=False, blank=True , default = "null")
	a6 = models.TextField(null=False, blank=True , default = "null")

	q7 = models.TextField(null=False, blank=True , default = "null")
	a7 = models.TextField(null=False, blank=True , default = "null")

	q8 = models.TextField(null=False, blank=True , default = "null")
	a8 = models.TextField(null=False, blank=True , default = "null")

	q9 = models.TextField(null=False, blank=True , default = "null")
	a9 = models.TextField(null=False, blank=True , default = "null")

	q10 = models.TextField(null=False, blank=True , default = "null")
	a10 = models.TextField(null=False, blank=True , default = "null")

	description = models.TextField(null=False, blank=True , default = "null")

