import re
from abc import ABC, abstractmethod
from typing import Dict, List
import requests
import json
from bs4 import BeautifulSoup
from base_plugin import BasePlugin


class AbstractVulnerability(ABC):
    """
    pass
    """

    def template_method(self, **kwargs) -> Dict:
        """
        pass
        :return:
        """
        return self.required_vulnerability(**kwargs)

    @abstractmethod
    def required_vulnerability(self, **kwargs) -> Dict:
        pass


class VulnDB(AbstractVulnerability):
    """
    pass
    """

    def __init__(self):
        """
        pass
        """
        self.api = 'API_VULNDB'
        self.user_agent = 'VulDB API Python Agent'

    def required_vulnerability(self, **kwargs) -> Dict:
        """

        :param kwargs: product and version
        :return:
        """
        url = 'https://vuldb.com/?api'
        headers = {'User-Agent': self.user_agent, 'X-VulDB-ApiKey': self.api}
        post_data = {'advancedsearch': f'product:{kwargs["product"]},version:{kwargs["version"]}', 'limit': 10}
        response = requests.post(url, headers=headers, data=post_data)
        if response.status_code == 200:
            response_json = json.loads(response.content)
        else:
            response_json = {}
        return response_json


class CveMitre(AbstractVulnerability):

    def __init__(self):
        self.url = 'https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword='

    def parse_html(self, target) -> List:
        """

        :param target:
        :return:
        """
        url = f'{self.url}{target}'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser").find('div', id='TableWithRules')
        listing_item_main = soup.find_all('td')
        result_cve = self.re_cve(listing_item_main)
        return result_cve

    def re_cve(self, items) -> List:
        """

        :param items:
        :return:
        """
        list_cve = []
        for i in items:
            re_find = re.match("CVE", i.text)
            if re_find:
                list_cve.append(i.text)
        return list_cve

    def required_vulnerability(self, **kwargs) -> Dict:
        """

        :param kwargs: product and version
        :return:
        """
        target = f'{kwargs["product"]} {kwargs["version"]}'
        data = {
            "data": self.parse_html(target)
        }
        return data


def result_code(abstract_vulnerability: AbstractVulnerability, **kwargs) -> Dict:
    """

    :param abstract_vulnerability:
    :return:
    """
    return abstract_vulnerability.template_method(**kwargs)


class FenixCVEMitre(BasePlugin):

    def __init__(self):
        """

        """
        pass

    def run(self, **kwargs):
        if kwargs is not None:
            if (('product' in kwargs) and (kwargs['product'] is not None)) and \
                    (('version' in kwargs) and (kwargs['version'] is not None)):
                result_cvemitre = result_code(CveMitre(), product=kwargs['product'], version=kwargs['version'])
                return {'cve_mitre': result_cvemitre['data']}
