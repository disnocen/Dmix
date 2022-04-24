import ecdsa
import base58
import hashlib
import os
import asyncio
from bitcoinrpc import BitcoinRPC
from bitcoinutils.setup import setup
from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey
from schnorr_lib import *

# doo tath before running the program

# bitcoind -fallbackfee=0.01
# btc loadwallet testing

rpc = BitcoinRPC("http://127.0.0.1:18443", "user", "password")

# convert data to base58
def base58_encode(data):
    return base58.b58encode(data)

# double sha256
def double_sha256(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

# function to create bitcoin private key 
def create_keys():
    private_key = os.urandom(32)
    return private_key

# compute ckeck sum of private key
def checksum(private_key):
    return double_sha256(private_key)[:4]

def x_frombytes(pk: PublicKey):
    pub_bytes = pk.to_bytes()
    x = int(pub_bytes[0:32].hex(),16)
    return x

def y_frombytes(pk: PublicKey):
    pub_bytes = pk.to_bytes()
    y = int(pub_bytes[32:64].hex(),16)
    return y

def point_from_pk(pk):
    return (x_frombytes(pk), y_frombytes(pk))

# convert private key to wif
def to_wif(private_key,net="regtest",compressed=True):
    if net == "testnet" or net == "test" or net == "testnet3" or net == "regtest":
        prefix = b'\xef'
    else:
        prefix = b'\x80'

    if compressed:
        suffix = b'\01'
    else:
        suffix = b''

    checksum_key = checksum(prefix + private_key + suffix)
    key = prefix + private_key + suffix + checksum_key
    return base58_encode(key).decode()


# create three private keys; convert to wif format and store it in bitcoin node
async def import_wif_in_node(wif):
    # importprivkey "privkey" ( "label" ) ( rescan )
    # loop = asyncio.get_event_loop()
    x = await rpc.acall("importprivkey",[wif, "", False])
    # loop.close()
    return x

def create_keys_and_wif(net="regtest",compressed=True):
    private_key1 = create_keys()
    private_key2 = create_keys()
    private_key3 = create_keys()
    wif1 = to_wif(private_key1)
    wif2 = to_wif(private_key2)
    wif3 = to_wif(private_key3)
    print(wif1,wif2,wif3)
    # print(import_wif_in_node(wif1),import_wif_in_node(wif2),import_wif_in_node(wif3))
    return wif1,wif2,wif3

async def send_a_bitcoin(address):
    x = await rpc.acall("sendtoaddress",[address, 1.05])
    print(x)
    return x

async def main():
    setup('regtest')
    a = create_keys_and_wif()
    x = await asyncio.gather(import_wif_in_node(a[0]),import_wif_in_node(a[1]),import_wif_in_node(a[2]))  # import_wif_in_node(i)
    privs = [PrivateKey.from_wif(wiff) for wiff in a]
    pubs = [priv.get_public_key() for priv in privs]
    
    addresses = [pub.get_address() for pub in pubs]
    print([addresses[0].to_string(),addresses[1].to_string(),addresses[2].to_string()])
    xx = await asyncio.gather(send_a_bitcoin(addresses[0].to_string()),send_a_bitcoin(addresses[1].to_string()),send_a_bitcoin(addresses[2].to_string()))
    print("xx=",xx)
    x = await rpc.acall("generatetoaddress",[101,"mjzcYyrS6GLyyowPfqbx3thenXZQ6ig4QY"])
    b=[]
    for _ in range(3):
        b.append(create_keys())
    b_wif = [to_wif(bb) for bb in b]
    privs_new = [PrivateKey.from_wif(wiff) for wiff in b_wif]
    pubs_new = [priv.get_public_key() for priv in privs_new]
    users = []
    for i in range(len(pubs_new)):
        # users.append([pubs_new[i].to_bytes(),point_from_pk(pubs_new[i]),b[i].hex()])
        users.append({"privateKey":b[i].hex(),"publicKey":pubs_new[i].to_hex()})
    # print(users)
    msg =os.urandom(32)
    print("X =",musig2_key_aggregation(users))
    print(schnorr_musig2_sign(msg, users))


if __name__ == "__main__":
    asyncio.run(main())