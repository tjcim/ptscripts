from ptscripts.enumeration import multi_testssl as mt


def test_create_command():
    expected = (
        "testssl.sh --csvfile /root/pentests/test/testssl/testssl_www.google.com_443.csv https://www.google.com",
        "/root/pentests/test/testssl/testssl_www.google.com_443.html"
    )
    results = mt.create_command("https://www.google.com", "/root/pentests/test/testssl/")
    assert expected == results
