from ptscripts.enumeration import multi_enum4linux as me


def test_get_ips(ports_csv):
    expected = ['10.0.0.45', '10.0.0.45']
    results = me.get_ips(ports_csv)
    assert expected == results


def test_create_command():
    expected = ("enum4linux -a 10.0.0.45", "/tmp/enum4linux_10.0.0.45.html")
    results = me.create_command("10.0.0.45", "/tmp", False)
    assert expected == results

    # With proxy
    expected = ("proxychains enum4linux -a 10.0.0.45", "/tmp/enum4linux_10.0.0.45.html")
    results = me.create_command("10.0.0.45", "/tmp", True)
    assert expected == results
