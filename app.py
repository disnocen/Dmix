#!/usr/bin/env python3

# from flask import Flask, render_template, request, url_for, flash, redirect
from quart import  Quart, render_template, request, url_for, flash, redirect
import json
import sys
import subprocess
import os.path
from os import path
import shutil
import asyncio
from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.keys import PrivateKey, P2pkhAddress, P2shAddress
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.script import Script
from bitcoinrpc import BitcoinRPC

# Create the application.
APP = Quart(__name__)
rpc = BitcoinRPC("http://127.0.0.1:18443", "user", "password")


# await rpc.getconnectioncount()
rpc.acall("loadwallet",["testing"])


@APP.route('/', methods=('GET', 'POST'))
async def index():
    """ Displays the index page accessible at '/'
    """
    x = " "
    if request.method == 'POST':
        legacy = request.args.post('legacy')
        print("we are in post!")
        if legacy == "on":
            x = await rpc.acall("getnewaddress",["", "legacy"])
        else:
            x = await rpc.acall("getnewaddress",[])

    templateData = {'address' : x}
    return await render_template('index.html', **templateData)

@APP.route('/sendtxhtml', methods=('GET', 'POST'))
async def index_sendtx():
    """ Displays the index page accessible at '/'
    """
    return await render_template('sendtx.html')

@APP.route('/gettx')
async def gettx():
    txhash = str(request.args.get('txhash'))
    rawtx = await rpc.acall("getrawtransaction",[txhash])
    y = await rpc.acall("decoderawtransaction",[rawtx])
    y = json.dumps(y, indent=4)

    yy = str(y).split('\n')
    string_html='<br/>'.join(yy)
    return "<pre>" + string_html + "</pre>"

@APP.route('/createblocks')
async def createblocks():
    nblocks = int(request.args.get('nblocks'))
    addr = request.args.get('addr')
    x = await rpc.acall("generatetoaddress",[nblocks,addr])
    blockcount = await rpc.acall("getblockcount",[])
    return str(x)+"<br/><br/> <br/><br/> we have " + str(blockcount) + " blocks"

@APP.route('/sendtx')
async def sendtx():
    amt = int(request.args.get('amt'))
    addr = request.args.get('addr')
    x = await rpc.acall("sendtoaddress",[addr,amt])
    return "transaction sent<br/>" + "<a href=/gettx?txhash=" + str(x) + ">" + str(x) + "</a>"

@APP.route('/chosentx')
async def chosentx():
    x = await rpc.acall("listunspent",[])
    string_html = "these your txs<br/>"
    string_html += '<form action="/sendtxwithinputs">'
    sums = 0

    for i in range(len(x)):
        tx = x[i]
        txid = tx['txid']
        vout = str(tx['vout'])
        checkbox = request.args.get(txid + "_" + vout)
        if checkbox == "on":
            print(tx)
            sums += float(tx['amount'])
            scriptPubKey = tx['scriptPubKey']
            decode = await rpc.acall("decodescript",[scriptPubKey])
            typetx=decode["type"]

            if typetx == "scripthash":
                string_html += '<label for="' + txid +'">Transaction hex:</label><br>\n'
                string_html += '<input type="text"  name="'+txid+'" value="'+txid+'" readonly><br>\n'
                string_html += '<label for="' + txid+ "_vout" +'">Vout:</label><br>\n'
                string_html += '<input type="number"  name="'+txid + "_vout"+'" value='+vout+'  readonly><br/><br/>\n'
                string_html += '<label for="' + txid+ "_inscript" +'">Input Script:</label><br>\n'
                string_html += '<input type="text"  name="'+txid + '"_inscript"><br/><br/>\n'
                string_html += '<label for="' + txid+ "_redeemscript"
                +'">Output Script:</label><br>\n'
                string_html += '<input type="text"  name="'+txid + '"_redeemscript"><br/><br/>\n'
            else:
                # string_html += '<div><form>   <input type="text" id="' + txid +'" name="country" value="" readonly><br><br> '
                string_html += '<label for="' + txid +'">Transaction hex:</label><br>\n'
                string_html += '<input type="text"  name="'+txid+'" value="'+txid+'" readonly><br>\n'
                string_html += '<label for="' + txid+ "_vout" +'">Vout:</label><br>\n'
                string_html += '<input type="number"  name="'+txid + "_vout"+'" value='+vout+'  readonly><br/><br/>\n'
    
    string_html +=  '<label for="address">Insert address:</label><br>\n <input type="text" class="address" name="address"><br/>'
    string_html +=  '<label for="amount">Insert amount:</label><br>\n <input type="number" class="amount" name="amount" value="'+ str(sums) +'" step="0.01"><br/>'
    string_html += '<input type="submit" value="Submit">'

    string_html += '</form>'
    return string_html
            
        
@APP.route('/sendtxwithinputs')
async def sendtxwithinputs():
    x = await rpc.acall("listunspent",[])
    #create inputs
    ins = []
    keys = []
    for i in range(len(x)):
        tx = x[i]
        txid = tx['txid']
        vout = str(tx['vout'])
        if (request.args.get(txid) == txid) and (request.args.get(txid+"_vout") == vout):
            keys.append(await rpc.acall("dumpprivkey",[tx["address"]]))
            ins.append({"txid":txid,"vout": int(vout)}) 

    #create outputs
    address = request.args.get("address")
    amt = request.args.get("amount")
    to = [{address:float(amt)}]

    # send tx
    txrawhash = await rpc.acall("createrawtransaction",[ins,to])
    signedtx = await rpc.acall("signrawtransactionwithkey",[txrawhash,keys])
    y = await rpc.acall("decoderawtransaction",[signedtx["hex"]])
    y = json.dumps(y, indent=4)

    yy = str(y).split('\n')
    string_html='<br/>'.join(yy)
    string_html="<pre>" + string_html + "</pre>"
    txhash = await rpc.acall("sendrawtransaction",[signedtx["hex"]])
    return string_html + "<br/>" +"<br/>" +"<br/>" + str(txhash)
    
@APP.route('/sendtxwithscript')
async def sendtxwithscript():
    x = await rpc.acall("listunspent",[])
    #create inputs
    ins = []
    keys = []
    for i in range(len(x)):
        tx = x[i]
        txid = tx['txid']
        vout = str(tx['vout'])
        if (request.args.get(txid) == txid) and (request.args.get(txid+"_vout") == vout):
            keys.append(await rpc.acall("dumpprivkey",[tx["address"]]))
            ins.append({"txid":txid,"vout": int(vout)}) 

    #create outputs
    address = request.args.get("address")
    amt = request.args.get("amount")
    to = [{address:float(amt)}]

    # send tx
    txrawhash = await rpc.acall("createrawtransaction",[ins,to])
    signedtx = await rpc.acall("signrawtransactionwithkey",[txrawhash,keys])
    y = await rpc.acall("decoderawtransaction",[signedtx["hex"]])
    y = json.dumps(y, indent=4)

    yy = str(y).split('\n')
    string_html='<br/>'.join(yy)
    string_html="<pre>" + string_html + "</pre>"
    txhash = await rpc.acall("sendrawtransaction",[signedtx["hex"]])
    return string_html + "<br/>" +"<br/>" +"<br/>" + str(txhash)
    

     
@APP.route('/sendtxchoosesender')
async def sendtxchoosesender():
    x = await rpc.acall("listunspent",[])
    string_html = "Choose which input (singular) you want to spend from <br/><br/><br/>"
    string_html += '<form  action="/chosentx" > '
    string_html += '<input type="submit" value="Submit">'
    string_html += "<table> <tr> <th> </th> <th>txid</th> <th>vout</th> <th>address</th> <th>amt</th> </tr> "
    for i in range(len(x)):
        tx = x[i]
        txid = tx['txid']
        n = str(tx['vout'])
        address = tx['address']
        amount = str(tx['amount'])
        string_html += "<tr> <td>" + '<input type="checkbox" id="' + txid + "_" + n + '" name="' + txid + "_" + n + '"> </td><td> ' +'<a href="gettx?txhash='+ txid +'">'+ txid + "</a>" + "</td><td>"+n+"</td><td>"+address+"</td><td>"+str(amount)+"</td></tr>" 

    string_html +="</table>"
    string_html += '<input type="submit" value="Submit">'
    string_html += '</form> '
    return str(string_html)

@APP.route('/newaddr')
async def newaddr():
    legacy = request.args.get('legacy')
    if legacy == "on":
        x = await rpc.acall("getnewaddress",["", "legacy"])
    else:
        x = await rpc.acall("getnewaddress",[])
    return str(x) #+ "  " + str(legacy)

@APP.route('/listunspent')
async def listing():
    x = await rpc.acall("listunspent",[])
    
    string_html = """
<html>
    <head>
        <title>
            P2T table
        </title>
        <link rel="stylesheet" href="/static/styles/style.css">
    </head>

<body>
    <div class="totaleTitolo">
        <div class="titolo">
            Unspent <br>
            transaction list
        </div>
        <div>
            <img src="/static/img/btcWallet2.png" style ="width: 15%">
        </div>
    </div>
    
<table class="tabella"> 
    <tr> 
        <th>txid</th> <th>address</th> <th class="colPiccola">amt</th> 
    </tr> 
    """
    for i in range(len(x)):
        tx = x[i]
        txid = tx['txid']
        address = tx['address']
        amount = str(tx['amount'])
        string_html += "<tr> <td> " +'<a href="gettx?txhash='+ txid +'">'+ txid + "</a>" + "</td><td>"+address+'</td><td class="colPiccola">'+str(amount)+"</td></tr>" 

    string_html +="</table>"
    return str(string_html)

@APP.route('/balance')
async def balance():
    x = await rpc.acall("getbalance",[])
    return "your balance is " + str(x)

if __name__ == '__main__':
    APP.debug=True
    APP.run()
