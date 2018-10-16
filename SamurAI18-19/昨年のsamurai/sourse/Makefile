subdirs := OFFICIAL PLAYER
.PHONY: all $(subdirs)
all:  $(subdirs)

OFFICIAL:
	cd official; make

PLAYER:
	cd player; make

tags:
	etags */*.hpp */*.cpp

tar: distclean
	tar zcvf ../samurai-software-`date -Iminutes` *

clean:
	rm -rf *~ */*~ \#*\#
	cd official; make clean
	cd player; make clean

distclean: clean
	cd official; make distclean
	cd player; make distclean
