# SPDX-License-Identifier: MIT
"""Synthetic connected-group validator tests; no production source data."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'check_connected_groups.py'
SPEC = importlib.util.spec_from_file_location('check_connected_groups', TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
check_connected_groups = MODULE.check_connected_groups


def valid_document():
    source_hash = 'a' * 64
    return {'source_sha256': source_hash, 'rows': [{
        'ayah': 1, 'to_ayah': 3,
        'internal_boundary_reviews': [{
            'after_ayah': boundary,
            'source_sha256': source_hash,
            'decision': 'continuous',
            'outgoing_word': 'synthetic outgoing token',
            'incoming_word': 'synthetic incoming token',
            'word_context_evidence': 'Synthetic context review record',
            'signed_review_evidence': 'Synthetic waveform review record',
            'reason': 'actual_voiced_join_without_independent_stop',
            'ASR_timing_used': False,
            'source_review_window': [0.0, 8.0],
        } for boundary in (1, 2)],
    }]}


class ConnectedGroupTests(unittest.TestCase):
    def test_valid_document_is_not_mutated(self):
        document = valid_document()
        original = copy.deepcopy(document)
        self.assertIs(check_connected_groups(document), True)
        self.assertEqual(document, original)

    def test_missing_empty_and_single_groups_remain_valid(self):
        for document in ({}, {'rows': []}, {'groups': []}, {'rows': [{'ayah': 1}]},
                         {'groups': [{'from_ayah': 1, 'to_ayah': 1}]},
                         {'rows': [], 'groups': [{'from_ayah': 1, 'to_ayah': 2}]}):
            with self.subTest(document=document):
                self.assertIs(check_connected_groups(document), True)

    def test_groups_alias_fallback_hash_and_multiple_evidence_references(self):
        document = valid_document()
        document['sources'] = {'Arabic': {'sha256': document.pop('source_sha256')}}
        document['groups'] = document.pop('rows')
        group = document['groups'][0]
        group['from_ayah'] = group.pop('ayah')
        group['internal_boundary_reviews'].reverse()
        group['internal_boundary_reviews'][0]['signed_review_evidence'] = ['Review one', 'Review two']
        self.assertIs(check_connected_groups(document), True)

    def test_structured_evidence_remains_valid(self):
        for evidence in ({'reference': 'Synthetic review'}, [{'reference': 'Synthetic review'}]):
            document = valid_document()
            record = document['rows'][0]['internal_boundary_reviews'][0]
            record['word_context_evidence'] = evidence
            record['signed_review_evidence'] = evidence
            with self.subTest(evidence=evidence):
                self.assertIs(check_connected_groups(document), True)

    def test_malformed_document_or_collection(self):
        for document in (None, [], 'text', 1, {'rows': None}, {'groups': {}},
                         {'rows': [] , 'groups': None}, {'sources': []},
                         {'sources': {'Arabic': []}}, {'source_sha256': 7},
                         {'source_sha256': '  '}):
            with self.subTest(document=document):
                with self.assertRaises(ValueError):
                    check_connected_groups(document)

    def test_malformed_groups(self):
        for group in (None, [], 'text', {}, {'ayah': True}, {'ayah': 1.0},
                      {'ayah': 0}, {'ayah': -1}, {'ayah': 2, 'to_ayah': 1},
                      {'ayah': 1, 'to_ayah': False}, {'ayah': 1, 'to_ayah': float('inf')},
                      {'ayah': 1, 'from_ayah': 2}, {'ayah': 1, 'internal_boundary_reviews': None},
                      {'ayah': 1, 'internal_boundary_reviews': [{}]}):
            with self.subTest(group=group):
                with self.assertRaises(ValueError):
                    check_connected_groups({'rows': [group]})

    def test_required_recording_hash(self):
        document = valid_document()
        del document['source_sha256']
        with self.assertRaisesRegex(ValueError, 'recording hash'):
            check_connected_groups(document)

    def test_independent_complete_boundary_coverage(self):
        variants = ([], None, {}, [None, None], [{}, {}])
        for records in variants:
            document = valid_document()
            document['rows'][0]['internal_boundary_reviews'] = records
            with self.subTest(records=records):
                with self.assertRaises(ValueError):
                    check_connected_groups(document)
        for boundary in (1, 3, True, 1.5, '2', None):
            document = valid_document()
            document['rows'][0]['internal_boundary_reviews'][1]['after_ayah'] = boundary
            with self.subTest(boundary=boundary):
                with self.assertRaises(ValueError):
                    check_connected_groups(document)

    def test_missing_evidence_fields_are_rejected(self):
        for field in valid_document()['rows'][0]['internal_boundary_reviews'][0]:
            document = valid_document()
            del document['rows'][0]['internal_boundary_reviews'][0][field]
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    check_connected_groups(document)

    def test_invalid_evidence_is_rejected(self):
        cases = {
            'source_sha256': ['b' * 64, '', None, 1],
            'decision': ['split', 'pending', None],
            'outgoing_word': ['', '  ', 1, ['word']],
            'incoming_word': ['', '  ', False],
            'word_context_evidence': ['', '  ', [], True, 1, {}],
            'signed_review_evidence': ['', '  ', [], False, 1, {}],
            'reason': ['region identity', '', None],
            'ASR_timing_used': [True, 0, None, 'false'],
        }
        for field, values in cases.items():
            for value in values:
                document = valid_document()
                document['rows'][0]['internal_boundary_reviews'][0][field] = value
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValueError):
                        check_connected_groups(document)

    def test_invalid_windows_are_rejected(self):
        windows = (None, [], [0], [0, 1, 2], '01', {'start': 0, 'end': 1},
                   [-1, 1], [1, 1], [2, 1], [0, 8.01], [False, 1], [0, True],
                   ['0', 1], [0, float('inf')], [float('-inf'), 1],
                   [float('nan'), 1], [0, float('nan')], [0, 10 ** 400])
        for window in windows:
            document = valid_document()
            document['rows'][0]['internal_boundary_reviews'][0]['source_review_window'] = window
            with self.subTest(window=window):
                with self.assertRaises(ValueError):
                    check_connected_groups(document)

    def test_cli_valid_and_invalid_under_optimization(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic.json'
            for optimized in (False, True):
                command = [sys.executable, '-B'] + (['-O'] if optimized else []) + [str(TOOL), str(path)]
                path.write_text(json.dumps(valid_document()), encoding='utf-8')
                success = subprocess.run(command, capture_output=True, text=True, check=False)
                self.assertEqual(success.returncode, 0, success.stderr)
                self.assertIn('evidence passed', success.stdout)
                invalid = valid_document()
                invalid['rows'][0]['internal_boundary_reviews'][0]['ASR_timing_used'] = True
                path.write_text(json.dumps(invalid), encoding='utf-8')
                failed = subprocess.run(command, capture_output=True, text=True, check=False)
                self.assertNotEqual(failed.returncode, 0)
                self.assertIn('ASR_timing_used must be false', failed.stderr)
                self.assertNotIn('passed', failed.stdout)
                self.assertNotIn('Traceback', failed.stderr)

    def test_cli_malformed_json_and_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic.json'
            command = [sys.executable, '-B', str(TOOL), str(path)]
            for content in (None, '{', '[]'):
                if content is not None:
                    path.write_text(content, encoding='utf-8')
                result = subprocess.run(command, capture_output=True, text=True, check=False)
                with self.subTest(content=content):
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn('Traceback', result.stderr)
                    self.assertNotIn('passed', result.stdout)


if __name__ == '__main__':
    unittest.main()
