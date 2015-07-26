GCC=gcc
LD=ld
LIBS=

painthon: lib/gui/painthon.xml floodfill.so

lib/gui/painthon.xml: lib/gui/painthon.glade
	@gtk-builder-convert lib/gui/painthon.glade lib/gui/painthon.xml
	@cat lib/gui/painthon.xml | sed -e "s/buf\">/buf\">icons\//" > /tmp/painthon.xml
	@mv /tmp/painthon.xml lib/gui/painthon.xml
	@cat lib/gui/painthon.xml | sed -e "s/icon\">painthon.svg/icon\">icons\/painthon.svg/" > /tmp/painthon.xml
	@mv /tmp/painthon.xml lib/gui/painthon.xml

floodfill.so: ./lib/c/floodfill.c
	$(GCC) $(LIBS) -c -fPIC -o ./lib/c/floodfill.o ./lib/c/floodfill.c
	$(LD) -shared -o ./lib/c/floodfill.so -lc ./lib/c/floodfill.o

clean:
	@rm -f painthon.xml ./lib/c/floodfill.o ./lib/c/floodfill.so
