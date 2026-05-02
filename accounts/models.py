from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    streak_days = models.PositiveIntegerField(default=0)
    total_xp = models.PositiveIntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class StudySession(models.Model):
    SCRIPT_CHOICES = [
        ('hiragana', 'Hiragana'),
        ('katakana', 'Katakana'),
        ('kana', 'Hiragana + Katakana'),
        ('kanji', 'Kanji'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    script = models.CharField(max_length=20, choices=SCRIPT_CHOICES)
    correct = models.PositiveIntegerField(default=0)
    incorrect = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    mode = models.CharField(max_length=20, default='normal')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.script} - {self.created_at.date()}"


class CharacterProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    script = models.CharField(max_length=20)
    character = models.CharField(max_length=10)
    romanji = models.CharField(max_length=20)
    correct_count = models.PositiveIntegerField(default=0)
    incorrect_count = models.PositiveIntegerField(default=0)
    mastered = models.BooleanField(default=False)
    ease_factor = models.FloatField(default=2.5)
    interval = models.PositiveIntegerField(default=1)
    next_review = models.DateField(null=True, blank=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'script', 'character')

    def __str__(self):
        return f"{self.user.username} - {self.character} ({self.script})"


class Achievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    key = models.CharField(max_length=50)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'key')

    def __str__(self):
        return f"{self.user.username} - {self.key}"