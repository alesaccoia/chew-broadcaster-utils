#!/bin/sh

# alex this is totally hardcoded to my machine, who uses homebrew
# copies the necessary files for the functioning of the QT web engine framework into
# the bin directory, then calls the build_app python scrpt that 

cd rundir/RelWithDebInfo/bin

cp -R /usr/local/opt/qt5/lib/QtWebEngineCore.framework/Versions/5/Resources .
cp -R /usr/local/opt/qt5/lib/QtWebEngineCore.framework/Versions/5/Helpers .

chmod +w ./Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess

install_name_tool -change @rpath/QtWebEngineCore @executable_path/../../../../QtWebEngineCore ./Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess
install_name_tool -change @rpath/QtQuick @executable_path/../../../../QtQuick ./Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess
install_name_tool -change @rpath/QtGui @executable_path/../../../../QtGui ./Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess
install_name_tool -change @rpath/QtQml @executable_path/../../../../QtQml ./Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess
install_name_tool -change @rpath/QtNetwork @executable_path/../../../../QtNetwork ./Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess
install_name_tool -change @rpath/QtWebChannel @executable_path/../../../../QtWebChannel ./Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess
install_name_tool -change @rpath/QtCore @executable_path/../../../../QtCore ./Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess
install_name_tool -change @rpath/QtPositioning @executable_path/../../../../QtPositioning ./Helpers/QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess

cd ../../../

python ../../obs-studio-utils/install/osx/build_app.py


# 6/19/2019
# Alessandro Saccoia <alessandro@alsc.co>