import requests
from xml.etree import ElementTree


class ALM_API():

    def __init__(self, alm_url ):
        self.session = requests.Session()
        self.alm_url = alm_url

    def _url(self, path):
        return self.alm_url+path

    def authenticate(self, alm_user, alm_pass):
        headers = {'Content-Type': 'application/xml'}
        xml = """<?xml version='1.0' encoding='utf-8'?>
        <alm-authentication>
        	    <user>{}</user>
        	    <password>{}</password>
        </alm-authentication>""".format(alm_user, alm_pass)

        response = self.session.post(self._url("/qcbin/authentication-point/alm-authenticate"), headers=headers,
                                    data=xml)
        if response.status_code == 200:
            response = self.session.post(self._url("/qcbin/rest/site-session"))
            if response.status_code == 201:
                return True
            else:
                return False
        else:
            return False

    def get_domains(self):
        response = self.session.get(self._url("/qcbin/api/domains"))
        response_tree_root = ElementTree.fromstring(response.content)
        return [domain.attrib['Name'] for domain in response_tree_root.iter('Domain') if domain.attrib['Name']!='' ]

    def get_projects(self, domain):
        response = self.session.get((self._url("/qcbin/api/domains/{}/projects".format(domain))))
        response_tree_root = ElementTree.fromstring(response.content)

        return [domain.attrib['Name'] for domain in response_tree_root.iter('Project') if domain.attrib['Name'] != '']

    def get_domain_mapping(self):
        response = self.session.get(self._url("/qcbin/api/domains"))
        response_tree_root = ElementTree.fromstring(response.content)
        domains= [domain.attrib['Name'] for domain in response_tree_root.iter('Domain') if domain.attrib['Name'] != '']
        domain_mapping = {}
        for domain in domains:
            response = self.session.get((self._url("/qcbin/api/domains/{}/projects".format(domain))))
            response_tree_root = ElementTree.fromstring(response.content)
            domain_mapping[domain] = [domain.attrib['Name'] for domain in response_tree_root.iter('Project') if domain.attrib['Name'] != '']

        return domain_mapping
