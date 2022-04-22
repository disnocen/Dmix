# README

## organization of file:
1. stack
2. command
3. the `app.py` file i.e. the platform

## stack:
- `schnorr_lib.py` libreria musig di bitpolito per creazione chiavi
- `quart` to create an app for browser (it's the async version of `flask`; async needed to interact with the node)
- `asyncio`  needed by quart
- `json`,`sys`,`subprocess`, `os` to manipulate thing on systems
- `bitcoinutils` to manipulate tx

## do:
 in the directory of this repository
```
pip3 install -r requirements.txt
```
assuming `$BTCPATH` is the right one according to this table (from [here](https://github.com/bitcoin/bitcoin/blob/master/doc/bitcoin-conf.md))

Operating System | Data Directory | Example Path
-- | -- | --
Windows | `%APPDATA%\Bitcoin\` | `C:\Users\username\AppData\Roaming\Bitcoin\bitcoin.conf`
Linux | `$HOME/.bitcoin/` | `/home/username/.bitcoin/bitcoin.conf`
macOS | `$HOME/Library/Application Support/Bitcoin/` | `/Users/username/Library/Application Support/Bitcoin/bitcoin.conf`

then move the `bitcoin.conf` file there
## the platform

assuming you
- did the previous command
- have a bitcoin node (using `bitcoind`) running on *regtest* and listening on port 18443 with the `bitcoin.conf` provided in the repo in the right path for your os

then you can start the platform doing (in the directory of this repository)

```
python3 app.py
```

and go to <http://127.0.0.1:5000> to see the application platform. As you can see you have buttons for functions:

![platform](img/platform.png)