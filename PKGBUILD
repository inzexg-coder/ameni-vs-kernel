# Maintainer: inzexg-coder <amenokeakira@gmail.com>
# Contributor: Ameni Agent
pkgname=ameni-vs-kernel
pkgver=1.0.0
pkgrel=1
pkgdesc="Ameni VS Kernel — configuration archive and diagnostic toolkit for Visual Studio build-system failures (LNK2019, LNK1104, linker errors)"
arch=('any')
url="https://github.com/inzexg-coder/ameni-vs-kernel"
license=('MIT')
depends=('bash')
optdepends=('powershell: run PowerShell verification scripts natively')
source=("${pkgname}-${pkgver}.tar.gz::${url}/archive/v${pkgver}.tar.gz")
sha256sums=('SKIP')

package() {
  cd "${srcdir}/${pkgname}-${pkgver}"
  install -d "${pkgdir}/usr/share/${pkgname}"
  cp -r .ameni props scripts errors vs2017 vs2022 vs2025 "${pkgdir}/usr/share/${pkgname}/"
  install -Dm644 README.md "${pkgdir}/usr/share/doc/${pkgname}/README.md"
  install -Dm644 .vsconfig "${pkgdir}/usr/share/${pkgname}/.vsconfig"

  # Symlink CLI
  install -Dm755 .ameni/bin/ameni "${pkgdir}/usr/bin/ameni"

  install -Dm644 advanced.md debugging.md general.md vc++-directories.md \
    "${pkgdir}/usr/share/doc/${pkgname}/"
}
