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
  def __init__(self, name, data, dest="/var/portbuild/tarballs"):
    """Create a Torrent object."""
    self.name = name
    self.data = data
    self.dest = dest
    self.handle = None

  def status(self):
    """Print status for the current torrent."""
    if not self.handle:
      raise TorrentNotStarted
    s = self.handle.status()
    print('%s - %.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d)' %
        (self.name, s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
        s.num_peers))

  @staticmethod
  def create(target):
    url = "http://%s:6969/announce" % (socket.gethostname())
    creator = "Ports Management Team <portmgr@FreeBSD.org>"
    fs = libtorrent.file_storage()
    libtorrent.add_files(fs, target)
    torrent = libtorrent.create_torrent(fs)
    torrent.add_tracker(url, 0)
    torrent.set_creator(creator)
    libtorrent.set_piece_hashes(torrent, os.path.dirname(target))
    data = libtorrent.bencode(torrent.generate())
    return Torrent(target, data=data)

# vim: tabstop=2 shiftwidth=2 expandtab
