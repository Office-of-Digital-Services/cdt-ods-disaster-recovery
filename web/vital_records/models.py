from uuid import UUID, uuid4

from django.db import models
from django.utils import timezone
from django_fsm import FSMField, transition

from web.vital_records.routes import Routes


class VitalRecordsRequest(models.Model):
    """Represents a request to order a vital record through the Disaster Recovery app."""

    STATUS_CHOICES = [
        ("initialized", "Initialized"),
        ("started", "Started"),
        ("statement_completed", "Sworn Statement Completed"),
        ("name_completed", "Name Completed"),
        ("county_completed", "County Completed"),
        ("dob_completed", "Date of Birth Completed"),
        ("parents_names_completed", "Parents Names Completed"),
        ("order_info_completed", "Order Info Completed"),
        ("submitted", "Request Submitted"),
        ("enqueued", "Request Enqueued"),
        ("packaged", "Request Packaged"),
        ("sent", "Request Sent"),
        ("finished", "Finished"),
    ]

    FIRE_CHOICES = [
        ("eaton", "Eaton fire"),
        ("hurst", "Hurst fire"),
        ("lidia", "Lidia fire"),
        ("palisades", "Palisades fire"),
        ("woodley", "Woodley fire"),
    ]

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
        ("Alameda", "Alameda"),
        ("Alpine", "Alpine"),
        ("Amador", "Amador"),
        ("Butte", "Butte"),
        ("Calaveras", "Calaveras"),
        ("Colusa", "Colusa"),
        ("Contra Costa", "Contra Costa"),
        ("Del Norte", "Del Norte"),
        ("El Dorado", "El Dorado"),
        ("Fresno", "Fresno"),
        ("Glenn", "Glenn"),
        ("Humboldt", "Humboldt"),
        ("Imperial", "Imperial"),
        ("Inyo", "Inyo"),
        ("Kern", "Kern"),
        ("Kings", "Kings"),
        ("Lake", "Lake"),
        ("Lassen", "Lassen"),
        ("Los Angeles", "Los Angeles"),
        ("Madera", "Madera"),
        ("Marin", "Marin"),
        ("Mariposa", "Mariposa"),
        ("Mendocino", "Mendocino"),
        ("Merced", "Merced"),
        ("Modoc", "Modoc"),
        ("Mono", "Mono"),
        ("Monterey", "Monterey"),
        ("Napa", "Napa"),
        ("Nevada", "Nevada"),
        ("Orange", "Orange"),
        ("Placer", "Placer"),
        ("Plumas", "Plumas"),
        ("Riverside", "Riverside"),
        ("Sacramento", "Sacramento"),
        ("San Benito", "San Benito"),
        ("San Bernardino", "San Bernardino"),
        ("San Diego", "San Diego"),
        ("San Francisco", "San Francisco"),
        ("San Joaquin", "San Joaquin"),
        ("San Luis Obispo", "San Luis Obispo"),
        ("San Mateo", "San Mateo"),
        ("Santa Barbara", "Santa Barbara"),
        ("Santa Clara", "Santa Clara"),
        ("Santa Cruz", "Santa Cruz"),
        ("Shasta", "Shasta"),
        ("Sierra", "Sierra"),
        ("Siskiyou", "Siskiyou"),
        ("Solano", "Solano"),
        ("Sonoma", "Sonoma"),
        ("Stanislaus", "Stanislaus"),
        ("Sutter", "Sutter"),
        ("Tehama", "Tehama"),
        ("Trinity", "Trinity"),
        ("Tulare", "Tulare"),
        ("Tuolumne", "Tuolumne"),
        ("Ventura", "Ventura"),
        ("Yolo", "Yolo"),
        ("Yuba", "Yuba"),
    ]

    NUMBER_CHOICES = [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6"), (7, "7"), (8, "8"), (9, "9"), (10, "10")]

    STATE_CHOICES = [
        ("", "Select state"),
        ("AK", "Alaska"),
        ("AL", "Alabama"),
        ("AR", "Arkansas"),
        ("AS", "American Samoa"),
        ("AZ", "Arizona"),
        ("CA", "California"),
        ("CO", "Colorado"),
        ("CT", "Connecticut"),
        ("DC", "District of Columbia"),
        ("DE", "Delaware"),
        ("FL", "Florida"),
        ("FM", "Federated States of Micronesia"),
        ("GA", "Georgia"),
        ("GU", "Guam"),
        ("HI", "Hawaii"),
        ("IA", "Iowa"),
        ("ID", "Idaho"),
        ("IL", "Illinois"),
        ("IN", "Indiana"),
        ("KS", "Kansas"),
        ("KY", "Kentucky"),
        ("LA", "Louisiana"),
        ("MA", "Massachusetts"),
        ("MD", "Maryland"),
        ("ME", "Maine"),
        ("MH", "Marshall Islands"),
        ("MI", "Michigan"),
        ("MN", "Minnesota"),
        ("MO", "Missouri"),
        ("MP", "Northern Mariana Islands"),
        ("MS", "Mississippi"),
        ("MT", "Montana"),
        ("NC", "North Carolina"),
        ("ND", "North Dakota"),
        ("NE", "Nebraska"),
        ("NH", "New Hampshire"),
        ("NJ", "New Jersey"),
        ("NM", "New Mexico"),
        ("NV", "Nevada"),
        ("NY", "New York"),
        ("OH", "Ohio"),
        ("OK", "Oklahoma"),
        ("OR", "Oregon"),
        ("PA", "Pennsylvania"),
        ("PR", "Puerto Rico"),
        ("PW", "Palau"),
        ("RI", "Rhode Island"),
        ("SC", "South Carolina"),
        ("SD", "South Dakota"),
        ("TN", "Tennessee"),
        ("TX", "Texas"),
        ("UT", "Utah"),
        ("VA", "Virginia"),
        ("VI", "Virgin Islands"),
        ("VT", "Vermont"),
        ("WA", "Washington"),
        ("WI", "Wisconsin"),
        ("WV", "West Virginia"),
        ("WY", "Wyoming"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    status = FSMField(default="initialized", choices=STATUS_CHOICES)
    fire = models.CharField(max_length=50, choices=FIRE_CHOICES)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)
    legal_attestation = models.CharField(max_length=386)
    first_name = models.CharField(max_length=128)
    middle_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128)
    county_of_event = models.CharField(max_length=15, choices=COUNTY_CHOICES)
    date_of_event = models.DateField(null=True)
    person_1_first_name = models.CharField(max_length=128)
    person_1_last_name = models.CharField(max_length=128)
    person_2_first_name = models.CharField(max_length=128, blank=True)
    person_2_last_name = models.CharField(max_length=128, blank=True)
    number_of_records = models.IntegerField(choices=NUMBER_CHOICES, null=True)
    order_first_name = models.CharField(max_length=128)
    order_last_name = models.CharField(max_length=128)
    address = models.CharField(max_length=128)
    address_2 = models.CharField(max_length=128)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2, choices=STATE_CHOICES)
    zip_code = models.CharField(max_length=10)
    email_address = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=10)
    started_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    enqueued_at = models.DateTimeField(null=True, blank=True)
    packaged_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def get_with_status(request_id: UUID, required_status: str):
        """
        Return a VitalRecordsRequest with a matching ID and status.

        Raise a ValueError if the request is not found or does not have the required status.
        """
        request = VitalRecordsRequest.objects.filter(pk=request_id).first()

        if request is None:
            raise ValueError(f"Couldn't find VitalRecordsRequest: {request_id}")
        if request.status != required_status:
            raise ValueError(
                f"VitalRecordsRequest: {request_id} has an invalid status. \
                  Expected: {required_status}, Actual: {request.status}"
            )

        return request

    @staticmethod
    def get_finished():
        return VitalRecordsRequest.objects.filter(status="finished")

    # Transitions from state to state
    @transition(field=status, source="initialized", target="started")
    def complete_start(self):
        self.started_at = timezone.now()
        return Routes.app_route(Routes.request_statement)

    @transition(field=status, source="started", target="statement_completed")
    def complete_statement(self):
        return Routes.app_route(Routes.request_name)

    @transition(field=status, target="name_completed")
    def complete_name(self):
        return Routes.app_route(Routes.request_county)

    @transition(field=status, target="county_completed")
    def complete_county(self):
        return Routes.app_route(Routes.request_dob)

    @transition(field=status, target="dob_completed")
    def complete_dob(self):
        return Routes.app_route(Routes.request_parents)

    @transition(field=status, target="parents_names_completed")
    def complete_parents_names(self):
        return Routes.app_route(Routes.request_order)

    @transition(field=status, target="order_info_completed")
    def complete_order_info(self):
        return Routes.app_route(Routes.request_submit)

    @transition(field=status, source="order_info_completed", target="submitted")
    def complete_submit(self):
        self.submitted_at = timezone.now()
        return Routes.app_route(Routes.request_submitted)

    @transition(field=status, source="submitted", target="enqueued")
    def complete_enqueue(self):
        self.enqueued_at = timezone.now()

    @transition(field=status, source="enqueued", target="packaged")
    def complete_package(self):
        self.packaged_at = timezone.now()

    @transition(field=status, source="packaged", target="sent")
    def complete_send(self):
        self.sent_at = timezone.now()

    @transition(field=status, source="sent", target="finished")
    def finish(self):
        pass


class VitalRecordsRequestMetadata(models.Model):
    id = models.BigAutoField(primary_key=True)
    request_id = models.UUIDField(editable=False)
    fire = models.CharField(max_length=50, choices=VitalRecordsRequest.FIRE_CHOICES, editable=False)
    number_of_records = models.IntegerField(choices=VitalRecordsRequest.NUMBER_CHOICES, editable=False)
    submitted_at = models.DateTimeField(editable=False)
    enqueued_at = models.DateTimeField(editable=False)
    packaged_at = models.DateTimeField(editable=False)
    sent_at = models.DateTimeField(editable=False)
    cleaned_at = models.DateTimeField(editable=False)

    class Meta:
        verbose_name = "Request metadata"
        verbose_name_plural = "Request metadata"
