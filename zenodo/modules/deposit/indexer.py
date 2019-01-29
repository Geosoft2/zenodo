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

"""Record modification prior to indexing."""

from __future__ import absolute_import, print_function

import copy

from flask import current_app
from invenio_pidrelations.contrib.records import index_siblings
from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidrelations.serializers.utils import serialize_relations
from invenio_pidstore.models import PersistentIdentifier

#CLI Tool imports
from extractTool.extractTool import getMetadata
import sys
from os.path import join

from .api import ZenodoDeposit
def indexer_receiver(sender, json=None, record=None, index=None,
                     **dummy_kwargs):
    """Connect to before_record_index signal to transform record for ES.

    In order to avoid that a record and published deposit differs (e.g. if an
    embargo task updates the record), every time we index a record we also
    index the deposit and overwrite the content with that of the record.

    :param sender: Sender of the signal.
    :param json: JSON to be passed for the elastic search.
    :type json: `invenio_records.api.Deposit`
    :param record: Indexed deposit record.
    :type record: `invenio_records.api.Deposit`
    :param index: Elasticsearch index name.
    :type index: str
    """
    if not index.startswith('deposits-records-'):
        return

    if not isinstance(record, ZenodoDeposit):
        record = ZenodoDeposit(record, model=record.model)

    if record['_deposit']['status'] == 'published':
        schema = json['$schema']

        pub_record = record.fetch_published()[1]

        # Temporarily set to draft mode to ensure that `clear` can be called
        json['_deposit']['status'] = 'draft'
        json.clear()
        json.update(copy.deepcopy(pub_record.replace_refs()))

        # Set back to published mode and restore schema.
        json['_deposit']['status'] = 'published'
        json['$schema'] = schema
        json['_updated'] = pub_record.updated
    else:
        json['_updated'] = record.updated
        json['_created'] = record.created

    # Compute filecount and total file size
    files = json.get('_files', [])
    json['filecount'] = len(files)
    json['size'] = sum([f.get('size', 0) for f in files])

    recid = record.get('recid')
    if recid:
        pid = PersistentIdentifier.get('recid', recid)
        pv = PIDVersioning(child=pid)
        relations = serialize_relations(pid)
        if pv.exists:
            if pv.draft_child_deposit:
                is_last = (pv.draft_child_deposit.pid_value
                           == record['_deposit']['id'])
                relations['version'][0]['is_last'] = is_last
                relations['version'][0]['count'] += 1
        else:
            relations = {'version': [{'is_last': True, 'index': 0}, ]}
        if relations:
            json['relations'] = relations

def extractor_receiver(sender, *args, **kwargs):
    """Connect to before_record_insert to extract spatial related metadata.

    :param record: Indexed deposit record.
    :type record: `invenio_records.api.Deposit`
    """

    bboxArray=[]
    #folder_convHullArray=[]
    timeArray=[]
    record = kwargs['record']
    record['bbox']=[[None],[None],[None]]
    try:
        for i in record['_files']:
            #definition of the folderpath
            id_val=(i['file_id'])
            first_two=id_val[:2]
            second_two=id_val[2:4]
            last_part=id_val[4:]

            first_part=join(sys.prefix, 'var/instance/data')
            path=first_part+'/'+first_two+'/'+second_two+'/'+last_part+'/data'
            val=getMetadata(path,'bbox', True)
            #only appends value if it is not None
            if (val and val[0]!=None):
                bboxArray=bboxArray+[val[0]]
            if(val and val[2]!=[None]):
                timeArray=timeArray+[val[2]]
           
        #Copy from openfolder function in CLI tool 
        if len(bboxArray)!=0: 
            bboxes=bboxArray
            min_lon_list=[min_lon for min_lon, min_lat, max_lon, max_lat in bboxes]
            for x in min_lon_list:
                try:
                    if x<min_lon_all:
                        min_lon_all=x
                except NameError:
                    min_lon_all = x
            min_lat_list=[min_lat for min_lon, min_lat, max_lon, max_lat in bboxes]
            for x in min_lat_list:
                try:
                    if x<min_lat_all:
                        min_lat_all=x
                except NameError:
                    min_lat_all = x

            max_lon_list=[max_lon for min_lon, min_lat, max_lon, max_lat in bboxes]
            for x in max_lon_list:
                try:
                    if x>max_lon_all:
                        max_lon_all=x
                except NameError:
                    max_lon_all=x

            max_lat_list=[max_lat for min_lon, min_lat, max_lon, max_lat in bboxes]
            for x in max_lat_list:
                try:
                    if x>max_lat_all:
                        max_lat_all=x
                except NameError:
                    max_lat_all=x

            # bounding box of the entire folder
            folderbbox=[min_lon_all, min_lat_all, max_lon_all, max_lat_all]                        

        else:
            folderbbox=[None]

        if len(timeArray)!=0: 
            times=timeArray
            start_dates=[]
            end_dates=[]
            for z in times:
                start_dates.append(z[0])
                end_dates.append(z[1])
            min_date=min(start_dates)
            max_date=max(end_dates)
            folder_timeextend=[min_date, max_date]
            
            foldertime=folder_timeextend
        else:
            foldertime=[None]

        record['bbox']=[folderbbox,[None], foldertime]

    except Exception as e:
        print (e)

def index_versioned_record_siblings(sender, action=None, pid=None,
                                    deposit=None):
    """Send previous version of published record for indexing."""
    first_publish = (deposit.get('_deposit', {}).get('pid', {})
                     .get('revision_id')) == 0
    if action == "publish" and first_publish:
        recid_pid, _ = deposit.fetch_published()
        current_app.logger.info(u'indexing siblings of {}', recid_pid)
        index_siblings(recid_pid, neighbors_eager=True)