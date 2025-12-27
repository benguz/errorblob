class Errorblob < Formula
  desc "Never block on the same bug twice - a lightning-fast error database for teams"
  homepage "https://github.com/yourusername/errorblob"
  url "https://github.com/yourusername/errorblob/releases/download/v0.1.0/errorblob-0.1.0.tar.gz"
  sha256 "REPLACE_WITH_SHA256_OF_TARBALL"
  license "MIT"

  depends_on "python@3.12"

  def install
    # Create a virtualenv and install the package
    venv = virtualenv_create(libexec, "python3.12")
    venv.pip_install_and_link buildpath
  end

  test do
    assert_match "errorblob", shell_output("#{bin}/errorblob --version")
  end
end

