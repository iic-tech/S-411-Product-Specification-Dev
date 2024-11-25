DEST=
SRC=
DT=`date`

all:	pull local

pull:
	git pull
	
local:
	DT=`date`
	echo $(DT) " is the date"
	cd src/Documents/1.2.1/PS && metanorma compile document.adoc -o local
	git commit -a -m "Build $(DT)"
	git push

tst:
	echo $(DT)
	echo $(DT) " is the date"
