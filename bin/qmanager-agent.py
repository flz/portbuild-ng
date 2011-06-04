#! /usr/bin/env python

import signal
import pickle
import platform
import socket
import time

from pika import BasicProperties

import portbuild.qthreads as qthreads
import portbuild.torrent as torrent
import portbuild.util as util

ready = []

class AgentProducer(qthreads.QueueProducerThread):

  def __init__(self):
    qthreads.QueueProducerThread.__init__(self)

  def setup(self):
    """Set up AgentProducer."""
    self.channel = self.connection.channel()
    self.channel.add_on_return_callback(self.notify_return)
    util.debug("AgentProducer is all set!")

  def teardown(self):
    """Clean up AgentProducer."""
    self.channel.close()

  def notify(self, queue):
    """Send notification back to the head node."""
    message = "Finished" # FIXME
    util.log("Sending notification on {0}".format(queue))
    props = BasicProperties(content_type="text/plain", delivery_mode=1)
    self.channel.basic_publish(exchange="",
                               routing_key=queue,
                               mandatory=True,
                               immediate=True,
                               body=pickle.dumps(message),
                               properties=props)

  def notify_return(self, method, header, body):
    """Notification was returned. Head node isn't listening anymore."""
    # This actually is only triggered when the exchange doesn't exists,
    # not when the queue doesn't exist.
    print "Message returned!"

class AgentConsumer(qthreads.QueueConsumerThread):

  def __init__(self):
    qthreads.QueueConsumerThread.__init__(self)

  def setup(self):
    """Set up AgentConsumer."""
    self.arch = platform.machine()
    self.hostname = socket.gethostname()

    self.channel = self.connection.channel()
    self.channel.queue_declare(queue=self.arch, durable=True, exclusive=False, auto_delete=False)
    self.channel.basic_qos(prefetch_count=1)
    self.channel.basic_consume(self.handle_delivery, queue=self.arch)
    util.debug("AgentConsumer is all set!")
    util.debug("AgentConsumer listening on queue {0}...".format(self.arch))

  def teardown(self):
    """Clean up AgentConsumer."""
    self.channel.close()

  def handle_delivery(self, channel, method, header, body):
    """Message received callback."""
    global producer

    message = pickle.loads(body)
    p = message["package"]
    arch = message["arch"]
    branch = message["branch"]
    buildid = message["buildid"]
    torrents = message["torrents"]
    reply_to = message["reply_to"]
    self.buildname = "{0}/{1}/{2}".format(arch, branch, buildid)

    if buildid in ready:
      util.log("Building {0} for build {1}".format(p.name, self.buildname))
      channel.basic_ack(delivery_tag=method.delivery_tag)
    else:
      time.sleep(5)
      channel.basic_reject(delivery_tag=method.delivery_tag)
      util.log("Setting up build {0}".format(self.buildname))
      ts = torrent.TorrentSession()
      for t in torrents:
        t.dest="." # XXX - Temporary while I'm testing locally.
        ts.add(t)
        while not ts.all_seeding():
          ts.status()
          time.sleep(1)
      util.debug("Finished downloading components.")
      ts.terminate()
      producer.notify(reply_to)
      ready.append(buildid)

consumer = AgentConsumer()
consumer.start()

producer = AgentProducer()
producer.start()

def shutdown(signum, stack):
  global loop
  loop = False

signal.signal(signal.SIGINT, shutdown)

loop = True
while loop:
  time.sleep(3)

consumer.stop()
producer.stop()

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab
