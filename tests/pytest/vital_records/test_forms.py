import pytest

from web.vital_records.forms.common import StatementForm, TypeForm
from web.vital_records.models import VitalRecordsRequest


def test_TypeForm():
    form = TypeForm()

    assert form.fields["type"].choices == [
        ("", "Select type"),
        ("birth", "Birth record"),
        ("marriage", "Marriage record"),
        ("death", "Death record"),
    ]


@pytest.mark.parametrize(
    "type,expected_choices",
    [
        (
            "birth",
            [
                ("", "Select relationship"),
                ("self", "Self"),
                ("parent", "Parent"),
                ("legal guardian", "Legal guardian"),
                ("child", "Child"),
                ("grandparent", "Grandparent"),
                ("grandchild", "Grandchild"),
                ("sibling", "Sibling"),
                ("spouse", "Spouse"),
                ("domestic_partner", "Domestic partner"),
            ],
        ),
        (
            "marriage",
            [
                ("", "Select relationship"),
                ("self", "Self"),
                ("parent", "Parent"),
                ("legal guardian", "Legal guardian"),
                ("child", "Child"),
                ("grandparent", "Grandparent"),
                ("grandchild", "Grandchild"),
                ("sibling", "Sibling"),
                ("spouse", "Spouse"),
                ("domestic_partner", "Domestic partner"),
            ],
        ),
        (
            "death",
            [
                ("", "Select relationship"),
                ("parent", "Parent"),
                ("legal guardian", "Legal guardian"),
                ("child", "Child"),
                ("grandparent", "Grandparent"),
                ("grandchild", "Grandchild"),
                ("sibling", "Sibling"),
                ("spouse", "Spouse"),
                ("domestic_partner", "Domestic partner"),
                ("surviving_next_of_kin", "Surviving next of kin (As specified in HSC § 7100)"),
            ],
        ),
    ],
)
def test_StatementForm(type, expected_choices):
    model_instance = VitalRecordsRequest(type=type)
    form = StatementForm(instance=model_instance)

    choices = form.fields["relationship"].choices
    assert choices == expected_choices
