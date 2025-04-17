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
        ("sworn_statement_completed", "Sworn Statement Completed"),
        ("name_completed", "Name Completed"),
        ("submitted", "Request Submitted"),
    ]

    FIRE_CHOICES = [("palisades", "Palisades fire"), ("eaton", "Eaton fire")]

    RELATIONSHIP_CHOICES = [
        ("self", "Self"),
        ("parent", "Parent"),
        ("legal guardian", "Legal guardian"),
        ("child", "Child"),
        ("grandparent", "Grandparent"),
        ("grandchild", "Grandchild"),
        ("sibling", "Sibling"),
        ("spouse", "Spouse"),
        ("domestic_partner", "Domestic partner"),
    ]

    status = FSMField(default="started", choices=STATUS_CHOICES)
    fire = models.CharField(max_length=50, choices=FIRE_CHOICES, blank=True)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES, blank=True)
    legal_attestation = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    # Transitions from state to state
    @transition(field=status, target="eligibility_completed")
    def complete_eligibility(self):
        pass

    @transition(field=status, target="sworn_statement_completed")
    def complete_statement(self):
        pass

    @transition(field=status, target="name_completed")
    def complete_name(self):
        pass
