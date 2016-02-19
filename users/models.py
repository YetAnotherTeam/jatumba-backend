from django.db import models


class Team(models.Model):
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
    team = models.ForeignKey(Team)
    instrument = models.ForeignKey(Instrument)
    is_leader = models.BooleanField()

    def __str__(self):
        return '%s; Team: %s; Instrument: %s; Is leader? %s;' % (
            self.user.username, self.team.name, self.instrument.name, self.is_leader)
