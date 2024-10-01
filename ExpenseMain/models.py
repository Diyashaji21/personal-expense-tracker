from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

# Create your models here.
class UserDetail(models.Model):
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=100)

#     class Meta:
#         verbose_name_plural = "UserDetails"

    def __str__(self):
        return self.name
    

class UserPreference(models.Model):
    user=models.OneToOneField(to=UserDetail,on_delete=models.CASCADE)
    currency=models.CharField(max_length=255,blank=True,null=True)

    def __str__(self):
        return str(self.user)+"'s"+' preferences'
    

class Expense(models.Model):
    amount=models.FloatField()
    date = models.DateField(null=True, blank=True)
    description=models.TextField()
    owner=models.ForeignKey(to=UserDetail,on_delete=models.CASCADE)
    category=models.CharField(max_length=266)

    class Meta:
        ordering=['-date']

    def __str__(self):
        return self.category


# class Category(models.Model):
#     name=models.CharField(max_length=255)

#     class Meta:
#         verbose_name_plural="Categories"

#     def __str__(self):
#         return self.name
    

class Income(models.Model):
    amount=models.FloatField()
    date = models.DateField(null=True, blank=True)
    description=models.TextField()
    owner=models.ForeignKey(to=UserDetail,on_delete=models.CASCADE)
    source=models.CharField(max_length=266)

    class Meta:
        ordering=['-date']

    def __str__(self):
        return self.source
    

# class Source(models.Model):
#     name=models.CharField(max_length=255)

#     def __str__(self):
#         return self.name
