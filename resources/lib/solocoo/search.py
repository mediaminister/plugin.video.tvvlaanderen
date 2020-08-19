# -*- coding: utf-8 -*-
""" Solocoo Search API """

from __future__ import absolute_import, division, unicode_literals

import json
import logging

from resources.lib.solocoo import SOLOCOO_API, util
from resources.lib.solocoo.channel import ASSET_TYPE_CHANNEL

_LOGGER = logging.getLogger(__name__)


class SearchApi:
    """ Solocoo Search API """

    def __init__(self, auth):
        """ Initialisation of the class.

        :param resources.lib.solocoo.auth.AuthApi auth: The Authentication object
        """
        self._auth = auth
        self._tokens = self._auth.login()

    def search(self, query):
        """ Search through the catalog.

        :returns: A list of results.

        :rtype: List[]
        """
        _LOGGER.debug('Requesting entitlements')
        entitlements = self._auth.list_entitlements()

        _LOGGER.debug('Requesting search listing')
        reply = util.http_get(SOLOCOO_API + '/search', params=dict(query=query), token_bearer=self._tokens.jwt_token)
        data = json.loads(reply.text)

        results = []

        # Parse EPG
        results_epg = next((c for c in data.get('collection') if c.get('label') == 'sg.ui.search.epg'), {})
        results.extend([util.parse_channel(asset)
                        for asset in results_epg.get('assets', [])
                        if asset.get('type') == ASSET_TYPE_CHANNEL])

        # Parse replay
        replay = next((c for c in data.get('collection') if c.get('label') == 'sg.ui.search.replay'), {})
        results.extend([util.parse_program(asset)
                        for asset in replay.get('assets', [])])

        # Filter only available channels
        results = util.filter_unavailable_assets(results, entitlements.get('offers', []))

        return results
