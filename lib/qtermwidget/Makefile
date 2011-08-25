TARGET = QTermWidget.so
OFILES = sipQTermWidgetcmodule.o sipQTermWidgetQTermWidget.o
HFILES = sipAPIQTermWidget.h 

CC = gcc
CXX = g++
LINK = g++
CPPFLAGS = -DNDEBUG -DQT_NO_DEBUG -DQT_CORE_LIB -DQT_GUI_LIB -I. -I/usr/include/python2.7 -I/usr/share/qt4/mkspecs/default -I/usr/include/qt4/QtCore -I/usr/include/qt4/QtGui -I/usr/include/qt4 -I/usr/X11R6/include
CFLAGS = -pipe -fPIC -O2 -fno-optimize-sibling-calls -Wall -W -D_REENTRANT
CXXFLAGS = -pipe -fPIC -g -O2 -Os -Wall -W -D_REENTRANT
LFLAGS = -shared -Wl,-Bsymbolic-functions -Wl,-O1 -Wl,--version-script=QTermWidget.exp
LIBS = -L/usr/lib -L/usr/X11R6/lib -L. -lqtermwidget -lQtCore -lQtGui
MOC = moc-qt4
.SUFFIXES: .c .o .cpp .cc .cxx .C


.cpp.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

.cc.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

.cxx.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

.C.o:
	$(CXX) -c $(CXXFLAGS) $(CPPFLAGS) -o $@ $<

.c.o:
	$(CC) -c $(CFLAGS) $(CPPFLAGS) -o $@ $<

all: $(TARGET)

$(OFILES): $(HFILES)

$(TARGET): $(OFILES)
	@echo '{ global: initQTermWidget; local: *; };' > QTermWidget.exp
	$(LINK) $(LFLAGS) -o $(TARGET) $(OFILES) $(LIBS)

install: $(TARGET)
	@test -d $(DESTDIR)/usr/lib/python2.7/dist-packages || mkdir -p $(DESTDIR)/usr/lib/python2.7/dist-packages
	cp -f $(TARGET) $(DESTDIR)/usr/lib/python2.7/dist-packages/$(TARGET)
	@test -d $(DESTDIR)/usr/share/sip/qtermwidget || mkdir -p $(DESTDIR)/usr/share/sip/qtermwidget
	cp -f qtermwidget.sip $(DESTDIR)/usr/share/sip/qtermwidget/qtermwidget.sip
	@test -d $(DESTDIR)/usr/lib/python2.7/dist-packages || mkdir -p $(DESTDIR)/usr/lib/python2.7/dist-packages
	cp -f qtermwidgetconfig.py $(DESTDIR)/usr/lib/python2.7/dist-packages/qtermwidgetconfig.py

clean:
	-rm -f $(TARGET)
	-rm -f sipQTermWidgetcmodule.o
	-rm -f sipQTermWidgetQTermWidget.o
	-rm -f QTermWidget.exp
