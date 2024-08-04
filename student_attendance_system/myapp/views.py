from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.contrib.auth.models import User
from .models import attendance
# Machine Learning Packages
import numpy as np
import cv2
import os
from PIL import Image
import datetime


# Create your views here.


def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        print(username, first_name, last_name, email, pass1, pass2)
        if pass1 == pass2:
            if User.objects.filter(email=email).exists():
                messages.warning(request, "Email already exist!")
            elif User.objects.filter(username=username).exists():
                messages.warning(request, "Username already exist!")
            else:
                user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                                email=email, password=pass1)
                user.save()
                print("user registered successfully")
                return redirect(add_face)
        else:
            messages.warning(request, "Password does not match!!")
    context = {'form': form}
    return render(request, 'register.html', context)


def signin(request):
    user = None
    last_login.objects.all().delete()
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
        except:
            messages.warning("Fill the details")
        if user is not None:
            login(request, user)
            var = last_login(username=username, password=password)
            var.save()
            return redirect(mark_attendance)

        else:
            messages.info(request, 'Username OR password is incorrect')

    context = {}
    return render(request, 'login.html', context)


def mark_attendance(request):
    return render(request, 'mark_attendance.html')


def add_face(request):
    if not os.path.exists('media_att/images'):
        os.makedirs('media_att/images')

    faceCascade = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    count = 0

    face_detector = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')
    var = User.objects.last()
    face_id = var.id
    face_id = int(face_id)
    while (True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.3, 6)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            count += 1
            # Save the captured image into the images directory
            cv2.imwrite("media_att/images/Users." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y + h, x:x + w])
            cv2.imshow('image', img)
        # Press Escape to end the program.
        k = cv2.waitKey(100) & 0xff
        if k < 50:
            break
        # Take 30 face samples and stop video. You may increase or decrease the number of
        # images. The more the better while training the model.
        elif count >= 50:
            break

    print("\n [INFO] Exiting Program.")
    cam.release()
    cv2.destroyAllWindows()

    return render(request, 'photo.html')


def getImagesAndLabels():
    path = 'media_att/images/'
    detector = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    ids = []
    for imagePath in imagePaths:
        # convert it to grayscale
        PIL_img = Image.open(imagePath).convert('L')
        img_numpy = np.array(PIL_img, 'uint8')
        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)
        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y + h, x:x + w])
            ids.append(id)
    return faceSamples, ids


def create_model(request):
    path = 'media_att/images/'
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    print("\n[INFO] Training faces...")
    faces, ids = getImagesAndLabels()
    recognizer.train(faces, np.array(ids))
    # Save the model into the current directory.
    recognizer.write('data/trainer.yml')
    print("\n[INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))

    return redirect(register)


def loginpage(request):
    var = User.objects.all()
    teacher_subject = request.session.get('teacher_subject', '')
    print(teacher_subject)
    names = []
    names.append(None)
    for i in var:
        names.append(i.id)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    try:
        recognizer.read('data/trainer.yml')
    except:
        return redirect(register)

    face_cascade_Path = "data/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(face_cascade_Path)
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Video Capture
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    # Min Height and Width for the window size to be recognized as a face
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )
        recognized_users = []
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id1, confidence = recognizer.predict(gray[y:y + h, x:x + w])

            if confidence < 70:
                try:
                    name = User.objects.get(id=id1)
                    id = name.username
                    confidence = "  {0}%".format(round(100 - confidence))
                    if id != "Who are you ? Please Register!":
                        recognized_users.append(id)
                        print(recognized_users)
                except:
                    return render(request, 'who.html')
            else:
                id = "Who are you ? Please Register!"
                confidence = "  {0}%".format(round(100 - confidence))

            cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)
        # Escape to exit the webcam / program
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break

        for user_id in recognized_users:
            # person = User.objects.get(username=id)
            if user_id == "Who are you ? Please Register!":
                # Handle the case where the username is not valid (e.g., log a message, skip this user, etc.)
                print("Invalid username:", user_id)
                continue

            try:
                person = User.objects.get(username=user_id)
            except User.DoesNotExist:
                # Handle the case where the user does not exist (e.g., log a message, redirect, etc.)
                print(f"User with username {user_id} does not exist.")
                continue
            print("person", person)
            new = attendance.objects.filter(user=person, date=datetime.datetime.today())
            last_login_usernames = list(last_login.objects.values_list('username', flat=True))
            request.GET = request.GET.copy()
            request.GET['last_login_usernames'] = last_login_usernames
            print(last_login_usernames)
            if len(new) == 0 or id in last_login_usernames:
                existing_attendance = attendance.objects.filter(user=person, subject=teacher_subject,
                                                                date=datetime.datetime.today())
                if not existing_attendance.exists():
                    details = attendance(user=person, subject=teacher_subject, date=datetime.datetime.today(),
                                         Time=datetime.datetime.now().strftime("%H:%M:%S"))
                    details.save()
            else:
                last_attendance = new.order_by('-id').first()
                last_attendance_time = datetime.datetime.combine(datetime.date.today(), last_attendance.Time)
                time_difference = datetime.datetime.now() - last_attendance_time
                if time_difference.total_seconds() >= 300:  # Check if 5 minutes have passed
                    # subjects = ["DC", "CC", "IOT", "SSC"]  # List of subjects
                    subjects_already_inserted = [att.subject for att in new]
                    print(id, request.user.username)
                    print(id == request.user.username)
                    if teacher_subject not in subjects_already_inserted or id in last_login_usernames:
                        existing_attendance = attendance.objects.filter(user=person, subject=teacher_subject,
                                                                        date=datetime.datetime.today())
                        if not existing_attendance.exists():
                            details = attendance(user=person, subject=teacher_subject,
                                                 date=datetime.datetime.today(),
                                                 Time=datetime.datetime.now().strftime("%H:%M:%S"))
                            print(details)
                            details.save()
                            break  # Break after inserting the first subject that is not inserted yet

    cam.release()
    cv2.destroyAllWindows()
    return redirect(teacher_home)


def select_subject(request):
    subjects = Teacher.objects.values_list('subject', flat=True).distinct()
    if request.method == "POST":
        sub = request.POST.get('sub')
        request.session['sub'] = sub
        return redirect(view_attendance)
    return render(request, "select_subject.html", {'subjects': subjects})


def view_attendance(request):
    sub = request.session.get('sub')
    user = User.objects.get(id=request.user.id)
    attend = attendance.objects.filter(subject=sub, user=user)
    print(attend)
    return render(request, 'attendance.html', {'attend': attend, "sub": sub})


def logoutUser(request):
    logout(request)
    return redirect(first_portal)


def teacher_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        first_name = first_name.capitalize()
        last_name = request.POST.get('last_name')
        last_name = last_name.capitalize()
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')
        subject = request.POST.get('subject')
        subject = subject.upper()
        print(username, first_name, last_name, email, pass1, pass2, subject)
        if pass1 == pass2:
            if Teacher.objects.filter(email=email).exists():
                messages.warning(request, "Email already exist!")
            elif Teacher.objects.filter(username=username).exists():
                messages.warning(request, "Username already exist!")
            else:
                teacher = Teacher.objects.create(username=username, first_name=first_name, last_name=last_name,
                                                 email=email, password=pass1, subject=subject)
                teacher.save()
                request.session['teacher_id'] = username
                print("teacher registered successfully")
                return redirect(teacher_login)
    return render(request, 'teacher_register.html')


def teacher_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)
        if Teacher.objects.filter(username=username, password=password).exists():
            teacher = Teacher.objects.get(username=username, password=password)
            request.session['teacher_id'] = username
            request.session['teacher_subject'] = teacher.subject
            print("teacher login successfully")
            return redirect(teacher_home)

    return render(request, 'teacher_login.html')


def first_portal(request):
    return render(request, 'first_portal.html')


def teacher_home(request):
    return render(request, 'teacher_home.html')


def logoutTeacher(request):
    logout(request)
    return redirect(first_portal)


def teacher_view_attendance(request):
    teacher_id = request.session.get('teacher_id')
    print(teacher_id)
    teacher = Teacher.objects.get(username=teacher_id)
    sub = teacher.subject
    attendance_records = attendance.objects.filter(subject=teacher.subject)
    return render(request, 'teacher_view_attendance.html', {'attend': attendance_records, "sub": sub})
