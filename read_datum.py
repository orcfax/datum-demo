"""Single-script demo to show how to access on on-chain datum."""
# pylint: disable=W0718, C0206

import json
import logging
import sys
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Final

import cbor2
import numpy
import pycardano
import requests
from pycardano import Address, Network, OgmiosChainContext, UTxO

OGMIOS_URL: Final[str] = "ws://ogmios.preprod.orcfax.io:1337"

# plutus chain index api
PLUTUS_CHAIN_INDEX_API: Final[
    str
] = "http://plutus-chain-index.preprod.orcfax.io:9084/tx"

# smart contract
ADA_USD_ORACLE_ADDR: Final[
    str
] = "addr_test1wrtcecfy7np3sduzn99ffuv8qx2sa8v977l0xql8ca7lgkgmktuc0"

auth_addr = Address.from_primitive(
    "addr_test1vrc7lrdcsz08vxuj4278aeyn4g82salal76l54gr6rw4ync86tfse"
)

# policy ID for the Auth tokens
AUTH_POLICY: Final[str] = "5ec8416ecd8af5fe338068b2aee00a028dc1f4c0cd5978fb86d7c038"

network = Network.TESTNET
context = OgmiosChainContext(ws_url=OGMIOS_URL, network=network)

logger = logging.getLogger(__name__)

logging.basicConfig(
    format="%(asctime)-15s %(levelname)s :: %(filename)s:%(lineno)s:%(funcName)s() :: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    level="INFO",
)


@dataclass
class PricePair:
    """Stores our values."""

    ada_usd: int
    usd_ada: int


def display_utxo(utxo: pycardano.transaction.UTxO):
    """Display the details in a UTxO.

    Example UTxO:

    ```json
        {'input': {
        'index': 0,
        'transaction_id': TransactionId(hex='6812900646a00e1cf994e969bed7dd6556950cafbea23d773cb9d61b278f05cc'),
        }, 'output': {
        'address': addr_test1wrtcecfy7np3sduzn99ffuv8qx2sa8v977l0xql8ca7lgkgmktuc0,
        'amount': {
            'coin': 3413520,
            'multi_asset': {ScriptHash(hex='104d51dd927761bf5d50d32e1ede4b2cff477d475fe32f4f780a4b21'): {AssetName(b'\xcc\x02\xc7,\xb3\xef\x8e8\x99Vy\x95\x85\xc0Y\x04S\xf3\xec\xcfpO\xe5\xd7\xdd\xa2\xcbb/\x8b2u'): 1}},
        },
        'datum': RawCBOR(cbor=b'\xd8y\x9f\xa7H@contextRhttps://schema.orgR_:contentSignatureX@d10c6c3167060a8e82f2c1a8bb8b271ec796f3379a2473d522e478aabd1f6a5fJidentifier\xa3JpropertyIDPArkly IdentifierDtypeMPropertyValueEvalueX/urn:orcfax:d72786af-d8fa-4488-8f53-d4578b2f6f23DnameOADA-USD|USD-ADADtypeMPropertyValueEvalue\x9f\xd8|\x9f\x19_\x9b\x1b\xff\xff\xff\xff\xff\xff\xff\xfb\xff\xd8|\x9f\x1b\x00\x0e\x84\x03\xdf6\x89\x8b\x1b\xff\xff\xff\xff\xff\xff\xff\xf1\xff\xffNvalueReference\x9f\xa3E@typeMPropertyValueDnameIvalidFromEvalue\x1b\x00\x00\x01\x8a\xbc-\x9e\x85\xa3E@typeMPropertyValueDnameLvalidThroughEvalue\x1b\x00\x00\x01\x8a\xbcd\x8d\x05\xffX 04CA0001HAY2VBEC6PP7P1DSEA2V2VHY\xd8z\x9f\x1b\x00\x00\x01\x8a\xbcd\x8d\x05\xffX\x1c\x90\xb1!\xaakh\x92\x00\xad\xf7\xed\x11P@\xa9cu\xd2\xb6\x8e#c=hd\xc5:\x91\xff'),
        'datum_hash': None,
        'post_alonzo': False,
        'script': None,
        }}
    ```
    """
    logger.info("(input) transaction id: %s", str(utxo.input.transaction_id))
    logger.info("(output) transaction addr: %s", str(utxo.output.address))
    logger.info(
        "(output) datum cbor:\n\n%s\n", cbor2.dumps(utxo.output.datum.cbor).hex()
    )
    logger.info("(output) Tx cost: %s ADA", utxo.output.amount.coin / 1000000)


def _decode_number(value_pair: list):
    """Decode a number value."""
    significand = numpy.uint64(value_pair[0]).astype(numpy.int64)
    base10_component = numpy.uint64(value_pair[1]).astype(numpy.int64)
    value = significand * 10 ** numpy.float_(base10_component)
    return value


def decode_datum_bytes(json_datum: dict):
    """Decode a datum's key/value pairs from their respective
    encodings.
    """
    decoded = {}
    for key, value in json_datum.items():
        if isinstance(value, list):
            item_list = []
            if key.decode() == "value":
                if len(value) == 2:
                    for value_pair in value:
                        item_list.append(_decode_number(value_pair.value))
                decoded[key.decode()] = item_list
                continue
            for item in value:
                if isinstance(item, cbor2.CBORTag):
                    item_list.append(item.value)
                if isinstance(item, dict):
                    item_list.append(decode_datum_bytes(item))
            decoded[key.decode()] = item_list
            continue
        try:
            decoded[key.decode()] = value.decode()
        except AttributeError:
            if isinstance(value, int):
                decoded[key.decode()] = value
                continue
            decoded[key.decode()] = decode_datum_bytes(value)
    return decoded


def _recombine_datum(json_datum: dict):
    """Recombine the datum in a more familiar order.

    The dictionary order isn't guaranteed to be preserved when placed
    on-chain. We do the necessary gymnastics here to reorder it.
    """
    new_datum = OrderedDict()
    new_datum["@context"] = json_datum["@context"]
    new_datum["type"] = json_datum["type"]
    new_datum["name"] = json_datum["name"]
    new_datum["value"] = json_datum["value"]
    new_datum["valueReference"] = json_datum["valueReference"]
    new_datum["identifier"] = json_datum["identifier"]
    new_datum["_:contentSignature"] = json_datum["_:contentSignature"]
    return new_datum


def decode_utxo(utxo: pycardano.transaction.UTxO):
    """Split a UTxO into the components that we need to process and
    initially return the Orcfax Datum."""
    oracle_datum = cbor2.loads(utxo.output.datum.cbor)
    # datum value full -- oracle_datum.value
    json_datum = oracle_datum.value[0]
    json_datum = decode_datum_bytes(json_datum)
    json_datum = _recombine_datum(json_datum)
    logger.info("\n\n%s\n", json.dumps(json_datum, indent=2))
    logger.info("oracle datum identifier (internal): %s", oracle_datum.value[1])
    timestamp = oracle_datum.value[2].value[0]
    timestamp_human = datetime.utcfromtimestamp(int(timestamp) / 1000).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    logger.info("oracle datum timestamp: %s (%s)", timestamp_human, timestamp)
    labels = oracle_datum.value[0][b"name"].decode().split("|", 1)
    ada_usd_value = oracle_datum.value[0][b"value"][0].value
    usd_ada_value = oracle_datum.value[0][b"value"][1].value
    price_pair = PricePair(ada_usd=ada_usd_value, usd_ada=usd_ada_value)
    pretty_log_value(ada_usd_value, labels[0])
    pretty_log_value(usd_ada_value, labels[1])
    return price_pair


def pretty_log_value(value_pair: cbor2.CBORTag, label: str):
    """Return pretty logging information about a value pair."""
    value = _decode_number(value_pair)
    logger.info("%s: %s", label, value)


def get_tx_info(tx_id: str):
    """Return the transaction information from the plutus chain index api"""
    data = {"getTxId": tx_id}
    headers = {"Content-type": "application/json"}
    try:
        tx_info = json.loads(
            requests.post(
                PLUTUS_CHAIN_INDEX_API, json=data, headers=headers, timeout=30
            ).text
        )
    except Exception as exc:
        logger.exception(exc)
        tx_info = None
    return tx_info


def validate_utxo(utxo: UTxO):
    """check if the token included in the utxo is the correct one."""
    logger.info("inspecting the utxo for valid auth tokens")
    valid = False
    last_tx_info = get_tx_info(str(utxo.input.transaction_id))
    last_tx_inputs = last_tx_info["_citxInputs"]
    inputs = {}
    # find out the inputs of the last publish transaction
    for item in last_tx_inputs:
        tx_id = item["txInRef"]["txOutRefId"]["getTxId"]
        index = item["txInRef"]["txOutRefIdx"]
        if tx_id not in inputs:
            inputs[tx_id] = [index]
        else:
            inputs[tx_id].append(index)
    # find out the addresses where the inputs are consumed from
    for tx_id in inputs:
        tx_info = get_tx_info(tx_id)
        tx_outputs = tx_info["_citxOutputs"]
        for index in inputs[tx_id]:
            # if the input is from the AUTH address
            if tx_outputs["contents"][index]["address"]["addressCredential"][
                "contents"
            ]["getPubKeyHash"] == str(auth_addr.payment_part):
                for value in tx_outputs["contents"][index]["value"]["getValue"]:
                    # if the token policy is the auth_policy (which doesn't change)
                    if value[0]["unCurrencySymbol"] == AUTH_POLICY:
                        valid = True
                        logger.info(
                            "the utxo is valid, it contains the correct auth token"
                        )
    return valid


def get_latest_utxo(oracle_addr: str):
    """return the latest Orcfax UTxO from those found on-chain."""
    oracle_utxos = context.utxos(oracle_addr)
    logger.info("inspecting '%s' UTxOs", len(oracle_utxos))
    latest_timestamp = 0
    latest_utxo = None
    for utxo in oracle_utxos:
        if utxo.output.script or not utxo.output.datum:
            continue

        oracle_datum = cbor2.loads(utxo.output.datum.cbor)
        try:
            timestamp = oracle_datum.value[2].value[0]
            if timestamp > latest_timestamp:
                latest_timestamp = timestamp
                latest_utxo = utxo
        except IndexError:
            pass
    time_now = datetime.now(timezone.utc)
    datum_timestamp = datetime.fromtimestamp(
        latest_timestamp / 1000
    )  # convert to seconds from milliseconds.
    time_diff = (
        (
            time_now.replace(tzinfo=None) - datum_timestamp.replace(tzinfo=None)
        ).total_seconds()
        / 60
        / 60
    )
    diff_hours = f"{time_diff:.2f}"  # 2 decimal places.
    if time_diff > 1:
        logger.warning(
            "'%s' hours since datum was published (%s)", diff_hours, latest_timestamp
        )
    if validate_utxo(latest_utxo):
        return latest_utxo
    return None


def read_datum():
    """Return savings to an account when a profit has been made."""
    logger.info("entering this script... ")
    logger.info("oracle smart contract: %s", ADA_USD_ORACLE_ADDR)
    latest_utxo = get_latest_utxo(ADA_USD_ORACLE_ADDR)
    if not latest_utxo:
        logger.info("no oracle data found")
        sys.exit(0)
    display_utxo(latest_utxo)
    decode_utxo(latest_utxo)


def main():
    """Primary entry point for this script."""
    read_datum()


if __name__ == "__main__":
    main()
