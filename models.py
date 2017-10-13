""" Class objects used by the scripts. """
import logging


log = logging.getLogger("ptscripts.models")


class Vulnerability:
    def __init__(self, finding, risk_level, _id, impact=None, remediation=None):
        log.debug("Creating vulnerability: {}".format(_id))
        self.id = _id
        self.finding = finding
        self.risk_level = risk_level
        self.impact = impact
        self.remediation = remediation
        self.resource = ""
        self.affected = []

    def add_affected(self, host):
        log.debug("here")
        self.affected.append(host)

    def list_format(self):
        formatted_hosts = ",\r\n".join(self.affected)
        return [
            self.finding, formatted_hosts, self.risk_level, self.impact, self.remediation,
            self.resource
        ]

    def __repr__(self):
        return "{} {} {}".format(self.id, self.affected, self.risk_level)


class TestSSLVulnerability(Vulnerability):
    def __init__(self, finding, risk_level, _id, impact=None, remediation=None):  # pylint: disable=super-on-old-class
        super().__init__(finding, risk_level, _id, impact, remediation)
        risk_levels = {"NOT ok": "M", "MINOR": "L", "WARN": "L", "MEDIUM": "L"}
        try:
            self.risk_level = risk_level + ": " + risk_levels[self.risk_level]
        except KeyError:
            log.error("Couldn't set an appropriate risk level for {}".format(_id))

    def add_affected(self, issue):
        log.debug(issue)
        ip = issue[1].split('/')[1]
        port = issue[2]
        self.affected.append("{}:{}".format(ip, port))


class NessusVulnerability(Vulnerability):
    def __init__(self, finding, risk_level, _id, impact=None, remediation=None):  # pylint: disable=super-on-old-class
        super().__init__(finding, risk_level, _id, impact, remediation)
        risk_levels = {"Critical": "H", "High": "H", "Medium": "M", "Low": "L"}
        self.risk_level = risk_levels[self.risk_level]

    def add_affected(self, nessus_vuln):
        ip = nessus_vuln[4]
        port = nessus_vuln[6]
        protocol = nessus_vuln[5]
        host = "{}:{} ({})".format(ip, port, protocol)
        log.debug("Adding host {} to vulnerability {}".format(host, self.id))
        self.affected.append(host)
