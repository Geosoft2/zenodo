# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016, 2017 CERN.
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

"""UI for similarity page of a record."""

from __future__ import absolute_import, print_function, unicode_literals

import six
from flask import Blueprint, current_app, render_template, request

from invenio_records_ui.signals import record_viewed
from werkzeug.utils import import_string

blueprint = Blueprint(
    'zenodo_records',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/search'
)

def similar_records(pid, record, template=None, **kwargs):
    """Render similar records for given record
    
    Based on /home/daniel/git/zenodo-dev/zenodo/zenodo/config.py see records_ui_export
    """
    formats = current_app.config.get('ZENODO_RECORDS_EXPORTFORMATS')
    fmt = request.view_args.get('format')

    if formats.get(fmt) is None:
        return render_template(
            'zenodo_records/records_export_unsupported.html'), 410
    else:
        serializer = import_string(formats[fmt]['serializer'])
        data = serializer.serialize(pid, record)
        if isinstance(data, six.binary_type):
            data = data.decode('utf8')

        # emit record_viewed event
        record_viewed.send(
            current_app._get_current_object(),
            pid=pid,
            record=record,
        )
        return render_template(
            template, pid=pid, record=record,
            data=data, format_title=formats[fmt]['title'])
