import ecdsa
import base58
import hashlib

# convert data to base58
def base58_encode(data):
    return base58.b58encode(data)

# double sha256
def double_sha256(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()

# function to create bitcoin private key 
def create_keys():
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    public_key = private_key.get_verifying_key()
    return private_key, public_key

# compute ckeck sum of private key
def checksum(private_key):
    return double_sha256(private_key)[:4]

def x(pk):
    return pk.pubkey.point.x()

def y(pk):
    return pk.pubkey.point.y()

def point_from_pk(pk):
    return (x(pk),y(pk))

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

    checksum_key = checksum(prefix + private_key.to_string() + suffix)
    print(checksum_key.hex())
    key = prefix + private_key.to_string() + suffix + checksum_key
    return base58_encode(key)

(sk,pk) = create_keys()



# print the private key
print("Private key: ", sk.to_string().hex())
print("Wif: ", to_wif(sk))

# print public key
print("Public key hex: ", pk.to_string().hex())
print("Public key : ", pk.to_string())
print("Public key der ", pk.to_der().hex())
print("public key x ", pk.pubkey.point.x())
print("public key y ", pk.pubkey.point.y())

# convert public ky into bitcoin curve point
