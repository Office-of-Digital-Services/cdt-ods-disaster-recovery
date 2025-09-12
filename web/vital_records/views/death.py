from django.views.generic.edit import UpdateView

from web.vital_records.views import common


class NameView(common.NameView):
    pass


class CountyView(common.CountyView):
    pass


class DateOfDeathView(common.DateOfEventView):
    pass


class DateOfBirthView(common.DateOfEventView):
    pass


class ParentView(UpdateView):
    pass


class SpouseView(UpdateView):
    pass
