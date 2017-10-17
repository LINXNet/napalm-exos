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

"""Tests."""

import unittest
from unittest import SkipTest

from napalm_exos import exos
from napalm_base import exceptions
from napalm_base.test.base import TestConfigNetworkDriver


class TestConfigExosDriver(unittest.TestCase, TestConfigNetworkDriver):
    """Group of tests that test Configuration related methods."""

    @classmethod
    def setUpClass(cls):
        """Run before starting the tests."""
        hostname = '192.168.56.101'
        username = 'admin'
        password = ''
        cls.vendor = 'exos'

        cls.device = exos.ExosDriver(hostname, username, password, timeout=60,
                                     optional_args={})
        cls.device.open()

        cls.device.load_replace_candidate(filename='%s/initial.conf' % cls.vendor)
        cls.device.commit_config()

    def test_replacing_config_with_typo(self):
        result = False
        try:
            self.device.load_replace_candidate(filename='%s/new_typo.conf' % self.vendor)
            self.device.commit_config()
        except NotImplementedError:
            raise SkipTest()
        except exceptions.ReplaceConfigException:
            self.device.load_replace_candidate(filename='%s/initial.conf' % self.vendor)
            diff = self.device.compare_config()
            intended_diff = self.read_file('%s/initial.diff' % self.vendor)
            self.device.discard_config()
            result = True and (diff == intended_diff)
        self.assertTrue(result)

    def test_merge_configuration_typo_and_rollback(self):
        result = False
        try:
            self.device.load_merge_candidate(filename='%s/merge_typo.conf' % self.vendor)
            self.device.compare_config()
            self.device.commit_config()
            raise Exception("We shouldn't be here")
        except exceptions.MergeConfigException:
            self.device.load_replace_candidate(filename='%s/initial.conf' % self.vendor)
            intended_diff = self.read_file('%s/initial.diff' % self.vendor)
            result = self.device.compare_config() == intended_diff
            self.device.discard_config()

        self.assertTrue(result)
