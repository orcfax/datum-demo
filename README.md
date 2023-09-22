# Orcfax Datum Demo

Demonstration how to read an Orcfax Datum using PyCardano. The example reads
an on-chain Datum via [Ogmios][ogmios-1] and logs various details about the
Datum as it goes.

Will work out of the box, and connects to Orcfax preprod smart contract
address.

[ogmios-1]: https://ogmios.dev/

## Example output

The output can be worked on as necessary. It currently looks as follows.

<!-- markdownlint-disable-line-length MD013 -->
```text
2023-09-22T13:28:16Z INFO :: read_datum.py:197:read_datum() :: entering this script...
2023-09-22T13:28:16Z INFO :: read_datum.py:198:read_datum() :: oracle smart contract: addr_test1wrtcecfy7np3sduzn99ffuv8qx2sa8v977l0xql8ca7lgkgmktuc0
2023-09-22T13:28:19Z INFO :: read_datum.py:162:get_latest_utxo() :: inspecting '848' UTxOs
2023-09-22T13:28:19Z INFO :: read_datum.py:65:display_utxo() :: (input) transaction id: 0ec260a31c937f73eca073867d79a6edcdda3bd1f966ab42714fc528b653f716
2023-09-22T13:28:19Z INFO :: read_datum.py:66:display_utxo() :: (output) transaction addr: addr_test1wrtcecfy7np3sduzn99ffuv8qx2sa8v977l0xql8ca7lgkgmktuc0
2023-09-22T13:28:19Z INFO :: read_datum.py:67:display_utxo() :: (output) datum cbor:

590207d8799fa74840636f6e746578745268747470733a2f2f736368656d612e6f7267525f3a636f6e74656e745369676e61747572655840323639353835383434336164333935343064373161336538653562663632313161363738666339353539656639393166636565386634356330353838636362394a6964656e746966696572a34a70726f706572747949445041726b6c79204964656e74696669657244747970654d50726f706572747956616c75654576616c7565582f75726e3a6f72636661783a66333635323533622d353565662d346633622d383031372d613133666164333262313030446e616d654f4144412d5553447c5553442d41444144747970654d50726f706572747956616c75654576616c75659fd87c9f1a91d107c81bfffffffffffffff6ffd87c9f1b000e85b16ddaf53d1bfffffffffffffff1ffff4e76616c75655265666572656e63659fa34540747970654d50726f706572747956616c7565446e616d654976616c696446726f6d4576616c75651b0000018abc9b91d5a34540747970654d50726f706572747956616c7565446e616d654c76616c69645468726f7567684576616c75651b0000018abcd28055ff58203034434130303031484159395137564e4b534754514b3039324531544638445ad87a9f1b0000018abcd28055ff581c90b121aa6b689200adf7ed115040a96375d2b68e23633d6864c53a91ff

2023-09-22T13:28:19Z INFO :: read_datum.py:70:display_utxo() :: (output) Tx cost: 3.42214 ADA
2023-09-22T13:28:19Z INFO :: read_datum.py:137:decode_utxo() ::

{
  "@context": "https://schema.org",
  "type": "PropertyValue",
  "name": "ADA-USD|USD-ADA",
  "value": [
    0.24463953360000001,
    4.087646772720957
  ],
  "valueReference": [
    {
      "@type": "PropertyValue",
      "name": "validFrom",
      "value": 1695381426645
    },
    {
      "@type": "PropertyValue",
      "name": "validThrough",
      "value": 1695385026645
    }
  ],
  "identifier": {
    "propertyID": "Arkly Identifier",
    "type": "PropertyValue",
    "value": "urn:orcfax:f365253b-55ef-4f3b-8017-a13fad32b100"
  },
  "_:contentSignature": "2695858443ad39540d71a3e8e5bf6211a678fc9559ef991fcee8f45c0588ccb9"
}

2023-09-22T13:28:19Z INFO :: read_datum.py:138:decode_utxo() :: oracle datum identifier (internal): b'04CA0001HAY9Q7VNKSGTQK092E1TF8DZ'
2023-09-22T13:28:19Z INFO :: read_datum.py:143:decode_utxo() :: oracle datum timestamp: 2023-09-22T12:17:06Z (1695385026645)
2023-09-22T13:28:19Z INFO :: read_datum.py:156:pretty_log_value() :: ADA-USD: 0.24463953360000001
2023-09-22T13:28:19Z INFO :: read_datum.py:156:pretty_log_value() :: USD-ADA: 4.087646772720957
```

## Developer install

### pip

Setup a virtual environment `venv` and install the local development
requirements as follows:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements/local.txt
```

### tox

#### Run tests (all)

```bash
python -m tox
```

#### Run linting-only

```bash
python -m tox -e linting
```

### pre-commit

Pre-commit can be used to provide more feedback before committing code. This
reduces reduces the number of commits you might want to make when working on
code, it's also an alternative to running tox manually.

To set up pre-commit, providing `pip install` has been run above:

* `pre-commit install`

This repository contains a default number of pre-commit hooks, but there may
be others suited to different projects. A list of other pre-commit hooks can be
found [here][pre-commit-1].

[pre-commit-1]: https://pre-commit.com/hooks.html
