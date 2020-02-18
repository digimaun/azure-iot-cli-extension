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


class AuthenticationMechanism(Model):
    """AuthenticationMechanism.

    :param symmetric_key:
    :type symmetric_key: ~service.models.SymmetricKey
    :param x509_thumbprint:
    :type x509_thumbprint: ~service.models.X509Thumbprint
    :param type: Possible values include: 'sas', 'selfSigned',
     'certificateAuthority', 'none'
    :type type: str or ~service.models.enum
    """

    _attribute_map = {
        'symmetric_key': {'key': 'symmetricKey', 'type': 'SymmetricKey'},
        'x509_thumbprint': {'key': 'x509Thumbprint', 'type': 'X509Thumbprint'},
        'type': {'key': 'type', 'type': 'str'},
    }

    def __init__(self, **kwargs):
        super(AuthenticationMechanism, self).__init__(**kwargs)
        self.symmetric_key = kwargs.get('symmetric_key', None)
        self.x509_thumbprint = kwargs.get('x509_thumbprint', None)
        self.type = kwargs.get('type', None)
