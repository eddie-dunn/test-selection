"""tests for avg_timesaving.py"""
# pylint: disable=missing-docstring

from avg_timesaving import get_test_sizes
from collections import OrderedDict as od

def test_get_test_sizes():
    data = od()
    data['mod1'] = {'test1': 1, "test2": 33}
    data['mod2'] = {'test2': 3, "test3": 31}
    data['mod3'] = {'test2': 3, "test3": 31, 'test4': 3}
    data['mod4'] = {'test2': 3, "test3": 31, 'test4': 3}
    data['mod5'] = {'test2': 3, "test3": 31, 'test4': 3}
    data['mod6'] = {'test2': 3, "test3": 31, 'test4': 3}
    data['mod7'] = {'test2': 3}
    test_sizes = get_test_sizes(data)
    assert test_sizes == [2, 2, 3, 3, 3, 3, 1]


def test_get_test_sizes1():
    data = {
        "apps/recording_indexer": {
            "test_syslog": 23,
            "recording_length_300s.local": 12,
            "recording_length_300s.external": 18,
            "test_always_multicast_cgi": 3,
            "test_the_rest": 3,
            "test_parse_core": 6,
            "discovery_tests": 8,
            "test_access_control": 8,
            "test_heater_state_machine": 1,},
        "apps/scm": {
            "test_syslog": 8,
            "recording_length_300s.local": 8,
            "recording_length_300s.external": 18,
            "test_the_rest": 4,
            "ptz_tests": 11,}
    }

    test_sizes = get_test_sizes(data)
    assert set(test_sizes) == set([9, 5])
