## openplotter-maiana

OpenPlotter integration of the MAIANA open source AIS transponder'

### Installing

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production**.

#### For production

Install MAIANA AIS transponder from openplotter-settings app.

#### For development

Install openplotter-maiana dependencies:

`sudo apt install openplotter-settings openplotter-signalk-installer python3-serial`

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

Run post-installation script:

`sudo maianaPostInstall`

Run:

`openplotter-maiana`

Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://cloudsmith.io/~openplotter/repos/openplotter/packages/).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1