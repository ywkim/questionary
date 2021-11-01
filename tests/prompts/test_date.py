# -*- coding: utf-8 -*-
"""Testsuite for date module."""
from typing import List

import datetime

import prompt_toolkit
from prompt_toolkit.validation import ValidationError
import pytest
from prompt_toolkit import document
from prompt_toolkit.completion.base import CompleteEvent

from questionary.prompts import date
from tests.utils import KeyInputs, feed_cli_with_input


def _check_simple_completions(
    date_format: str, text_inputs: List[str], order: List[str], delimeter: str
) -> None:
    """Checks completions of `SimpleDateCompleter`.

    Completions should follow the order of ``order`` and use the delimeter
    ``delimeter``.

    Args:
        date_format (str): The ``date_format`` for the :class: `SimpleDateCompleter`.
        text_inputs (str): Several text inputs that are given to the completer.
        order (List[str]): Expected order of completions. Needs to be of the same length
            as ``text_inputs``.
        delimeter (str): The expected seperating delimeter.

    Raises:
        ValueError: if ``order`` and ``text_inputs`` are not of the same length.
    """
    if len(text_inputs) != len(order):
        raise (
            ValueError(
                "'tect_inputs' and 'order' need to have the same number of items."
            )
        )

    # create ``Completer``
    completer = date.SimpleDateCompleter(date_format=date_format)

    def _returns_expected_completions(
        text: str, options: List[str], delimeter: str
    ) -> None:
        """Checks if completions for ``text`` are in ``options``."""
        input = document.Document(text)
        # check if completions are expected ones
        for completion in completer.get_completions(
            document=input, complete_event=CompleteEvent()
        ):
            assert completion.text in map(lambda x: x + delimeter, options)

    # last entry should use no delimeter
    delimeters: List[str] = [delimeter for _ in range(len(text_inputs) - 1)] + [""]
    for i in range(len(order)):
        _returns_expected_completions(
            text=text_inputs[i], options=order[i], delimeter=delimeters[i]
        )


def test_simple_date_completer():
    """Yields completions depending on the chosen ``date_format``."""
    # check order of completions
    _check_simple_completions(
        date_format=date.ISO8601,
        text_inputs=["202", "2021-02", "2021-02-02"],
        order=[date.YEAR, date.MONTH, date.DAY],
        delimeter="-",
    )

    # check order of completions for other format
    _check_simple_completions(
        date_format=date.ISO8601_TIME,
        text_inputs=["20", "20:02", "2021:02:02"],
        order=[date.HOUR, date.MINUTE, date.SECOND],
        delimeter=":",
    )


def test_simple_date_completer_exception():
    """Raises ``ValueError``, if ``date_format`` is not supported."""
    # supported date_formats are allowed
    for date_format in date.SUPPORTED_FORMATS:
        date.SimpleDateCompleter(date_format=date_format)

    # not supported ones make it raise ``ValueError``
    with pytest.raises(ValueError):
        date.SimpleDateCompleter(date_format="not-supported")


def test_simple_date_validator_exception():
    """Raises ``ValueError``, if ``date_format`` is not supported."""
    # supported date_formats are allowed
    for date_format in date.SUPPORTED_FORMATS:
        date.SimpleDateValidator(date_format=date_format)

    # not supported ones make it raise ``ValueError``
    with pytest.raises(ValueError):
        date.SimpleDateValidator(date_format="not-supported")


def test_parsing_completer():
    """Completion using a custom date parser."""
    completer = date.ParsingDateCompleter(parser=date.custom_date_parser)
    input = document.Document("2021")
    completions = [c.text for c in completer.get_completions(input, CompleteEvent())]
    assert "2021-01-01 00:00:00" in completions


def test_parsing_completer_exception():
    """Parser needs to be a callable or None."""
    date.ParsingDateCompleter()

    with pytest.raises(ValueError):
        date.ParsingDateCompleter(parser="i am not a callable")


def test_parsing_validator():
    """Validaton using a custom date parser."""
    validator = date.ParsingDateValidator(parser=date.custom_date_parser)
    input = document.Document("2021")
    validator.validate(input)

    # raises if date cannot be validated
    with pytest.raises(ValidationError):
        validator.validate(document.Document("invalid"))


def test_parsing_validator_init_exception():
    """Parser needs to be a callable or None."""
    date.ParsingDateValidator()

    with pytest.raises(ValueError):
        date.ParsingDateValidator(parser="i am not a callable")


def test_date():
    """Test date on default behavior."""
    message = "Type a date: "
    text = "2021-01-01" + KeyInputs.ENTER
    result, cli = feed_cli_with_input("date", message, text)
    assert result == datetime.datetime(2021, 1, 1, 0, 0)


def test_date_string_return():
    """Date may return a string."""
    message = "Type a date: "
    text = "2021-01-01" + KeyInputs.ENTER
    result, cli = feed_cli_with_input("date", message, text, return_date_object=False)
    assert result == "2021-01-01"
