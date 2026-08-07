# Copyright 2026 The Waydroid Project
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
import secrets


_IDENTITY_FILE = "identity.json"


def luhn_check_digit(digits):
    total = 0
    parity = (len(digits) - 1) % 2
    for index, character in enumerate(digits):
        value = int(character)
        if index % 2 == parity:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return str((-total) % 10)


def _random_digits(length):
    return "".join(secrets.choice("0123456789") for _ in range(length))


def _new_identity():
    # Use conventional Chinese mobile prefixes while keeping every identifier
    # local to this Waydroid instance. IMEI and ICCID include Luhn check digits.
    imei_body = "35" + _random_digits(12)
    iccid_body = "898600" + _random_digits(13)
    return {
        "imei": imei_body + luhn_check_digit(imei_body),
        "imsi": "46000" + _random_digits(10),
        "iccid": iccid_body + luhn_check_digit(iccid_body),
        "serial": secrets.token_hex(4),
    }


def _valid_identity(identity):
    required_lengths = {
        "imei": 15,
        "imsi": 15,
        "iccid": 20,
        "serial": 8,
    }
    if not isinstance(identity, dict):
        return False
    for key, length in required_lengths.items():
        value = identity.get(key)
        if not isinstance(value, str) or len(value) != length:
            return False
    if not all(identity[key].isdigit() for key in ("imei", "imsi", "iccid")):
        return False
    if any(character not in "0123456789abcdef" for character in identity["serial"]):
        return False
    return (luhn_check_digit(identity["imei"][:-1]) == identity["imei"][-1]
            and luhn_check_digit(identity["iccid"][:-1]) == identity["iccid"][-1])


def load_or_create(work):
    path = os.path.join(work, _IDENTITY_FILE)
    try:
        with open(path, encoding="utf-8") as identity_file:
            identity = json.load(identity_file)
        if not _valid_identity(identity):
            raise RuntimeError("Waydroid identity file is invalid: " + path)
        return identity
    except FileNotFoundError:
        pass

    identity = _new_identity()
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError:
        return load_or_create(work)
    with os.fdopen(descriptor, "w", encoding="utf-8") as identity_file:
        json.dump(identity, identity_file, sort_keys=True)
        identity_file.write("\n")
    return identity
