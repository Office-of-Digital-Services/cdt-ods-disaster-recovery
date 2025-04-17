from uuid import uuid4

from django.db import models
from django_fsm import FSMField, transition

from cdt_identity.models import IdentityGatewayConfig, ClaimsVerificationRequest


class UserFlow(models.Model):
    """Represents a user journey through the Disaster Recovery app."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
    )
    system_name = models.SlugField(
        help_text="Internal system name for this flow.",
        unique=True,
    )
    oauth_config = models.ForeignKey(
        IdentityGatewayConfig,
        on_delete=models.PROTECT,
        help_text="The IdG connection details for this flow.",
    )
    claims_request = models.ForeignKey(
        ClaimsVerificationRequest,
        on_delete=models.PROTECT,
        help_text="The claims request details for this flow.",
    )


class VitalRecordsRequest(models.Model):
    STATUS_CHOICES = [
        ("started", "Started"),
        ("eligibility_completed", "Eligibility Completed"),
        ("submitted", "Request Submitted"),
    ]

    FIRE_CHOICES = [("palisades", "Palisades fire"), ("eaton", "Eaton fire")]

    status = FSMField(default="started", choices=STATUS_CHOICES)
    fire = models.CharField(max_length=50, choices=FIRE_CHOICES)

    # Transitions from state to state
    @transition(field=status, target="eligibility_completed")
    def complete_eligibility(self):
        pass
