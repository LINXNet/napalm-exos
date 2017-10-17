# Copyright 2016 LINX. All rights reserved.
#
# The contents of this file are licensed under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.


from pyEXOS import EXOS

from napalm_base.base import NetworkDriver
from napalm_base.exceptions import (
    ConnectionException,
    MergeConfigException,
    ReplaceConfigException,
    )


class ExosDriver(NetworkDriver):
    """Napalm driver for Exos."""

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """Constructor."""
        self.device = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout
        self.loaded = False
        self.replace = False
        self.changed = False

        if optional_args is None:
            optional_args = {}

        self.port = optional_args.get('port', 22)

    def open(self):
        """Implementation of NAPALM method open."""
        try:
            self.device = EXOS(
                hostname=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
                timeout=self.timeout)
            self.device.open()
        except Exception:
            raise ConnectionException("Unable to connect to {0}".format(self.hostname))

    def close(self):
        """Implementation of NAPALM method close."""
        self.device.close()

    def is_alive(self):
        """Implementation of NAPALM method is_alive."""
        return self.device.is_alive()

    def load_merge_candidate(self, filename=None, config=None):
        """Implementation of NAPALM method load_merge_candidate."""
        self.device.load_candidate_config(filename=filename, config=config)
        self.loaded = True
        self.replace = False

    def load_replace_candidate(self, filename=None, config=None):
        """Implementation of NAPALM method load_replace_candidate."""
        self.device.load_candidate_config(filename=filename, config=config)
        self.loaded = True
        self.replace = True

    def compare_config(self):
        """Implementation of NAPALM method compare_config."""
        if self.loaded:
            if self.replace:
                return self.device.compare_replace_config()
            else:
                return self.device.compare_merge_config()
        else:
            return ''

    def commit_config(self):
        """Implementation of NAPALM method commit_config."""
        if self.loaded:
            if self.replace:
                try:
                    self.device.commit_replace_config()
                except Exception as e:
                    self.device.rollback()
                    raise ReplaceConfigException(str(e))
            else:
                try:
                    self.device.commit_config()
                except Exception as e:
                    self.device.rollback()
                    raise MergeConfigException(str(e))
        else:
            raise MergeConfigException('No config loaded.')

        self.changed = True
        self.loaded = False

    def discard_config(self):
        """Implementation of NAPALM method discard_config."""
        if self.loaded:
            self.device.discard_config()
        self.loaded = False

    def rollback(self):
        """Implementation of NAPALM method rollback."""
        if self.changed:
            self.device.rollback()
        self.changed = False
