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
    STARTED = "started"
    ELIGIBILITY_COMPLETED = "eligibility_completed"
    SWORN_STATEMENT_COMPLETED = "sworn_statement_completed"
    SUBMITTED = "submitted"

    STATUS_CHOICES = [
        (STARTED, "Started"),
        (ELIGIBILITY_COMPLETED, "Eligibility Completed"),
        (SWORN_STATEMENT_COMPLETED, "Sworn Statement Completed"),
        (SUBMITTED, "Request Submitted"),
    ]

    PALISADES_FIRE = "palisades"
    EATON_FIRE = "eaton"

    FIRE_CHOICES = [(PALISADES_FIRE, "Palisades fire"), (EATON_FIRE, "Eaton fire")]

    status = FSMField(default=STARTED, choices=STATUS_CHOICES)
    fire = models.CharField(max_length=50, choices=FIRE_CHOICES)

    # Transitions from state to state
    @transition(field=status, target=ELIGIBILITY_COMPLETED)
    def complete_eligibility(self):
        # User arrives at Elig form
        # Completes Elig form
        # Redirected to Sworn Statement form
        pass
