import xml.etree.ElementTree as ET

import pytest


@pytest.fixture()
def xml_host():
    host = """
<host starttime="1507085206" endtime="1507090329"><status state="up" reason="arp-response" reason_ttl="0"/>
<address addr="10.0.0.1" addrtype="ipv4"/>
<address addr="00:78:2A:E8:35:29" addrtype="mac"/>
<hostnames>
<hostname name="100.119.152.33.bigleaf.net" type="PTR"/>
</hostnames>
<ports><extraports state="filtered" count="8291">
<extrareasons reason="no-responses" count="8291"/>
</extraports>
<extraports state="open|filtered" count="49">
<extrareasons reason="no-responses" count="49"/>
</extraports>
<port protocol="tcp" portid="22"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="ssh" product="OpenSSH" version="7.2" extrainfo="protocol 2.0" method="probed" conf="10"><cpe>cpe:/a:openbsd:openssh:7.2</cpe></service><script id="banner" output="SSH-2.0-OpenSSH_7.2"/></port>
<port protocol="tcp" portid="53"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="domain" product="dnsmasq" version="2.76" method="probed" conf="10"><cpe>cpe:/a:thekelleys:dnsmasq:2.76</cpe></service></port>
<port protocol="tcp" portid="80"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="http" product="nginx" method="probed" conf="10"><cpe>cpe:/a:igor_sysoev:nginx</cpe></service></port>
<port protocol="tcp" portid="443"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="http" product="nginx" tunnel="ssl" method="probed" conf="10"><cpe>cpe:/a:igor_sysoev:nginx</cpe></service></port>
<port protocol="tcp" portid="3000"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="http" product="Mongoose httpd" tunnel="ssl" method="probed" conf="10"><cpe>cpe:/a:cesanta:mongoose</cpe></service></port>
<port protocol="udp" portid="53"><state state="open" reason="udp-response" reason_ttl="64"/><service name="domain" product="dnsmasq" version="2.76" method="probed" conf="10"><cpe>cpe:/a:thekelleys:dnsmasq:2.76</cpe></service></port>
</ports>
<times srtt="21329" rttvar="37569" to="171605"/>
</host>
"""
    return ET.XML(host)


@pytest.fixture
def xml_ports():
    ports = [
        '<port protocol="tcp" portid="22"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="ssh" product="OpenSSH" version="7.2" extrainfo="protocol 2.0" method="probed" conf="10"><cpe>cpe:/a:openbsd:openssh:7.2</cpe></service><script id="banner" output="SSH-2.0-OpenSSH_7.2"/></port>',
        '<port protocol="tcp" portid="53"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="domain" product="dnsmasq" version="2.76" method="probed" conf="10"><cpe>cpe:/a:thekelleys:dnsmasq:2.76</cpe></service></port>',
        '<port protocol="tcp" portid="80"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="http" product="nginx" method="probed" conf="10"><cpe>cpe:/a:igor_sysoev:nginx</cpe></service></port>',
        '<port protocol="tcp" portid="443"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="http" product="nginx" tunnel="ssl" method="probed" conf="10"><cpe>cpe:/a:igor_sysoev:nginx</cpe></service></port>',
        '<port protocol="tcp" portid="3000"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="http" product="Mongoose httpd" tunnel="ssl" method="probed" conf="10"><cpe>cpe:/a:cesanta:mongoose</cpe></service></port>',
        '<port protocol="udp" portid="53"><state state="open" reason="udp-response" reason_ttl="64"/><service name="domain" product="dnsmasq" version="2.76" method="probed" conf="10"><cpe>cpe:/a:thekelleys:dnsmasq:2.76</cpe></service></port>',
    ]
    elements = []
    for elem in ports:
        elements.append(ET.XML(elem))
    return elements


@pytest.fixture
def xml_port():
    port = """<port protocol="tcp" portid="22"><state state="open" reason="syn-ack" reason_ttl="64"/><service name="ssh" product="OpenSSH" version="7.2" extrainfo="protocol 2.0" method="probed" conf="10"><cpe>cpe:/a:openbsd:openssh:7.2</cpe></service><script id="banner" output="SSH-2.0-OpenSSH_7.2"/></port>"""
    return ET.XML(port)
