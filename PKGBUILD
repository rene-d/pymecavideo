# Contributor: Daneel <->

pkgname=pymecavideo
pkgver=4.0
pkgrel=1
pkgdesc="Permet de tracer point par point la trajectoire de point ainsi que choisir un référentiel particulier pour étudier la trajectoire dans celui-ci. Les données ainsi recueillies peuvent être exportées dans un logiciel de traitement."
arch=(i686 x86_64)
url="http://outilsphysiques.tuxfamily.org/pmwiki.php/Oppl/Pymecavideo"
license=('GPL3')
groups=()
depends=('pyqt' 'ffmpeg' 'vlc')
makedepends=('pyqt' 'python')
optdepends=()
provides=('pymecavideo')
conflicts=()
replaces=()
backup=()
options=()
source=("http://outilsphysiques.tuxfamily.org/upload/${pkgname}-${pkgver}.tar.gz")
noextract=()
md5sums=('4868adb40a802c206af69799d8f1f528')

build() {
	cd $srcdir/$pkgname-$pkgver
	find $srcdir/$pkgname-$pkgver -type d -name ".svn" -exec rm -rf {} \;
	make || return 1
	python setup.py install --root=$pkgdir/ --optimize=1 || return 1

	install -D -m644 $srcdir/$pkgname-$pkgver/COPYING $pkgdir/usr/share/licenses/$pkgname/LICENSE
	install -D -m644 $srcdir/$pkgname-$pkgver/icones/$pkgname-48.png $pkgdir/usr/share/pixmaps/$pkgname.png
	install -D -m644 $srcdir/$pkgname-$pkgver/$pkgname.svg $pkgdir/usr/share/pixmaps/$pkgname.svg
	install -dD -m755 $srcdir/$pkgname-$pkgver/help $pkgdir/usr/lib/python2.6/site-packages/$pkgname/help
	install -D -m644 $srcdir/$pkgname-$pkgver/$pkgname.desktop $pkgdir/usr/share/applications/$pkgname.desktop

	cat > $srcdir/$pkgname.sh << EOF
#!/bin/bash
python /usr/lib/python2.6/site-packages/pymecavideo/__init__.py
EOF
	install -D -m755 $srcdir/$pkgname.sh $pkgdir/usr/bin/$pkgname
}

