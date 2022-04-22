# Dmix

stack:
- `schnorr_lib.py` libreria musig di bitpolito per creazione chiavi
- `quart` to create an app for browser (it's the async version of `flask`; async needed to interact with the node)
- `asyncio`  needed by quart
- `json`,`sys`,`subprocess`, `os` to manipulate thing on systems
- `bitcoinutils` to manipulate tx

do:

```
pip3 install -r requirements.txt
```
