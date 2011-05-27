import unittest

import portbuild.torrent as torrent

class TestTorrent(unittest.TestCase):
  
  def setUp(self):
    """Setup torrent session."""
    # This doesn't actually check that the argument is an archive, just that the file exists.
    self.session = torrent.TorrentSession()
    self.torrent = torrent.Torrent.create("/etc/rc")

  def tearDown(self):
    self.session.terminate()

  def test_status_notstarted(self):
    """Should raise an exception because the torrent wasn't started."""
    self.assertRaises(torrent.TorrentNotStarted, self.torrent.status)

  def test_add_invalidtorrent_1(self):
    """Should raise an exception because the argument isn't a Torrent instance."""
    self.assertRaises(torrent.InvalidTorrent, self.session.add, None)

  def test_add_invalidtorrent_2(self):
    """Should raise an exception because the argument isn't a Torrent instance."""
    self.assertRaises(torrent.InvalidTorrent, self.session.add, "foo")

  def test_add_invalidtorrent_3(self):
    """Should raise an exception because the argument isn't a Torrent instance."""
    self.assertRaises(torrent.InvalidTorrent, self.session.add, 42)

  def test_add_validtorrent(self):
    """Adds a torrent to a session."""
    self.session.add(self.torrent)

  def test_add_torrentalreadyadded(self):
    """Should raise an exception because the torrent was previously added to a session."""
    self.session.add(self.torrent)
    self.assertRaises(torrent.TorrentAlreadyStarted, self.session.add, self.torrent)

if __name__ == '__main__':
    unittest.main()

# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab
