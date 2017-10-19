from ptscripts import multi_nikto as mn


def test_get_webservers(ports_csv):
    expected = [
        {'ipv4': '10.0.0.1', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '80', 'mac': '00:78:2A:E8:35:29', 'service_tunnel': '', 'hostnames': '',
         'product_version': '', 'service_name': 'http'},
        {'ipv4': '10.0.0.1', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '443', 'mac': '00:78:2A:E8:35:29', 'service_tunnel': 'ssl', 'hostnames': '',
         'product_version': '', 'service_name': 'http'},
        {'ipv4': '10.0.0.1', 'banner': '', 'product_name': 'Mongoose httpd', 'protocol': 'tcp',
         'port': '3000', 'mac': '00:78:2A:E8:35:29', 'service_tunnel': 'ssl', 'hostnames': '',
         'product_version': '', 'service_name': 'http'},
        {'ipv4': '10.0.0.7', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '80', 'mac': 'B8:AE:ED:EC:16:23', 'service_tunnel': '', 'hostnames': '',
         'product_version': '1.11.10', 'service_name': 'http'},
        {'ipv4': '10.0.0.7', 'banner': '', 'product_name': 'Werkzeug httpd', 'protocol': 'tcp',
         'port': '5000', 'mac': 'B8:AE:ED:EC:16:23', 'service_tunnel': '', 'hostnames': '',
         'product_version': '0.11.11', 'service_name': 'http'},
        {'ipv4': '10.0.0.7', 'banner': '', 'product_name': 'MochiWeb Erlang HTTP library',
         'protocol': 'tcp', 'port': '32768', 'mac': 'B8:AE:ED:EC:16:23', 'service_tunnel': '',
         'hostnames': '', 'product_version': '1.0', 'service_name': 'http'},
        {'ipv4': '10.0.0.45', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '80', 'mac': '00:11:32:73:03:38', 'service_tunnel': '', 'hostnames': '',
         'product_version': '', 'service_name': 'http'},
        {'ipv4': '10.0.0.45', 'banner': '', 'product_name': 'nginx', 'protocol': 'tcp',
         'port': '443', 'mac': '00:11:32:73:03:38', 'service_tunnel': 'ssl', 'hostnames': '',
         'product_version': '', 'service_name': 'http'},
        {'ipv4': '10.0.0.45', 'banner': '', 'product_name': 'Werkzeug httpd', 'protocol': 'tcp',
         'port': '5075', 'mac': '00:11:32:73:03:38', 'service_tunnel': '', 'hostnames': '',
         'product_version': '0.10.4', 'service_name': 'http'},
        {'ipv4': '10.0.0.45', 'banner': '', 'product_name': 'Plex Media Server httpd',
         'protocol': 'tcp', 'port': '32400', 'mac': '00:11:32:73:03:38', 'service_tunnel': '',
         'hostnames': '', 'product_version': '', 'service_name': 'http'},
    ]
    results = mn.get_webservers(ports_csv)
    assert expected == results


class TestCreateCommand(object):
    webserver = {
        "port": "8443", "protocol": "tcp", "ipv4": "10.0.0.75", "mac": "00:78:2A:E8:35:29",
        "hostnames": "", "service_name": "http", "service_tunnel": "ssl",
        "product_name": "nginx", "product_version": "", "banner": ""
    }

    def test_tunnel_no_proxy(self):
        expected = (
            "nikto -C all -host 10.0.0.75 -port 8443 -ssl -output /root/pentests/test/nikto/Nikto_10.0.0.75_8443.csv",
            "/root/pentests/test/nikto/Nikto_10.0.0.75_8443.html"
        )
        output_dir = "/root/pentests/test/nikto"
        proxy = False
        results = mn.create_command(self.webserver, output_dir, proxy)
        assert expected == results

    def test_no_tunnel_no_proxy(self):
        expected = (
            "nikto -C all -host 10.0.0.75 -port 8443 -output /root/pentests/test/nikto/Nikto_10.0.0.75_8443.csv",
            "/root/pentests/test/nikto/Nikto_10.0.0.75_8443.html"
        )
        self.webserver['service_tunnel'] = ''
        output_dir = "/root/pentests/test/nikto"
        proxy = False
        results = mn.create_command(self.webserver, output_dir, proxy)
        assert expected == results

    def test_tunnel_proxy(self):
        expected = (
            "proxychains nikto -C all -host 10.0.0.75 -port 8443 -ssl -output /root/pentests/test/nikto/Nikto_10.0.0.75_8443.csv",
            "/root/pentests/test/nikto/Nikto_10.0.0.75_8443.html"
        )
        self.webserver['service_tunnel'] = 'ssl'
        output_dir = "/root/pentests/test/nikto"
        proxy = True
        results = mn.create_command(self.webserver, output_dir, proxy)
        assert expected == results

    def test_no_tunnel_proxy(self):
        expected = (
            "proxychains nikto -C all -host 10.0.0.75 -port 8443 -output /root/pentests/test/nikto/Nikto_10.0.0.75_8443.csv",
            "/root/pentests/test/nikto/Nikto_10.0.0.75_8443.html"
        )
        self.webserver['service_tunnel'] = ''
        output_dir = "/root/pentests/test/nikto"
        proxy = True
        results = mn.create_command(self.webserver, output_dir, proxy)
        assert expected == results
