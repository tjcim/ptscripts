from ptscripts.enumeration import multi_wpscan as mw


def test_create_command():
    expected = (
        "wpscan -u https://www.google.com -e u1-100 --random-agent --follow-redirection --disable-tls-checks",
        "/root/pentests/test/wpscan/wpscan_www.google.com_443.html"
    )
    results = mw.create_command("https://www.google.com", "/root/pentests/test/wpscan/")
    assert expected == results
