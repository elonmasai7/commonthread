from django.db import models
from .models import CustomUser, Project, Skill

def find_matches(user):
    # Get skills needed by the user's created projects
    needed_skills = Skill.objects.filter(
        project__creator=user
    ).distinct()

    # Get users with shared interests
    base_query = CustomUser.objects.filter(
        interests__in=user.interests.all()
    ).exclude(id=user.id).distinct()

    # Annotate with matching scores
    matches = base_query.annotate(
        shared_interests_count=models.Count(
            'interests',
            filter=models.Q(interests__in=user.interests.all())
        ),
        skill_complementarity=models.Count(
            'skills',
            filter=models.Q(skills__in=needed_skills)
        )
    ).order_by(
        '-shared_interests_count',
        '-skill_complementarity'
    ).select_related('profile').prefetch_related('skills', 'interests')

    return matches