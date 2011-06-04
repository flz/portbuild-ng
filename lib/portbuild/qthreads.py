#! /usr/bin/env python

import threading
import time

from pika.adapters import BlockingConnection

class QueueThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.name = self.__class__.__name__
    self.connection = BlockingConnection()
    self._stop = threading.Event()
    self.setDaemon(True)

  def dprint(self, msg):
    print "%s: %s" % (self.name, msg)

class QueueConsumerThread(QueueThread):
  def __init__(self):
    QueueThread.__init__(self)

  def run(self):
    self.setup()
    self.channel.start_consuming()

  def stop(self):
    self.channel.stop_consuming()
    self._stop.set()

class QueueProducerThread(QueueThread):
  def __init__(self, freq=5):
    QueueThread.__init__(self)
    self.freq = freq

  def run(self):
    self.setup()
    # Need to find something better to avoid active loops.
    # Using signal.pause() when produce() is a no-op doesn't work.
    while True:
      self.produce()
      time.sleep(self.freq)

  def stop(self):
      self.connection.close()
      self._stop.set()

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab
