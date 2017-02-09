import csv
import requests
import sys

#collect info about group creation
file_name = raw_input('What is the name of the file with group info (include extension): ') #indicate what source file you are using
course_id = raw_input('What is the Cancvas Course ID: ') #indicate the course ID
group_set_name = raw_input('What do you want to call the Group Set: ')
access_token = "" #enter your access_token between quotes
canvas_url = "" #enter your canvas URL here including https://, no trailing /

#this section helps later in using sis_login_id rather than canvas_id
get_users_url=canvas_url+"/api/v1/courses/"+course_id+"/users"
student_list = requests.get(get_users_url,data={'access_token':access_token}) #get first page of students
student_list_raw=[]
for item in student_list.json():
	student_list_raw.append(item)
while student_list.links['current']['url'] != student_list.links['last']['url']:   #get remaining pages and add to a list
	get_users_url = student_list.links['next']['url']
	student_list = requests.get(get_users_url,data={'access_token':access_token})
	for item in student_list.json():
		student_list_raw.append(item)
id_dict={}
for student in student_list_raw: #create dictionary to help translate sis_login_id to canvas_id
	try:
		id_dict[student['sis_login_id']] = student['id']
	except KeyError:
		print "User does not have SIS Login ID: "+str(student['id'])

#group creations/user additions
with open(file_name,'rb') as f:
	curr_group=""
	reader = csv.reader(f)
	#create group set
	url=canvas_url+"/api/v1/courses/"+str(course_id)+"/group_categories?access_token="+access_token
	new_group_set = requests.post(url, data={'name':str(group_set_name)})
	new_group_set=new_group_set.json()
	group_set_id=new_group_set['id']
	#read from csv file to create groups and add users to groups
	for row in reader:
		sis_login_id=str(row[1])
		student_canvas_id = id_dict[sis_login_id]
		if(row[0]!=curr_group): #decides whether group rename needs to be done (only once per group)
			curr_group=str(row[0])
			url2 = canvas_url+"/api/v1/group_categories/"+str(group_set_id)+"/groups?access_token="+access_token
			created_group = requests.post(url2,data={'name':curr_group}) #add group
			created_group_id = created_group.json()['id']
			url3 = canvas_url+"/api/v1/groups/"+str(created_group_id)+"/memberships"+"?access_token="+access_token
			requests.post(url3,data={'user_id':student_canvas_id}) #add student to current group
		else:
			requests.post(url3,data={'user_id':student_canvas_id}) #add student to current group
