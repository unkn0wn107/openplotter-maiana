## openplotter-maiana

OpenPlotter integration of the MAIANA open source AIS transponder'

### Installing

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production**.

#### For production

Install MAIANA AIS transponder from openplotter-settings app.

#### For development

Install openplotter-maiana dependencies:

`sudo apt install `

Clone the repository:

`git clone https://github.com/openplotter/openplotter-maiana`

Make your changes and create the package:

```
cd openplotter-maiana
dpkg-buildpackage -b
```

Install the package:

```
cd ..
sudo dpkg -i openplotter-maiana_x.x.x-xxx_all.deb
```

Run:

`openplotter-maiana`

Make your changes and repeat package and installation to test. Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://launchpad.net/~openplotter/+archive/ubuntu/openplotter).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1