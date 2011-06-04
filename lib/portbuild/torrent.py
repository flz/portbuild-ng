import libtorrent
import os
import socket

class TorrentException(Exception):
  pass

class InvalidTorrent(TorrentException):
  pass

class TorrentNotStarted(TorrentException):
  pass

class TorrentAlreadyStarted(TorrentException):
  pass

class TorrentSession:
  def __init__(self):
    """Create a TorrentSession object."""
    self.session = libtorrent.session()
    self.session.listen_on(6881, 6891)
    self.torrents = []

  def add(self, torrent):
    """Add a torrent to the current sessions."""
    if not torrent or not isinstance(torrent, Torrent):
      raise InvalidTorrent

    if torrent.handle:
      raise TorrentAlreadyStarted

    torrent.session = self
    e = libtorrent.bdecode(torrent.data)
    info = libtorrent.torrent_info(e)
    torrent.handle = self.session.add_torrent(info, torrent.dest)
    self.torrents.append(torrent)
    
  def all_seeding(self):
    """Returns True if all torrent in the current session are seeding."""
    for torrent in self.torrents:
      if not torrent.handle.is_seed():
        return False
    return True

  def status(self):
    """Print status for all torrents in the current session."""
    for torrent in self.torrents:
      torrent.status()

  def terminate(self):
    """Terminate the current session."""
    for torrent in self.torrents:
      self.session.remove_torrent(torrent.handle)

class Torrent:
  def __init__(self, name, data):
    """Create a Torrent object."""
    self.name = os.path.basename(name)
    self.dest = os.path.dirname(name)
    self.data = data
    self.handle = None

  def __copy__(self):
    return Torrent(self.name, self.data)

  def status(self):
    """Print status for the current torrent."""
    if not self.handle:
      raise TorrentNotStarted
    s = self.handle.status()
    str = '{0} - {1:.2%} done (dl: {2:.1f} KB/s, ul: {3:.1f} KB/s, peers: {4})'
    print str.format(self.name, s.progress, \
                     s.download_rate/1024, s.upload_rate/1024, s.num_peers)

  def dump(self):
    with open("/tmp/{0}.torrent".format(os.path.basename(self.name)), "w") as f:
      f.write(self.data)

  @staticmethod
  def create(target):
    url = "http://{0}:6969/announce".format(socket.gethostname())
    creator = "Ports Management Team <portmgr@FreeBSD.org>"
    fs = libtorrent.file_storage()
    libtorrent.add_files(fs, target)
    torrent = libtorrent.create_torrent(fs)
    torrent.add_tracker(url, 0)
    torrent.set_creator(creator)
    libtorrent.set_piece_hashes(torrent, os.path.dirname(target))
    data = libtorrent.bencode(torrent.generate())
    return Torrent(target, data=data)

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab
