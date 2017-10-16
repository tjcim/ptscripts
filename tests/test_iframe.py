import os

from ptscripts import iframe


def test_iframe(tmpdir):
    url = "https://www.google.com/"
    output_dir = tmpdir.strpath
    output_file = os.path.join(output_dir, "iframe.html")

    # build expected
    expected_string = """
    <html>
    <head>
    </head>
    <body>
    <h1>Website {0} inside an iFrame</h1>
    <iframe src="{0}" height=600 width=600>
    </body>
    </html>
    """.format(url)
    expected = expected_string.splitlines()

    # Run script
    args = iframe.parse_args([url, output_dir])
    iframe.write_iframe(args)

    # Read results
    with open(output_file, "r") as f:
        results = f.read().splitlines()

    # Compare with expected
    assert results == expected
