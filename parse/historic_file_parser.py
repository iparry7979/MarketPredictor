# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 10:54:29 2026

@author: iparr
"""

import json
import gzip
import bz2
from typing import Iterator, Dict, Any

#The generators in this file can be thought of as a dynamic linked list.
#When the def of raw_message_stream is run it calls a next() function and
#runs until it hits yield. It then waits for next() to be called again

#This allows us to stream the file without loading the entire fucking thing
#into memory

def open_raw_file(path: str):
    """
    Opens a raw Betfair Market Stream API file.
    Supports:
      - plain text
      - .gz (gzip)
      - .bz2 (bzip2)
    """
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    elif path.endswith(".bz2"):
        return bz2.open(path, "rt", encoding="utf-8")
    else:
        return open(path, "r", encoding="utf-8")

def raw_message_stream(path: str) -> Iterator[Dict[str, Any]]:
    """
    Streams parsed JSON messages from a Betfair Market Stream API file.
    Yields one parsed message at a time.
    """
    with open_raw_file(path) as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                msg = json.loads(line)
                yield msg
            except json.JSONDecodeError as e:
                print(f"JSON error in {path} at line {line_number}: {e}")
                continue
            
def market_change_stream(path: str):
    """
    Yields (timestamp, market_change) pairs.
    """
    for msg in raw_message_stream(path):
        timestamp = msg.get("pt")
        for mc in msg.get("mc", []):
            yield timestamp, mc


def runner_change_stream(path: str):
    """
    Yields (timestamp, market_id, runner_change) triples.
    """
    for ts, mc in market_change_stream(path):
        market_id = mc.get("id")
        for rc in mc.get("rc", []):
            yield ts, market_id, rc
 
#for ts, mc in market_change_stream("D:/Betting System/Data/BetfairHistoricData/HorseRacing/Australia/2022/2/10/31224197/1.194446097.bz2"):
#    print(ts, mc["id"])
#    break

#for i, (ts, market_id, rc) in enumerate(runner_change_stream("D:/Betting System/Data/BetfairHistoricData/HorseRacing/Australia/2022/2/10/31224197/1.194446097.bz2")):
#    print(ts, market_id, rc.get("id"), rc.get("ltp"))
#    if i == 9:
#        break

#count=0
#for ts, market_id, rc in runner_change_stream("D:/Betting System/Data/BetfairHistoricData/HorseRacing/Australia/2022/2/10/31224197/1.194446097.bz2"):
#    print(count, ts, market_id, rc.get("id"), rc.get("ltp"))
#    count = count+1

