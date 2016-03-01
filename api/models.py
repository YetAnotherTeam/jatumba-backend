from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    vk_profile = models.CharField(max_length=30, blank=True, default='')
    fb_profile = models.CharField(max_length=30, blank=True, default='')

    def __str__(self):
        return 'Profile of user: %s' % self.user.username


class Session(models.Model):
    user = models.ForeignKey('auth.User')
    access_token = models.CharField(max_length=32)
    refresh_token = models.CharField(max_length=32)
    time = models.FloatField()

    def __str__(self):
        return 'Token of user: %s' % self.user.username


class Band(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)

    def __str__(self):
        return 'Name: %s; Description: %s;' % (self.name, self.description)


class Instrument(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return 'Instrument name: %s' % self.name


class Member(models.Model):
    user = models.ForeignKey('auth.User')
    band = models.ForeignKey(Band)
    instrument = models.ForeignKey(Instrument)
    is_leader = models.BooleanField()

    def __str__(self):
        return '%s; Band: %s; Instrument: %s; Is leader? %s;' % (
            self.user.username, self.band.name, self.instrument.name, self.is_leader)
