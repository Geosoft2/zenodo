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

from extractTool.similar import master

import requests

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
    """Get similar records by using record fetcher and request to get the actual record and a list of the 
    (last 1000 - as its the maximum possible in zenodo) metadata of records in the database."""
    
    print('################ query string try #########################')
    rqSize = request.args.get('size')
    print(rqSize)
    print('################ query string try #########################')

    """get actual record with fetcher"""
    record = fetch_record(recid)

    print('################ record fetch try #########################')
    print(record[1]['_files'][0]['type'])
    print('################ record fetch try #########################')

    print('################ record bbox fetch try #########################')
    print(type(record[1]['bbox']))
    print('################ record bbox fetch try #########################')    

    """variable of the record id for future use in loops as the parameter wont do"""
    rrid = record[1]['recid']
    
    """making the url for the api request fetching the maximum of 1000 records"""
    recordlistURL = url_for('invenio_records_rest.recid_list', _external=True)
    recordlist1000URL = recordlistURL+'?sort=mostrecent&page=1&size=1000'
    
    """api request to fetch the metadata of the latest 1000 records from api/records/"""
    response = requests.get(recordlist1000URL)
    recordlist_raw = response.json()
    
    """prints for navigation purpose"""
    print('################ bbox fetch try #########################')
    print(recordlist_raw['hits']['hits'][0]['metadata']['bbox'])
    print('################ bbox fetch try #########################')

    print('################ id fetch try #########################')
    print(recordlist_raw['hits']['hits'][0]['id'])
    print('################ id fetch try #########################')

    print('################ name fetch try #########################')
    print(recordlist_raw['hits']['hits'][0]['metadata']['title'])
    print('################ id fetch try #########################')

    print('################ total file count fetch try #########################')
    print(recordlist_raw['hits']['total'])
    print('################ total file count fetch try #########################')

    """total file count from the record-metadata-list"""
    total_files = recordlist_raw['hits']['total']
    
    """new list object to go on the record layer"""
    recordlist = recordlist_raw['hits']['hits']
    
    # print('################## record-list #######################')
    # print(recordlist)
    # print('################## record-list #######################')

    """obtaining a list of every record with a valid bounding box
    exception if: bbox is empty or not a list object or record id identical to the actual record"""
    bboxList = list()

    for i in range(0, total_files):
        try:
            rid = recordlist[i]['id']
            irecord = fetch_record(rid)
            rname = recordlist[i]['metadata']['title']
            rbbox = irecord[1]['bbox']
            rtype = irecord[1]['_files'][0]['type']
            if rbbox != None and rbbox != [] and type(rbbox) == list and type(rbbox[0]) == list and rid != rrid:
                bboxList.append([rbbox,rid,rname,rtype])
        except Exception:
            print('no valid bounding box found in record '+str(rid))
    
    print('################## bbox-list #######################')
    print(bboxList)
    print('################## bbox-list #######################')
    
    """appending the simulation score to the list with the method written in our module extractTool similar.py"""
    simList = list()
    for bboxItem in bboxList:
        simList.append([master(bboxItem[0][0],record[1]['bbox'][0], bboxItem[3], record[1]['_files'][0]['type']),bboxItem[0], bboxItem[1], bboxItem[2], bboxItem[3]])
    
    print('################## sim-list #######################')
    print(simList)
    print('################## sim-list #######################')

    """sorted list as of the similarity value descending order"""
    sortSimList = sorted(simList, key=lambda x: x[0], reverse=True)

    print('################## sortsim-list #######################')
    print(sortSimList)
    print('################## sortsim-list #######################')

    """variable to set how many records will be displayed in the output json file later on
    can be set with query parameter size e.g. --> ?size=10"""
    if rqSize:
        try:
            shouldbeZero = int(rqSize) - int(rqSize)
            if shouldbeZero == 0:
                size = int(rqSize)
                if size < 20:
                    sizeReverse = 20 - int(size)
                    json_output_int = 20 - sizeReverse
                else:
                    json_output_int = 20
            else:
                json_output_int = 20
        except ValueError:
            json_output_int = 20
    else:
        json_output_int = 20

    """json dictionary to prepare for the response"""
    json_dict = {}
    json_dict = [{"match": 
                    [
                        {"id": listItem[2]},
                        {"name": listItem[3]},
                        {"type": "Feature",
                         "geometry": {
                            "type": "Polygon",
                            "coordinates": listItem[1][0]}
                        },
                        {"filetype": listItem[4]},
                        {"sim_value": listItem[0]}
                    ]
                    } for listItem in sortSimList[0:json_output_int]]

    print('################## json_dict #######################')
    print(json_dict)
    print('################## json_dict #######################')
    
    return Response(
        json.dumps({
            'record': rrid,
            'similar': json_dict,
        },
            **_format_args()
        ),
        mimetype='application/json',
    )