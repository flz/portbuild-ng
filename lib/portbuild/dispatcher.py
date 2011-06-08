import copy
import json
import pickle
import time

from pika import BasicProperties

import portbuild.util as util
import portbuild.qthreads as qthreads

class DispatcherConsumer(qthreads.QueueConsumerThread):
  def __init__(self, on_success, on_failed):
    qthreads.QueueConsumerThread.__init__(self)
    self.queue = ""
    self.on_success = on_success
    self.on_failed = on_failed

  def setup(self):
    self.channel = self.connection.channel()
    result = self.channel.queue_declare(durable=True, exclusive=True, auto_delete=True)
    self.queue = result.method.queue
    self.channel.basic_consume(self.handle_delivery, queue=self.queue)
    util.debug("DispatcherConsumer is all set!")

  def handle_delivery(self, channel, method, header, body):
    # XXX - This is no-op for now.
    data = pickle.loads(body)
    print json.dumps(data)

class DispatcherProducer(qthreads.QueueProducerThread):
  def __init__(self, build):
    qthreads.QueueProducerThread.__init__(self, 5)
    self.build = build
    self.arch = build.arch
    self.channel = None
    self.reply_to = None

  def setup(self):
    # Declare channel and queue.
    self.channel = self.connection.channel()
    self.channel.queue_declare(queue=self.arch, durable=True, exclusive=False, auto_delete=False)
    util.debug("DispatcherProducer is all set!")

  def dispatch(self, package):
    """Add package to the work queue."""
    # Build the message...
    message = {}
    message["package"] = package
    message["arch"] = self.build.arch
    message["branch"] = self.build.branch
    message["buildid"] = self.build.buildid
    torrents = [copy.copy(t.torrent) for t in self.build.tarballs]

    message["torrents"] = torrents
    message["reply_to"] = self.reply_to

    # ... and push!
    self.channel.basic_publish(exchange="",
                               routing_key=self.arch,
                               body=pickle.dumps(message),
                               properties=BasicProperties(content_type="text/plain",
                                                          delivery_mode=1))

class Dispatcher:
  def __init__(self, build, on_success, on_failed):
    self.build = build
    self.consumer = DispatcherConsumer(on_success, on_failed)
    self.producer = DispatcherProducer(build)

  def start(self):
    self.consumer.start()
    util.debug("Waiting for DispatcherConsumer to be ready...")
    while not self.consumer.queue:
      time.sleep(1)
    self.producer.reply_to = self.consumer.queue
    self.producer.start()
    util.debug("Waiting for DispatcherProducer to be ready...")
    while not self.producer.channel:
      time.sleep(1)

  def stop(self):
    util.debug("Stopping Dispatcher...")
    self.consumer.stop()
    self.producer.stop()

  def dispatch(self, package):
    util.log("Dispatching {0}...".format(package.name))
    self.producer.dispatch(package)

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab
