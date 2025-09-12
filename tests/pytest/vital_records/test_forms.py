from web.vital_records.forms.common import TypeForm


def test_TypeForm():
    form = TypeForm()

    assert form.fields["type"].choices == [
        ("", "Select type"),
        ("birth", "Birth record"),
        ("marriage", "Marriage record"),
        ("death", "Death record")
    ]
