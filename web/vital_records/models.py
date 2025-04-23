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
        ("county_completed", "County Completed"),
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

    COUNTY_CHOICES = [
        ("", "Select county"),
        ("01", "Alameda"),
        ("02", "Alpine"),
        ("03", "Amador"),
        ("04", "Butte"),
        ("05", "Calaveras"),
        ("06", "Colusa"),
        ("07", "Contra Costa"),
        ("08", "Del Norte"),
        ("09", "El Dorado"),
        ("10", "Fresno"),
        ("11", "Glenn"),
        ("12", "Humboldt"),
        ("13", "Imperial"),
        ("14", "Inyo"),
        ("15", "Kern"),
        ("16", "Kings"),
        ("17", "Lake"),
        ("18", "Lassen"),
        ("19", "Los Angeles"),
        ("20", "Madera"),
        ("21", "Marin"),
        ("22", "Mariposa"),
        ("23", "Mendocino"),
        ("24", "Merced"),
        ("25", "Modoc"),
        ("26", "Mono"),
        ("27", "Monterey"),
        ("28", "Napa"),
        ("29", "Nevada"),
        ("30", "Orange"),
        ("31", "Placer"),
        ("32", "Plumas"),
        ("33", "Riverside"),
        ("34", "Sacramento"),
        ("35", "San Benito"),
        ("36", "San Bernardino"),
        ("37", "San Diego"),
        ("38", "San Francisco"),
        ("39", "San Joaquin"),
        ("40", "San Luis Obispo"),
        ("41", "San Mateo"),
        ("42", "Santa Barbara"),
        ("43", "Santa Clara"),
        ("44", "Santa Cruz"),
        ("45", "Shasta"),
        ("46", "Sierra"),
        ("47", "Siskiyou"),
        ("48", "Solano"),
        ("49", "Sonoma"),
        ("50", "Stanislaus"),
        ("51", "Sutter"),
        ("52", "Tehama"),
        ("53", "Trinity"),
        ("54", "Tulare"),
        ("55", "Tuolumne"),
        ("56", "Ventura"),
        ("57", "Yolo"),
        ("58", "Yuba"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    status = FSMField(default="started", choices=STATUS_CHOICES)
    fire = models.CharField(max_length=50, choices=FIRE_CHOICES)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)
    legal_attestation = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    county_of_birth = models.CharField(max_length=2, choices=COUNTY_CHOICES)
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

    @transition(field=status, target="county_completed")
    def complete_county(self):
        pass

    @transition(field=status, source="county_completed", target="submitted")
    def complete_submit(self):
        self.submitted_at = timezone.now()
