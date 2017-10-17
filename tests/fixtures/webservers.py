import pytest


@pytest.fixture
def webserver_list():
    webservers = [
        "http://10.0.0.1/",
        "https://10.0.0.1/",
        "https://10.0.0.1:3000/",
        "http://10.0.0.7/",
        "http://10.0.0.7:5000/",
        "http://10.0.0.7:32768/",
        "http://10.0.0.45/",
        "https://10.0.0.45/",
        "http://10.0.0.45:5075/",
        "http://10.0.0.45:32400/",
    ]
    return webservers


@pytest.fixture
def webserver_file(webserver_list, tmpdir):  # pylint: disable=redefined-outer-name
    webserver_file_path = tmpdir.join("test_webservers.txt")
    with open(webserver_file_path.strpath, "w") as f:
        for webserver in webserver_list:
            f.write(webserver + "\r\n")
    return webserver_file_path.strpath
