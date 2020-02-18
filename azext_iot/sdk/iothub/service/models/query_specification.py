# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class QuerySpecification(Model):
    """A Json query request.

    :param query: The query.
    :type query: str
    """

    _attribute_map = {
        'query': {'key': 'query', 'type': 'str'},
    }

    def __init__(self, **kwargs):
        super(QuerySpecification, self).__init__(**kwargs)
        self.query = kwargs.get('query', None)
