#!/usr/bin/python
# -*- coding: utf-8 -*-
import websocket  # pip install websocket-client
# from pymongo import MongoClient  # pip install pymongo

# from poloniex import Poloniex

from multiprocessing.dummy import Process as Thread
import json
import logging

logger = logging.getLogger(__name__)


class wsTicker(object):

    def __init__(self, api=None):
        self.api = api
        # if not self.api:
        #     self.api = Poloniex(jsonNums=float)
        # self.db = MongoClient().poloniex['ticker']
        # self.db.drop()
        self.ws = websocket.WebSocketApp("wss://api.poloniex.com/",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.on_open = self.on_open

    # def __call__(self, market=None):
    #     """ returns ticker from mongodb """
    #     if market:
    #         return self.db.find_one({'_id': market})
    #     return list(self.db.find())

    def on_message(self, ws, message):
        message = json.loads(message)
        if 'error' in message:
            logger.info(message['error'])
            return

        if message[0] == 1002:
            if message[1] == 1:
                logger.info('Subscribed to ticker')
                return

            if message[1] == 0:
                logger.info('Unsubscribed to ticker')
                return

            data = message[2]

            logger.info(
                {"id": float(data[0])},
                {"$set": {'last': data[1],
                          'lowestAsk': data[2],
                          'highestBid': data[3],
                          'percentChange': data[4],
                          'baseVolume': data[5],
                          'quoteVolume': data[6],
                          'isFrozen': data[7],
                          'high24hr': data[8],
                          'low24hr': data[9]
                          }})

    def on_error(self, ws, error):
        logger.error(error)

    def on_close(self, ws):
        logger.warning("Websocket closed!")

    def on_open(self, ws):
        # tick = self.api.returnTicker()
        # for market in tick:
        #     print(
        #         {'_id': market},
        #         {'$set': tick[market]})
        logger.info('Populated markets database with ticker data')
        self.ws.send(json.dumps({'command': 'subscribe',
                                 'channel': 'ticker'}))

    def start(self):
        self.t = Thread(target=self.ws.run_forever)
        self.t.daemon = True
        self.t.start()
        logger.info('Thread started')

    def stop(self):
        self.ws.close()
        self.t.join()
        logger.warning('Thread joined')


if __name__ == "__main__":
    import pprint
    from time import sleep
    websocket.enableTrace(True)
    ticker = wsTicker()
    ticker.start()
    while True:
        pass
    # for i in range(5):
    #     # sleep(10)
    #     # pprint.pprint(ticker('USDT_BTC'))
    # ticker.stop()