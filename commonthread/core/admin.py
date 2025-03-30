from django.contrib import admin
from .models import *

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'location')

admin.site.register([
    Interest,
    Skill,
    Project,
    CommunityChallenge,
    ChallengeParticipation,
    DiscussionThread
])