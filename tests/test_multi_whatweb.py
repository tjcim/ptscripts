from ptscripts import multi_whatweb as mw


def test_create_command():
    expected = (
        "whatweb -v -a 3 https://www.google.com",
        "/root/pentests/test/whatweb/whatweb_www.google.com_443.html"
    )
    results = mw.create_command("https://www.google.com", "/root/pentests/test/whatweb/")
    assert expected == results
