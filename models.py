""" Class objects used by the scripts. """
import logging


log = logging.getLogger("ptscripts.models")


class Vulnerability:  # pylint: disable=too-many-instance-attributes
    def __init__(self, finding, risk_level, _id, impact=None, remediation=None):
        log.debug("Creating vulnerability: {}".format(_id))
        self.id = _id
        self.finding = finding
        self.risk_level = risk_level
        self.impact = impact or ""
        self.remediation = remediation or ""
        self.resource = ""
        self.affected = []
        self.index = ""

    def add_affected(self, host):
        self.affected.append(host)

    def list_format(self):
        formatted_hosts = ",\r\n".join(self.affected)
        return [
            "", self.finding, formatted_hosts, self.risk_level, self.impact, self.remediation,
            self.resource
        ]

    def dict_format(self):
        formatted_hosts = ",\r\n".join(self.affected)
        return {
            "finding": self.finding, "risk_level": self.risk_level, "affected": formatted_hosts,
            "impact": self.impact, "remediation": self.remediation, "resource": self.resource,
            "index": self.index,
        }

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
        # The following is to remove nessus' carriage returns in awkward places. This will split
        # the impact and remediation into lines and if the line is blank it will replace the
        # carriage return, otherwise it will remove it and use a space.
        impact_lines = self.impact.splitlines()
        new_impact = []
        for line in impact_lines:
            if line:
                new_impact.append(line + " ")
            else:
                new_impact.append("\r\n")
        self.impact = "".join(new_impact)
        remediation_lines = self.impact.splitlines()
        new_remediation = []
        for line in remediation_lines:
            if line:
                new_remediation.append(line + " ")
            else:
                new_remediation.append("\r\n")
        self.remediation = "".join(new_remediation)

    def add_affected(self, nessus_vuln):
        ip = nessus_vuln["Host"]
        port = nessus_vuln["Port"]
        protocol = nessus_vuln["Protocol"]
        host = "{}:{} ({})".format(ip, port, protocol)
        log.debug("Adding host {} to vulnerability {}".format(host, self.id))
        self.affected.append(host)
