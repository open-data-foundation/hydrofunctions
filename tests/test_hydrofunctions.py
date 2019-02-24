#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_hydrofunctions
----------------------------------

Tests for `hydrofunctions` module.
"""
from __future__ import absolute_import, print_function, division, unicode_literals
from unittest import mock
import unittest

import pandas as pd
import numpy as np

import hydrofunctions as hf
from .test_data import JSON15min2day, two_sites_two_params_iv, nothing_avail, mult_flags, diff_freq


class fakeResponse(object):

    def __init__(self, code=200):
        self.status_code = code
        self.url = "fake url"
        self.reason = "fake reason"
        # .json will return a function
        # .json() will return JSON15min2day
        self.json = lambda: JSON15min2day
        if code == 200:
            pass
        else:
            self.status_code = code

    def raise_for_status(self):
        return self.status_code


class TestHydrofunctionsParsing(unittest.TestCase):
    """Test the parsing of hf.extract_nwis_df()

    test the following:
        Can it handle multiple qualifier flags?
        how does it encode mult params & mult sites?
        Does it raise HydroNoDataError if nothing returned?

        """

    def test_hf_extract_nwis_df_accepts_response_obj(self):
        fake_response = fakeResponse()
        actual = hf.extract_nwis_df(fake_response, interpolate=False)
        self.assertIs(type(actual), pd.core.frame.DataFrame,
                      msg="Did not return a df")

    def test_hf_extract_nwis_df_parse_multiple_flags(self):
        actual = hf.extract_nwis_df(mult_flags, interpolate=False)
        self.assertIs(type(actual), pd.core.frame.DataFrame,
                      msg="Did not return a df")

    def test_hf_extract_nwis_df_parse_two_sites_two_params_iv_return_df(self):
        actual = hf.extract_nwis_df(two_sites_two_params_iv, interpolate=False)
        self.assertIs(type(actual), pd.core.frame.DataFrame,
                      msg="Did not return a df")
        #TODO: test that data is organized correctly

    def test_hf_extract_nwis_df_parse_two_sites_two_params_iv_return_df(self):
        actual = hf.extract_nwis_df(two_sites_two_params_iv, interpolate=False)
        actual_len, actual_width = actual.shape
        self.assertIs(type(actual), pd.core.frame.DataFrame,
                      msg="Did not return a df")
        self.assertEqual(actual_len, 93, "Wrong length for dataframe")
        self.assertEqual(actual_width, 8, "Wrong width for dataframe")
        expected_columns = ['USGS:01541000:00060:00000',
                            'USGS:01541000:00060:00000_qualifiers',
                            'USGS:01541000:00065:00000',
                            'USGS:01541000:00065:00000_qualifiers',
                            'USGS:01541200:00060:00000',
                            'USGS:01541200:00060:00000_qualifiers',
                            'USGS:01541200:00065:00000',
                            'USGS:01541200:00065:00000_qualifiers']
        actual_columns = actual.columns.values
        self.assertCountEqual(actual_columns, expected_columns,
                              "column names don't match expected")
        self.assertTrue(actual.index.is_unique, "index has repeated values.")
        self.assertTrue(actual.index.is_monotonic, "index is not monotonic.")

    def test_hf_extract_nwis_df_parse_JSON15min2day_return_df(self):
        actual = hf.extract_nwis_df(JSON15min2day, interpolate=False)
        actual_len, actual_width = actual.shape
        self.assertIs(type(actual), pd.core.frame.DataFrame,
                      msg="Did not return a df")
        self.assertEqual(actual_len, 192, "Wrong length for dataframe")
        self.assertEqual(actual_width, 2, "Wrong width for dataframe")
        expected_columns = ['USGS:03213700:00060:00000',
                            'USGS:03213700:00060:00000_qualifiers']
        actual_columns = actual.columns.values
        self.assertCountEqual(actual_columns, expected_columns,
                              "column names don't match expected")
        self.assertTrue(actual.index.is_unique, "index has repeated values.")
        self.assertTrue(actual.index.is_monotonic, "index is not monotonic.")

    def test_hf_extract_nwis_df_parse_mult_flags_return_df(self):
        actual = hf.extract_nwis_df(mult_flags, interpolate=False)
        actual_len, actual_width = actual.shape
        self.assertIs(type(actual), pd.core.frame.DataFrame,
                      msg="Did not return a df")
        self.assertEqual(actual_len, 480, "Wrong length for dataframe")
        self.assertEqual(actual_width, 2, "Wrong width for dataframe")
        expected_columns = ['USGS:01542500:00060:00000',
                            'USGS:01542500:00060:00000_qualifiers']
        actual_columns = actual.columns.values
        self.assertCountEqual(actual_columns, expected_columns,
                              "column names don't match expected")
        self.assertTrue(actual.index.is_unique, "index has repeated values.")
        self.assertTrue(actual.index.is_monotonic, "index is not monotonic.")

    def test_hf_extract_nwis_raises_exception_when_df_is_empty(self):
        empty_response = {'value': {'timeSeries': []}}
        with self.assertRaises(hf.HydroNoDataError):
            hf.extract_nwis_df(empty_response, interpolate=False)

    def test_hf_extract_nwis_raises_exception_when_df_is_empty_nothing_avail(self):
        with self.assertRaises(hf.HydroNoDataError):
            hf.extract_nwis_df(nothing_avail, interpolate=False)

    def test_hf_extract_nwis_warns_when_diff_series_have_diff_freq(self):
        with self.assertWarns(hf.HydroUserWarning):
            hf.extract_nwis_df(diff_freq, interpolate=False)

    def test_hf_extract_nwis_returns_comma_separated_qualifiers_1(self):
        actual = hf.extract_nwis_df(mult_flags, interpolate=False)
        actual_flags_1 = actual.loc['2019-01-24T10:30:00.000-05:00', 'USGS:01542500:00060:00000_qualifiers']
        expected_flags_1 = 'P,e'
        self.assertEqual(actual_flags_1, expected_flags_1, "The data qualifier flags were not parsed correctly.")

    def test_hf_extract_nwis_returns_comma_separated_qualifiers_2(self):
        actual = hf.extract_nwis_df(mult_flags, interpolate=False)
        actual_flags_2 = actual.loc['2019-01-28T16:00:00.000-05:00', 'USGS:01542500:00060:00000_qualifiers']
        expected_flags_2 = 'P,Ice'
        self.assertEqual(actual_flags_2, expected_flags_2, "The data qualifier flags were not parsed correctly.")

    def test_hf_extract_nwis_replaces_NWIS_noDataValue_with_npNan(self):
        actual = hf.extract_nwis_df(mult_flags, interpolate=False)
        actual_nodata = actual.loc['2019-01-28T16:00:00.000-05:00', 'USGS:01542500:00060:00000']
        self.assertTrue(np.isnan(actual_nodata), "The NWIS no data value was not replaced with np.nan. ")

    def test_hf_extract_nwis_adds_missing_tags(self):
        actual = hf.extract_nwis_df(mult_flags, interpolate=False)
        actual_missing = actual.loc['2019-01-24 17:00:00-05:00', 'USGS:01542500:00060:00000_qualifiers']
        self.assertEqual(actual_missing, 'hf.missing', "Missing records should be given 'hf.missing' _qualifier tags.")

    def test_hf_extract_nwis_adds_upsample_tags(self):
        actual = hf.extract_nwis_df(diff_freq, interpolate=False)
        actual_upsample = actual.loc['2018-06-01 00:15:00-04:00', 'USGS:01570500:00060:00000_qualifiers']
        self.assertEqual(actual_upsample, 'hf.upsampled', "New records created by upsampling should be given 'hf.upsample' _qualifier tags.")

    def test_hf_extract_nwis_interpolates(self):
        actual = hf.extract_nwis_df(diff_freq, interpolate=True)
        actual_upsample_interpolate = actual.loc['2018-06-01 00:15:00-04:00', 'USGS:01570500:00060:00000']
        self.assertEqual(actual_upsample_interpolate, 42200.0, "New records created by upsampling should have NaNs replaced with interpolated values.")

    @unittest.skip("This feature is not implemented yet.")
    def test_hf_extract_nwis_interpolates_and_adds_tags(self):
        # Ideally, every data value that was interpolated should have a tag
        # added to the qualifiers that says it was interpolated.
        actual = hf.extract_nwis_df(diff_freq, interpolate=True)
        actual_upsample_interpolate_flag = actual.loc['2018-06-01 00:15:00-04:00', 'USGS:01570500:00060:00000_qualifiers']
        expected_flag = "hf.interpolated"
        self.assertEqual(actual_upsample_interpolate_flag, expected_flag, "Interpolated values should be marked with a flag.")

    def test_hf_get_nwis_property(self):
        sites = None
        bBox = (-105.430, 39.655, -104, 39.863)
        # TODO: test should be the json for a multiple site request.
        names = hf.get_nwis_property(JSON15min2day, key='name')
        self.assertIs(type(names), list, msg="Did not return a list")


class TestHydrofunctions(unittest.TestCase):

    @mock.patch('requests.get')
    def test_hf_get_nwis_calls_correct_url(self, mock_get):

        """
        Thanks to
        http://engineroom.trackmaven.com/blog/making-a-mockery-of-python/
        """

        site = 'A'
        service = 'iv'
        start = 'C'
        end = 'D'

        expected_url = 'https://waterservices.usgs.gov/nwis/'+service+'/?'
        expected_headers = {'Accept-encoding': 'gzip', 'max-age': '120'}
        expected_params = {'format': 'json,1.1', 'sites': 'A', 'stateCd': None,
                           'countyCd': None, 'bBox': None,
                           'parameterCd': None, 'period': None,
                           'startDT': 'C', 'endDT': 'D'}

        expected = fakeResponse()
        expected.status_code = 200
        expected.reason = "any text"

        mock_get.return_value = expected
        actual = hf.get_nwis(site, service, start, end)
        mock_get.assert_called_once_with(expected_url, params=expected_params,
                                         headers=expected_headers)
        self.assertEqual(actual, expected)

    @mock.patch('requests.get')
    def test_hf_get_nwis_calls_correct_url_multiple_sites(self, mock_get):

        site = ['site1', 'site2']
        parsed_site = hf.check_parameter_string(site, 'site')
        service = 'iv'
        start = 'C'
        end = 'D'

        expected_url = 'https://waterservices.usgs.gov/nwis/'+service+'/?'
        expected_headers = {'max-age': '120', 'Accept-encoding': 'gzip'}
        expected_params = {'format': 'json,1.1', 'sites': parsed_site,
                           'stateCd': None, 'countyCd': None,
                           'bBox': None, 'parameterCd': None,
                           'period': None, 'startDT': 'C', 'endDT': 'D'}

        expected = fakeResponse()
        expected.status_code = 200
        expected.reason = "any text"

        mock_get.return_value = expected
        actual = hf.get_nwis(site, service, start, end)
        mock_get.assert_called_once_with(expected_url, params=expected_params,
                                         headers=expected_headers)
        self.assertEqual(actual, expected)

    @mock.patch('requests.get')
    def test_hf_get_nwis_service_defaults_dv(self, mock_get):
        site = '01541200'
        expected_service = 'dv'

        expected_url = 'https://waterservices.usgs.gov/nwis/'+expected_service+'/?'
        expected_headers = {'max-age': '120', 'Accept-encoding': 'gzip'}
        expected_params = {'format': 'json,1.1', 'sites': site,
                           'stateCd': None, 'countyCd': None,
                           'bBox': None, 'parameterCd': None,
                           'period': None, 'startDT': None, 'endDT': None}
        expected = fakeResponse()
        expected.status_code = 200
        expected.reason = "any text"

        mock_get.return_value = expected
        actual = hf.get_nwis(site)
        mock_get.assert_called_once_with(expected_url, params=expected_params,
                                         headers=expected_headers)
        self.assertEqual(actual, expected)

    @mock.patch('requests.get')
    def test_hf_get_nwis_converts_parameterCd_all_to_None(self, mock_get):
        site = '01541200'
        service = 'iv'
        parameterCd = 'all'
        expected_parameterCd = None
        expected_url = 'https://waterservices.usgs.gov/nwis/'+service+'/?'
        expected_headers = {'max-age': '120', 'Accept-encoding': 'gzip'}
        expected_params = {'format': 'json,1.1', 'sites': site,
                           'stateCd': None, 'countyCd': None,
                           'bBox': None, 'parameterCd': None,
                           'period': None, 'startDT': None, 'endDT': None}
        expected = fakeResponse()
        expected.status_code = 200
        expected.reason = "any text"

        mock_get.return_value = expected
        actual = hf.get_nwis(site, service, parameterCd=parameterCd)
        mock_get.assert_called_once_with(expected_url, params=expected_params,
                                         headers=expected_headers)
        self.assertEqual(actual, expected)

    def test_hf_get_nwis_raises_ValueError_too_many_locations(self):
        with self.assertRaises(ValueError):
            hf.get_nwis('01541000', stateCd='MD')

    def test_hf_get_nwis_raises_ValueError_start_and_period(self):
        with self.assertRaises(ValueError):
            hf.get_nwis('01541000', start_date='2014-01-01', period='P1D')

    def test_hf_nwis_custom_status_codes_returns_None_for_200(self):
        fake = fakeResponse()
        fake.status_code = 200
        fake.reason = "any text"
        fake.url = "any text"
        self.assertIsNone(hf.nwis_custom_status_codes(fake))

    def test_hf_nwis_custom_status_codes_returns_status_for_non200(self):
        bad_response = fakeResponse()
        bad_response.status_code = 400
        bad_response.reason = "any text"
        bad_response.url = "any text"
        expected = 400
        # bad_response should raise a warning that should be caught during test
        actual = None
        with self.assertWarns(SyntaxWarning) as cm:
            actual = hf.nwis_custom_status_codes(bad_response)
        # Does the function return the bad status_code?
        self.assertEqual(actual, expected)

    def test_hf_select_data_returns_data_cols(self):
        DF = hf.extract_nwis_df(two_sites_two_params_iv)
        actual = hf.select_data(DF)
        expected = [False, True, False, True, False, True, False, True]
        self.assertListEqual(actual.tolist(), expected, "select_data should return an array of which columns contain the data, not the qualifiers.")

if __name__ == '__main__':
    unittest.main(verbosity=2)
