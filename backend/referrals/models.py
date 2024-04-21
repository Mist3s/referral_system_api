from django.db import models
from django.core.exceptions import ValidationError

from users.models import User


class Referral(models.Model):
    user = models.ForeignKey(
        User,
        related_name='referrals',
        on_delete=models.CASCADE,
        verbose_name='user'
    )
    referral = models.OneToOneField(
        User,
        related_name='referral',
        on_delete=models.CASCADE,
        verbose_name='Referral',
        unique=True
    )

    class Meta:
        ordering = ('user', '-id')
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'

    def clean(self):
        if self.user == self.referral:
            raise ValidationError(
                "The user and referral cannot be the same person."
            )

    def __str__(self):
        return f'{self.referral} реферал {self.user}'
