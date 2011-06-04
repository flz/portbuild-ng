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

  def setup(self):
    """Optional setup."""
    pass

  def teardown(self):
    """Optional cleanup routine."""
    pass

class QueueConsumerThread(QueueThread):
  def __init__(self):
    QueueThread.__init__(self)

  def run(self):
    """Start consumer thread."""
    self.setup()
    self.channel.start_consuming()

  def stop(self):
    """Stop consumer thread."""
    self.channel.stop_consuming()
    self.teardown()
    self.connection.close()
    self._stop.set()

class QueueProducerThread(QueueThread):
  def __init__(self, freq=5):
    QueueThread.__init__(self)
    self.freq = freq

  def run(self):
    """Start producer thread."""
    self.setup()
    # Need to find something better to avoid active loops.
    # Using signal.pause() when produce() is a no-op doesn't work.
    while True:
      self.produce()
      time.sleep(self.freq)

  def produce(self):
    """Periodic task. Do nothing by default."""
    pass

  def stop(self):
    """Stop producer thread."""
    self.teardown()
    self.connection.close()
    self._stop.set()

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab
