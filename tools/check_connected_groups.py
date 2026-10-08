# SPDX-License-Identifier: MIT
"""Validate source-specific evidence for connected groups without mutating media.

``check_connected_groups(document)`` returns True or raises ValueError. Missing
``rows`` and ``groups`` means no groups; ``rows`` takes precedence when both exist.
Single-ayah groups require no internal reviews. Connected groups require one
independent review for every internal boundary, tied to the recording hash.
Evidence is a nonblank string or a nonempty list/object. Evidence references
are checked for presence, not independently verified; passing does not establish
their accuracy or human listening approval.
"""

import argparse
import json
import math
from pathlib import Path


def _text(value, location):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location}: expected a nonblank string")
    return value


def _positive_integer(value, location):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{location}: expected a positive integer")
    return value


def _evidence(value, location):
    if isinstance(value, (list, dict)):
        if not value:
            raise ValueError(f"{location}: evidence cannot be empty")
    else:
        _text(value, location)


def _recording_hash(document):
    sources = document.get('sources', {})
    if not isinstance(sources, dict):
        raise ValueError("sources: expected an object")
    arabic = sources.get('Arabic', {})
    if not isinstance(arabic, dict):
        raise ValueError("sources.Arabic: expected an object")
    source_hash = document.get('source_sha256')
    fallback = arabic.get('sha256')
    if fallback is not None:
        _text(fallback, 'sources.Arabic.sha256')
    if source_hash is None:
        source_hash = fallback
    if source_hash is not None:
        _text(source_hash, 'source_sha256')
    return source_hash


def _review_window(value, location):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{location}: expected two numeric times in seconds")
    for endpoint in value:
        if (isinstance(endpoint, bool) or not isinstance(endpoint, (int, float))
                or (isinstance(endpoint, float) and not math.isfinite(endpoint))):
            raise ValueError(f"{location}: times must be finite numbers")
    start, end = value
    if not 0 <= start < end or end - start > 8:
        raise ValueError(f"{location}: require 0 <= start < end and at most 8 seconds")


def _check_group(group, source_hash, location):
    if not isinstance(group, dict):
        raise ValueError(f"{location}: expected an object")
    first = _positive_integer(group.get('ayah', group.get('from_ayah')),
                              f"{location}.ayah/from_ayah")
    if 'from_ayah' in group:
        alternate = _positive_integer(group['from_ayah'], f"{location}.from_ayah")
        if alternate != first:
            raise ValueError(f"{location}: ayah and from_ayah disagree")
    last = _positive_integer(group.get('to_ayah', first), f"{location}.to_ayah")
    if last < first:
        raise ValueError(f"{location}: to_ayah precedes the first ayah")
    records = group.get('internal_boundary_reviews', [])
    if not isinstance(records, list):
        raise ValueError(f"{location}.internal_boundary_reviews: expected an array")
    if len(records) != last - first:
        raise ValueError(f"{location}: every internal boundary requires one independent review")
    if first == last:
        return
    if source_hash is None:
        raise ValueError(f"{location}: missing recording hash")
    seen = set()
    for index, record in enumerate(records):
        review_location = f"{location}.internal_boundary_reviews[{index}]"
        if not isinstance(record, dict):
            raise ValueError(f"{review_location}: expected an object")
        boundary = _positive_integer(record.get('after_ayah'), f"{review_location}.after_ayah")
        if not first <= boundary < last or boundary in seen:
            raise ValueError(f"{review_location}: duplicate or out-of-range internal boundary")
        seen.add(boundary)
        if record.get('source_sha256') != source_hash:
            raise ValueError(f"{review_location}: review belongs to a different or missing source")
        if record.get('decision') != 'continuous':
            raise ValueError(f"{review_location}: split or unresolved boundary cannot remain connected")
        for field in ('outgoing_word', 'incoming_word'):
            _text(record.get(field), f"{review_location}.{field}")
        for field in ('word_context_evidence', 'signed_review_evidence'):
            _evidence(record.get(field), f"{review_location}.{field}")
        if record.get('reason') != 'actual_voiced_join_without_independent_stop':
            raise ValueError(f"{review_location}: actual voiced join evidence is required")
        if record.get('ASR_timing_used') is not False:
            raise ValueError(f"{review_location}: ASR_timing_used must be false; ASR timestamps are not cut anchors")
        _review_window(record.get('source_review_window'), f"{review_location}.source_review_window")


def check_connected_groups(document):
    """Return True for valid recorded evidence, otherwise raise ValueError."""
    if not isinstance(document, dict):
        raise ValueError("document: expected an object")
    for field in ('rows', 'groups'):
        if field in document and not isinstance(document[field], list):
            raise ValueError(f"{field}: expected an array")
    source_hash = _recording_hash(document)
    field = 'rows' if 'rows' in document else 'groups'
    for index, group in enumerate(document.get(field, [])):
        _check_group(group, source_hash, f"{field}[{index}]")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', type=Path, help='JSON document containing rows or groups')
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.document.read_text(encoding='utf-8'))
        check_connected_groups(document)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    print('Connected-group boundary evidence passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
