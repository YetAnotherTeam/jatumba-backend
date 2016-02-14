from django.db import models


class Profile(models.Model):
    user = models.ForeignKey(
        'auth.User'
    )
    team = models.ManyToManyField(Team)


class Team(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    leader = models.ForeignKey(Profile)


class Instruments(models.Model):
    name = models.CharField(max_length=25)
    players = models.ManyToManyField(Profile)


class Member(models.Model):
    user = models.ForeignKey(Profile)
    team = models.ForeignKey(Team)
    instrument = models.ForeignKey(Instruments)
