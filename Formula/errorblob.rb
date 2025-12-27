class Errorblob < Formula
  include Language::Python::Virtualenv

  desc "Never block on the same bug twice - a lightning-fast error database"
  homepage "https://github.com/yourusername/errorblob"
  url "https://github.com/yourusername/errorblob/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "UPDATE_WITH_ACTUAL_SHA256"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/errorblob", "--version"
  end
end

