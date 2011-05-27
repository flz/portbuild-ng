import unittest

import portbuild.tarball as tarball

class TestTarball(unittest.TestCase):
  
  def setUp(self):
    """Creates a tarball object."""
    # This doesn't actually check that the argument is an archive, just that the file exists.
    self.ball = tarball.Tarball("/nonexistent", "meh", "/etc/passwd")
    self.ball2 = tarball.Tarball("/nonexistent", "meh", "/etc/passwd")

  def tearDown(self):
    pass

  def test_init_ioerror(self):
    """Should raise an exception for a non-existent file."""
    self.assertRaises(IOError, tarball.Tarball, "/nonexistent", "meh", "/nonexistent/meh.tbz")

  def test_create_ok(self):
    """Should create (then remove) a empty tarball.
    May fail if /var/portbuild/tarball doesn't exist."""
    ball = tarball.Tarball.create("/var/portbuild", "scripts")
    ball.delete()

  def test_create_equal(self):
    """Should create (then remove) a empty tarball.
    May fail if /var/portbuild/tarball doesn't exist."""
    ball = tarball.Tarball.create("/var/portbuild", "scripts")
    ball.delete()

  def test_eq_self(self):
    self.assertTrue(self.ball == self.ball)

  def test_eq_none(self):
    self.assertFalse(self.ball == None)


if __name__ == '__main__':
    unittest.main()
