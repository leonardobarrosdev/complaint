from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext as _
from django.core.validators import RegexValidator
from datetime import datetime


class Profile(models.Model):
    COLLEGE = ((1, _('Federal Institute')), (2, _('FASF')), (3, _('Harverd')))
    TYPE_USER = (('student', _('student')),('grievance', _('grievance')))
    CB = (
        (1, _("Information Technology")),
        (2, _("Computer Science")),
        (3, _("Information Science")),
        (4, _("Electronics and Communication")),
        (5, _("Mechanical"))
    )
    PHONE_REGEX=RegexValidator(regex=r'^\d{10,10}$', message=_("Phone number must be entered in the format:Up to 10 digits allowed."))
    user=models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    company=models.SmallIntegerField(choices=COLLEGE, default=1)
    phone=models.CharField(validators=[PHONE_REGEX], max_length=10, blank=True)
    type_user=models.CharField(choices=TYPE_USER, max_length=20, default='student')
    branch=models.SmallIntegerField(choices=CB, default=1)

    def __str__(self):
        return self.user.username
    

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Complaint(models.Model):
    STATUS = ((1, _('Solved')), (2,  _('InProgress')), (3, _('Pending')))
    TYPE = (
        ('ClassRoom', _("Class Room")),
        ('Teacher', _("Teacher")),
        ('Management', _("Management")),
        ('College', _("College")),
        ('Other', _("Other"))
    )
    subject=models.CharField(max_length=200, blank=False, null=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    type_of_complaint=models.CharField(choices=TYPE, null=True, max_length=200)
    description=models.TextField(max_length=4000, blank=False, null=True)
    time=models.DateField(auto_now=True)
    status=models.IntegerField(choices=STATUS, default=3)
    
   
    def __init__(self, *args, **kwargs):
        super(Complaint, self).__init__(*args, **kwargs)
        self.__status = self.status

    def save(self, *args, **kwargs):
        if self.status and not self.__status:
            self.active_from = datetime.now()
        super(Complaint, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.get_type_of_complaint_display()


class Grievance(models.Model):
    complainer=models.OneToOneField(User,on_delete=models.CASCADE,default=None)

    def __str__(self):
        return self.complainer