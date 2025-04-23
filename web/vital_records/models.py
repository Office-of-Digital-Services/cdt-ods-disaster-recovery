from uuid import uuid4

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition


class VitalRecordsRequest(models.Model):
    """Represents a request to order a vital record through the Disaster Recovery app."""

    STATUS_CHOICES = [
        ("started", "Started"),
        ("eligibility_completed", "Eligibility Completed"),
        ("statement_completed", "Sworn Statement Completed"),
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

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    status = FSMField(default="started", choices=STATUS_CHOICES)
    fire = models.CharField(max_length=50, choices=FIRE_CHOICES)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)
    legal_attestation = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    submitted_at = models.DateTimeField(null=True, blank=True)

    # Transitions from state to state
    @transition(field=status, source="*", target="eligibility_completed")
    def complete_eligibility(self):
        pass

    @transition(field=status, target="statement_completed")
    def complete_statement(self):
        pass

    @transition(field=status, target="name_completed")
    def complete_name(self):
        pass

    @transition(field=status, source="name_completed", target="submitted")
    def complete_submit(self):
        self.submitted_at = timezone.now()
