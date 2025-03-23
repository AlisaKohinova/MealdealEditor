from django.db import models

# Create your models here.

class InvitationCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    used_by = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {'Used' if self.is_used else 'Available'}"
