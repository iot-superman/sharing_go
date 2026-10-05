from django.db import models
class Profile(models.Model):
    client_id=models.CharField(max_length=64,unique=True)
    nickname=models.CharField(max_length=80)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    def __str__(self): return self.nickname
class Ride(models.Model):
    MODE_CHOICES=[('taxi','計程車'),('drive','自駕')]
    STATUS_CHOICES=[('open','募集中'),('full','已額滿'),('cancelled','已取消'),('finished','已完成')]
    owner=models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='owned_rides')
    mode=models.CharField(max_length=10,choices=MODE_CHOICES,default='taxi')
    status=models.CharField(max_length=12,choices=STATUS_CHOICES,default='open')
    ride_date=models.DateField(); ride_time=models.TimeField(); max_people=models.PositiveSmallIntegerField(default=3)
    meeting_name=models.CharField(max_length=160); meeting_lat=models.FloatField(null=True,blank=True); meeting_lng=models.FloatField(null=True,blank=True)
    destination_name=models.CharField(max_length=160); destination_lat=models.FloatField(null=True,blank=True); destination_lng=models.FloatField(null=True,blank=True)
    estimated_total=models.PositiveIntegerField(default=120); price_per_person=models.PositiveIntegerField(default=0)
    plate=models.CharField(max_length=20,blank=True); vehicle=models.CharField(max_length=80,blank=True); note=models.TextField(blank=True); locked=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    members=models.ManyToManyField(Profile,through='RideMember',related_name='rides')
    class Meta: ordering=['-created_at']
class RideMember(models.Model):
    ride=models.ForeignKey(Ride,on_delete=models.CASCADE); profile=models.ForeignKey(Profile,on_delete=models.CASCADE)
    role=models.CharField(max_length=10,default='member'); joined_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['ride','profile'],name='uniq_ride_member')]
class Message(models.Model):
    ride=models.ForeignKey(Ride,on_delete=models.CASCADE,related_name='messages'); sender=models.ForeignKey(Profile,on_delete=models.CASCADE)
    text=models.CharField(max_length=1000); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['created_at']
class Location(models.Model):
    ride=models.ForeignKey(Ride,on_delete=models.CASCADE,related_name='locations'); profile=models.ForeignKey(Profile,on_delete=models.CASCADE)
    lat=models.FloatField(); lng=models.FloatField(); accuracy=models.FloatField(null=True,blank=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['ride','profile'],name='uniq_ride_location')]
