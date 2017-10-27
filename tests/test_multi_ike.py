from ptscripts.exploitation import multi_ike as mi


def test_create_command():
    expected = "ike-scan -M -A --id=test 10.0.0.63"
    results = mi.create_command("10.0.0.63")
    assert expected == results
