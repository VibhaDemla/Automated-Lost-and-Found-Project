from django.shortcuts import redirect , render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template import Context, Template , loader
from django.views.decorators.cache import cache_control
from django.http import JsonResponse

from LF.models import user_data,found_items_table

import ultralytics
from ultralytics import YOLO
import os
import cv2
import ultralytics
from ultralytics import YOLO
import numpy as np

import datetime
from datetime import datetime

#import webcolors
#from colorthief import ColorThief
#from sentence_transformers import SentenceTransformer, util

g_img_src = None
g_items = ["ID Card" , "Laptop" , "Keys" , "Mobile Phone" , "Tablet" , "Charger" , "Backpack" , "Bottle" , "Wallet" , "Money" , "Debit/Credit Card" , "Earphones" , "Eyewear" , "Apparels" , "Jewellery" , "Watch" , "Other"]

g_item_att = {
		"ID Card" : ["Location The Item Was Lost/Found" , "Name" , "Roll Number"] , 
		"Laptop" : ["Location The Item Was Lost/Found" ,"Item Color" , "Password Protected?" , "Laptop Brand Name" , "Laptop Processor" , "Welcome Screen User Name" , "Serial Number" , "Identity Mark"] , 
		"Keys" : ["Location The Item Was Lost/Found" ,"Text On Key" , "Item Color" , "Number of Keys"] ,
		"Mobile" : ["Location The Item Was Lost/Found" ,"Password Protected?" , "Item Color" , "Mobile Brand Name" , "SIM Card Operator Name" , "Back Cover Color" , "Serial Number" , "Identity Mark" ],
		"Tablet" : ["Location The Item Was Lost/Found" , "Item Color" ,"Password Protected?" , "Brand Name" , "SIM Card Operator Name" , "Back Cover Color" , "Serial Number" , "Identity Mark" ],
		"Charger":["Location The Item Was Lost/Found" , "Item Color" ,"Brand Name" , "Charger Type" ],
		"Backpack":["Location The Item Was Lost/Found" , "Item Color" ,"Brand Name" , "Number of Items" ],
		"Bottle":["Location The Item Was Lost/Found" , "Item Color" ,"Brand Name"],
		"Wallet":["Location The Item Was Lost/Found" , "Item Color" ,"Estimated Amount","Name On Any Debit Card"],
		"Money":["Location The Item Was Lost/Found","Exact Amount"],
		"Debit/Credit Card":["Location The Item Was Lost/Found" , "Item Color" ,"Bank Name","Card Holder's Name","Card Number","CVV"],
		"Earphones":["Location The Item Was Lost/Found" , "Item Color" ,"Connector Type"],
		"Eyewear":["Location The Item Was Lost/Found" , "Item Color" ,"Eye Wear Type","Brand Name"],
		"Apparels":["Location The Item Was Lost/Found" , "Item Color" ,"Apparel Type","Brand Name","Size"],
		"Jewellery":["Location The Item Was Lost/Found" , "Item Color" ,"Jewellery Type","Jewellery Material"],
		"Watch":["Location The Item Was Lost/Found" , "Item Color" ,"Watch Type" , "Brand Name" , "Strap Material"],
		"Other":["Location The Item Was Lost/Found" , "Color" ,"Question 1" , "Question 2" ,"Question 3" ,"Question 4","Question 5"]
		}

# Create your views here.


def home(request):
	return render(request,"LF/signin.html")

def signup(request):

	if request.method == "POST":

		email = request.POST['email']
		name = request.POST['name']
		phone = request.POST['phone']
		pass1 = request.POST['pass1']
		pass2 = request.POST['pass2']

		if User.objects.filter(email = email).exists():
			messages.error(request , 'This Email-ID is already registered!')
			return redirect('signup')

		if(len(pass1) < 2):
			messages.error(request , 'Password must be of atleast 8 characters!')
			return redirect('signup')

		if(pass1 != pass2):
			messages.error(request , "Password did not match!")	
			return redirect('signup')

		else:
			myUser = User.objects.create_user(email , email , pass1)
			myUser.first_name = name

			myUser.save()

			ins = user_data(user_email = email , user_name = name , user_phone = "7903758386" )
			ins.save()

			messages.success(request , "Account Created Successfully!")
			return render(request , "LF/signin.html")
				

		return redirect('signup')


	return render(request,"LF/signup.html")

def signin(request):
	if request.method == "POST":

		email = request.POST['email']
		pass1 = request.POST['pass1']

		user = authenticate(request , username = email , password = pass1)
		if user is not None:
			login(request,user)

			contact = user_data.objects.filter(user_email=email).first()
			phone = contact.user_phone

			request.session['view_data'] = {
				"user_id" : user.id,
				"user_name" : user.first_name,
				"user_email" : user.username,
				"user_phone" : phone,
				"item_type" : "Laptop",
				"item_color" : "Black",
				"item_ques" : None,
				"item_id" : None,
			}
			request.session.modified = True
			
			print(request.session.get('view_data')["user_name"])
			return redirect("userDashboard")
			
			
			
		else:
			messages.error(request , "Invalid Credentials!")	
			return redirect('signin')

	return render(request,"LF/signin.html")

def signout(request):
	logout(request)
	return render(request,"LF/signin.html")			

def userDashboard(request):
	return render(request,"LF/userDashboard.html")	

def notifications(request):
	return render(request,"LF/userDashboard.html")

def uploadImage(request):
	if request.method == "POST" and request.FILES.get('img'):
		ins = found_items_table()

		if(len(request.FILES) == 1):
			ins.item_img = request.FILES['img']

			ins.save()

			request.session['view_data']['item_id'] = ins.id
			request.session.modified = True

			print(ins.item_img , ins.id)

			global g_img_src
			g_img_src = str(ins.item_img)
			print(g_img_src)
			#Load the image and the object detection model	image = cv2.imread(g_img_src)
			image = cv2.imread(g_img_src)

			model1 = YOLO("my_Models/yolov8x.pt")
			model2 = YOLO("my_Models/yolov8l.pt")
			model3 = YOLO("my_Models/yolov8s.pt")

			# Perform object detection on the image
			results = model1(image,verbose=False)
			obj = []
			conf = 0

			for result in results:
					if(boxes := result.boxes.cpu().numpy()):
						if(boxes[0].cls != None):
							obj.append(int(boxes[0].cls))
							conf = conf + round(float(boxes[0].conf),2)
							#print(model1.names[int(boxes[0].cls)] , round(float(boxes[0].conf),2))


			# Perform object detection on the image
			results = model2(image,verbose=False)

			for result in results:
				if(boxes := result.boxes.cpu().numpy()):
					if(boxes[0].cls != None):
						obj.append(int(boxes[0].cls))
						conf = conf + round(float(boxes[0].conf),2)
						#print(model2.names[int(boxes[0].cls)] , round(float(boxes[0].conf),2))


			# Perform object detection on the image
			results = model3(image,verbose=False)

			for result in results:
				if(boxes := result.boxes.cpu().numpy()):
					if(boxes[0].cls != None):
						obj.append(int(boxes[0].cls))
						conf = conf + round(float(boxes[0].conf),2)
						#print(model3.names[int(boxes[0].cls)] , round(float(boxes[0].conf),2))    


			if(obj != []):
				res = max(set(obj), key = obj.count)
				item_type = str(model1.names[res].capitalize())
			
				context = {
			    'iname': item_type,
			  	}

				color_thief = ColorThief(g_img_src)
				# get the dominant color
				rgb_triplet = color_thief.get_color(quality=1)
				#print(dominant_color)

				min_colours = {}
				for key, name in webcolors.CSS21_HEX_TO_NAMES.items():
					r_c, g_c, b_c = webcolors.hex_to_rgb(key)
					rd = (r_c - rgb_triplet[0]) ** 2
					gd = (g_c - rgb_triplet[1]) ** 2
					bd = (b_c - rgb_triplet[2]) ** 2
					min_colours[(rd + gd + bd)] = name

				request.session['view_data']['item_color'] = str(min_colours[min(min_colours.keys())].capitalize())
				request.session.modified = True

				#return HttpResponse(template.render(context, request))

				return JsonResponse({'redirect_url': 'item_type' , 'context' : context})
				
				#print(model1.names[res] , round((conf/3),4)*100) 

			else:
				context = {
			    'iname': "Other",
			  	}
				return JsonResponse({'redirect_url': 'item_type' , 'context' : context})

				print("Could Not Detect!")


			return redirect("predictObject")
			

		else:
			return JsonResponse({'error': 'No image file uploaded'}, status=400)
			messages.error(request , "Please select atleast 1 image!")
		
		
		#return redirect('predictObject')	
	
	return render(request,"LF/uploadImage.html")

#context = { 'status' : "True"}
#return render(request , 'LF/userDashboard.html' , context)
'''template = loader.get_template('LF/predictObject.html')
				context = {
			    'iname': model1.names[res].capitalize(),
			  	}'''
				#return HttpResponse(template.render(context, request))

def item_type(request):
	context = request.GET.get('context', None)
	if context:
		context = eval(context)  # Convert the string to a dictionary
	else:
		context = {}
    
	request.session['view_data']['item_color'] = str("Black")
	request.session.modified = True
	return render(request, 'LF/predictObject.html', context)

def getItemType(request):
	if request.method == "POST":

		item_type = str(request.POST['object'])
		request.session['view_data']['item_type'] = item_type
		request.session.modified = True

		item_color = request.session.get('view_data')["item_color"]

		print(item_color)
		
		global g_item_att
		questions = g_item_att[item_type]
		request.session['view_data']['item_ques'] = questions
		request.session.modified = True

		context = {'item_type':item_type , 'item_color' : item_color , 'item_questions' : questions}
		return render(request, 'LF/getItemDetails.html', context)

	return render(request, 'LF/getItemDetails.html')	



def submitItemDetails(request):
	if request.method == "POST": 
		user_id = request.session.get('view_data')['user_id']
		user_email = request.session.get('view_data')['user_email']
		user_name = request.session.get('view_data')['user_name']
		user_phone = request.session.get('view_data')['user_phone']

		item_type = request.session.get('view_data')['item_type']
		item_id = request.session.get('view_data')['item_id']
		date_found = request.POST["Date Lost/Found"]

		questions = request.session.get('view_data')['item_ques']

		q_list = ["null","null","null","null","null","null","null","null","null","null",]
		answers = ["null","null","null","null","null","null","null","null","null","null",]

		for i,question in enumerate(questions):
			q_list[i] = question
			answers[i] = request.POST[question]

		print(q_list)
		print(answers)	

		found_items_table.objects.filter(id=item_id).update(item_type=item_type)
		found_items_table.objects.filter(id=item_id).update(found_by_id=user_id)
		found_items_table.objects.filter(id=item_id).update(found_by_name=user_name)
		found_items_table.objects.filter(id=item_id).update(found_by_email=user_email)
		found_items_table.objects.filter(id=item_id).update(found_by_contact=user_phone)
		found_items_table.objects.filter(id=item_id).update(date_found=date_found)

		found_items_table.objects.filter(id=item_id).update(q1=q_list[0],a1=answers[0],q2=q_list[1],a2=answers[1],q3=q_list[2],a3=answers[2],q4=q_list[3],a4=answers[3],q5=q_list[4],a5=answers[4],q6=q_list[5],a6=answers[5],q7=q_list[6],a7=answers[6],q8=q_list[7],a8=answers[7],q9=q_list[8],a9=answers[8],q10=q_list[9],a10=answers[9])
		
		g_item_att = {
		"ID Card" : ["Location The Item Was Lost/Found" , "Name" , "Roll Number"] , 
		"Laptop" : ["Location The Item Was Lost/Found" ,"Item Color" , "Password Protected?" , "Laptop Brand Name" , "Laptop Processor" , "Welcome Screen User Name" , "Serial Number" , "Identity Mark"] , 
		"Keys" : ["Location The Item Was Lost/Found" ,"Text On Key" , "Item Color" , "Number of Keys"] ,
		"Mobile" : ["Location The Item Was Lost/Found" ,"Password Protected?" , "Item Color" , "Mobile Brand Name" , "SIM Card Operator Name" , "Back Cover Color" , "IMEI Number" , "Identity Mark" ],
		"Tablet" : ["Location The Item Was Lost/Found" , "Item Color" ,"Password Protected?" , "Brand Name" , "SIM Card Operator Name" , "Back Cover Color" , "Serial Number" , "Identity Mark" ],
		"Charger":["Location The Item Was Lost/Found" , "Item Color" ,"Brand Name" , "Charger Type" ],
		"Backpack":["Location The Item Was Lost/Found" , "Item Color" ,"Brand Name" , "Number of Items" ],
		"Wallet":["Location The Item Was Lost/Found" , "Item Color" ,"Estimated Amount","Name On Any Debit Card"],
		"Money":["Location The Item Was Lost/Found","Exact Amount"],
		"Debit/Credit Card":["Location The Item Was Lost/Found" , "Item Color" ,"Bank Name","Card Holder's Name","Card Number","CVV"],
		"Earphones":["Location The Item Was Lost/Found" , "Item Color" ,"Connector Type"],
		"Eyewear":["Location The Item Was Lost/Found" , "Item Color" ,"Eye Wear Type","Brand Name"],
		"Apparels":["Location The Item Was Lost/Found" , "Item Color" ,"Apparel Type","Brand Name","Size"],
		"Jewellery":["Location The Item Was Lost/Found" , "Item Color" ,"Jewellery Type","Jewellery Material"],
		"Watch":["Location The Item Was Lost/Found" , "Item Color" ,"Watch Type" , "Brand Name" , "Strap Material"],
		"Other":["Location The Item Was Lost/Found" , "Color" ,"Question 1" , "Question 2" ,"Question 3" ,"Question 4","Question 5"]
		}

		description = " "
		if item_type == "ID Card":
			description = f"I lost my {item_type} near {answers[0]} , with name {answers[1]} and roll number {answers[2]}."

		if item_type == "Laptop":
			description = f"I lost my {answers[1]} {answers[3]} {item_type} near {answers[0]}.It had a {answers[7]} on it"

		if item_type == "Mobile":
			description = f"I lost my {answers[2]} {answers[3]} {item_type} phone near {answers[0]} with a {answers[5]} backcover."	
	
		found_items_table.objects.filter(id=item_id).update(description=description)

		messages.success(request , "The post has been created successfully!")
		return redirect('userDashboard')
	
	return redirect('userDashboard')

def findItem(request):
	if request.method == "POST":
		item_type = request.POST['item_type']
		userDescription = request.POST['description']
		date_lost = request.POST['date_lost']

		if(item_type not in g_items):
			itemDescriptions = found_items_table.objects.values_list('id', 'description' , 'date_found')
		else:	
			itemDescriptions = found_items_table.objects.filter(item_type = item_type).values_list('id', 'description' , 'date_found')
		
		if(len(itemDescriptions) == 0):
			print("No element")

		topMatches = getMatches(userDescription , itemDescriptions , date_lost)
		print(topMatches)

		idList = []
		for match in topMatches:
			idList.append(match[0])

		print(idList)	

		items = found_items_table.objects.filter(id__in = idList).values('id' , 'item_type' , 'item_img' , 'date_found' , 'a1')
		print(items)

		context = {'items': items}
		return render(request,"LF/topMatches.html" , context)

	return render(request , 'LF/findItem.html')	

def getMatches(userDescription , itemDescriptions , date_lost):	

	model = SentenceTransformer('all-MiniLM-L6-v2')	

	embedding_user_description = model.encode(userDescription, convert_to_tensor=True)

	date_lost = datetime.strptime(date_lost, '%Y-%m-%d').date()

	matchScores = []

	for description in itemDescriptions:
		if(date_lost <= description[2]):
			cosine_similarity = util.cos_sim(embedding_user_description, model.encode(description[1], convert_to_tensor=True))
			matchScores.append([description[0] , cosine_similarity.item()])

	sortedScores = sorted(matchScores, key=lambda x: x[1] , reverse = True)
	return list(sortedScores[0:3])

def topMatches(request):
	if request.method == "POST":
		pass

	return render(request , 'LF/topMatches.html')