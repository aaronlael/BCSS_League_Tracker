import types
import unittest
from unittest.mock import patch

import udisc_scrape


class UDiscEventURLTests(unittest.TestCase):
    def test_accepts_canonical_event_url_and_discards_query(self):
        self.assertEqual(
            udisc_scrape.validate_udisc_event_url(
                'https://udisc.com/events/Event123?round=1&view=scores'
            ),
            'https://udisc.com/events/Event123',
        )

    def test_rejects_non_udisc_hosts_schemes_and_paths(self):
        invalid_urls = [
            'http://udisc.com/events/Event123',
            'https://udisc.com.attacker.example/events/Event123',
            'https://attacker.example/?next=https://udisc.com/events/Event123',
            'https://user@udisc.com/events/Event123',
            'https://udisc.com:8443/events/Event123',
            'https://udisc.com/events/Event123/extra',
            'https://udisc.com/events/',
            'https://udisc.com.evil/events/Event123',
            'https://udisc.com/events/Event123#fragment',
            None,
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                with self.assertRaises(udisc_scrape.InvalidUDiscEventURL):
                    udisc_scrape.validate_udisc_event_url(url)

    def test_scraper_disables_redirects_and_uses_timeout(self):
        response = types.SimpleNamespace(
            status_code=200,
            content=b'<html><div class="w-full min-w-0 overflow-x-auto '
            b'overflow-y-hidden rounded-lg"><table></table></div></html>',
            raise_for_status=lambda: None,
        )
        with (
            patch.object(udisc_scrape.requests, 'get', return_value=response) as get,
            patch.object(udisc_scrape, 'BeautifulSoup') as soup_factory,
        ):
            table = soup_factory.return_value.find.return_value.find.return_value
            table.find_all.return_value = []
            result = udisc_scrape.scrape_results_page(
                'https://udisc.com/events/Event123'
            )

        self.assertEqual(result, [])
        get.assert_called_once_with(
            'https://udisc.com/events/Event123',
            timeout=(5, 20),
            allow_redirects=False,
        )

    def test_invalid_url_is_rejected_before_request(self):
        with patch.object(udisc_scrape.requests, 'get') as get:
            with self.assertRaises(udisc_scrape.InvalidUDiscEventURL):
                udisc_scrape.scrape_results_page(
                    'http://127.0.0.1/?url=https://udisc.com/events/Event123'
                )
        get.assert_not_called()

    def test_scraper_rejects_redirect_responses(self):
        response = types.SimpleNamespace(status_code=302, headers={'Location': 'http://127.0.0.1'})
        with patch.object(udisc_scrape.requests, 'get', return_value=response) as get:
            with self.assertRaises(udisc_scrape.requests.exceptions.HTTPError):
                udisc_scrape.scrape_results_page(
                    'https://udisc.com/events/Event123'
                )

        get.assert_called_once_with(
            'https://udisc.com/events/Event123',
            timeout=(5, 20),
            allow_redirects=False,
        )


if __name__ == '__main__':
    unittest.main()
