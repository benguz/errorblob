# This formula installs pre-built binaries (faster, no Python required)
class Errorblob < Formula
  desc "Never block on the same bug twice - a lightning-fast error database for teams"
  homepage "https://github.com/yourusername/errorblob"
  version "0.1.0"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/yourusername/errorblob/releases/download/v0.1.0/errorblob-macos-arm64"
      sha256 "REPLACE_WITH_SHA256"

      def install
        bin.install "errorblob-macos-arm64" => "errorblob"
      end
    end

    on_intel do
      url "https://github.com/yourusername/errorblob/releases/download/v0.1.0/errorblob-macos-x64"
      sha256 "REPLACE_WITH_SHA256"

      def install
        bin.install "errorblob-macos-x64" => "errorblob"
      end
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/yourusername/errorblob/releases/download/v0.1.0/errorblob-linux-arm64"
      sha256 "REPLACE_WITH_SHA256"

      def install
        bin.install "errorblob-linux-arm64" => "errorblob"
      end
    end

    on_intel do
      url "https://github.com/yourusername/errorblob/releases/download/v0.1.0/errorblob-linux-x64"
      sha256 "REPLACE_WITH_SHA256"

      def install
        bin.install "errorblob-linux-x64" => "errorblob"
      end
    end
  end

  test do
    assert_match "0.1.0", shell_output("#{bin}/errorblob --version")
  end
end

