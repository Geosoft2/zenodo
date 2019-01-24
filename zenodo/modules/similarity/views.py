# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2016 CERN.
#
# Zenodo is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Similarity API endpoint for Zenodo."""

from __future__ import absolute_import, print_function

from flask import Blueprint, Response, current_app, json, request, url_for, jsonify


from zenodo.modules.records.fetchers import zenodo_record_fetcher
from zenodo.modules.records.api import ZenodoRecord
from zenodo.modules.stats.utils import extract_event_record_metadata, fetch_record, fetch_record_file

blueprint = Blueprint(
    'zenodo_similarity',
    __name__,
    url_prefix='',
)

def _format_args():
    """Get JSON dump indentation and separates."""
    try:
        pretty_format = \
            current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and \
            not request.is_xhr
    except RuntimeError:
        pretty_format = False

    if pretty_format:
        return dict(
            indent=2,
            separators=(', ', ': '),
        )
    else:
        return dict(
            indent=None,
            separators=(',', ':'),
        )

@blueprint.route('/similarity/', methods=['GET'])
def index():
    """Demo endpoint."""
    return Response(
        json.dumps({
            'similarity': {
                'geosoftware2': 'rocks'
            }
        },
            **_format_args()
        ),
        mimetype='application/json',
    )

@blueprint.route('/records/<recid>/similar', methods=['GET'])
def similar(recid):
    """Get similar records."""
    # get actual record, MAYBE with a combination of zenodo_record_fetcher and ZenodoRecord.get_record(recid.object_uuid)
    record = fetch_record(recid)
    bbox = record[1]['bbox'][0]
    rrid = record[1]['recid'])
    print("###################################")
    for x in range(1, rrid):
        try:
            list(record[1]['bbox'][0])
        except Exception:
            (list(record[1]['bbox'][0]) == None) or (list(record[1]['bbox'][0]) == [])

    return Response(
        json.dumps({
            'record': recid,
            'similar': [
                {
                    'id': '2',
                    'similarity': bbox
                },
                {
                    'id': '4',
                    'similarity': bbox
                },
                {
                    'id': '6',
                    'similarity': bbox
                },
                {
                    'id': '8',
                    'similarity': bbox
                }
            ]
        },
            **_format_args()
        ),
        mimetype='application/json',
    )
