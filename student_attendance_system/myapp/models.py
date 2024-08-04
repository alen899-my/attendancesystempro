from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import User
# Create your models here.


class last_login(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.username


class attendance(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    date = models.DateField()
    Time = models.TimeField()

    def __str__(self):
        return str(self.user)+ " " + str(self.date)+ " "+str(self.Time)


class Teacher(models.Model):
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)



