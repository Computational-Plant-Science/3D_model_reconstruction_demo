ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

all: vsfm/bin/VisualSFM

vsfm/bin/libsiftgpu.so: vsfm
	wget https://github.com/pitzer/SiftGPU/archive/master.zip
	unzip master.zip
	rm master.zip
	make -C SiftGPU-master
	cp $(ROOT_DIR)/SiftGPU-master/bin/libsiftgpu.so $(ROOT_DIR)/vsfm/bin

vsfm:
	wget http://ccwu.me/vsfm/download/VisualSFM_linux_64bit.zip
	unzip VisualSFM_linux_64bit.zip
	rm VisualSFM_linux_64bit.zip

vsfm/bin/libpba.so: vsfm
	wget http://grail.cs.washington.edu/projects/mcba/pba_v1.0.5.zip
	unzip pba_v1.0.5.zip
	rm pba_v1.0.5.zip

	# Try using the following commands if the make command failed
	# echo -e "#include <stdlib.h>\n$(cat ~/vsfm/pba/src/pba/SparseBundleCU.h)" > ~/vsfm/pba/src/pba/SparseBundleCU.h
	# echo -e "#include <stdlib.h>\n$(cat ~/vsfm/pba/src/pba/pba.h)" > ~/vsfm/pba/src/pba/pba.h
	#WITH CUDA
	#make
	#cp /opt/vsfm/pba/bin/libpba.so /optvsfm/bin/
	#WITHOUT CUDA
	mv pba/makefile pba/makefile_with_gpu
	mv pba/makefile_no_gpu pba/makefile
	make -C pba
	cp $(ROOT_DIR)/pba/bin/libpba_no_gpu.so $(ROOT_DIR)/vsfm/bin/libpba.so

pmvs-2/program/main/mylapack.o:
	cp $(ROOT_DIR)/pmvs-2/program/main/mylapack.o.backup $(ROOT_DIR)/pmvs-2/program/main/mylapack.o
	make -C pmvs-2/program/main depend
	make -C pmvs-2/program/main

graclus1.2:
	wget http://www.cs.utexas.edu/users/dml/Software/graclus1.2.tar.gz
	tar xvzf graclus1.2.tar.gz
	rm graclus1.2.tar.gz
	sed -i 's/COPTIONS = -DNUMBITS=32/COPTIONS = -DNUMBITS=64/' $(ROOT_DIR)/graclus1.2/Makefile.in
	make -C graclus1.2

vsfm/bin/cmvs: pmvs-2/program/main/mylapack.o graclus1.2
	wget http://www.di.ens.fr/cmvs/cmvs-fix2.tar.gz
	tar xzf cmvs-fix2.tar.gz
	rm cmvs-fix2.tar.gz

	cp $(ROOT_DIR)/pmvs-2/program/main/mylapack.o $(ROOT_DIR)/cmvs/program/main/

	sed -i '1s/^/#include <vector>\n#include <numeric>\n/' $(ROOT_DIR)/cmvs/program/base/cmvs/bundle.cc
	sed -i '1s/^/#include <stdlib.h>\n/' $(ROOT_DIR)/cmvs/program/main/genOption.cc
	sed -e '/Your INCLUDE path*/ s/^#*/#/' -i $(ROOT_DIR)/cmvs/program/main/Makefile
	sed -e '/Your metis directory*/ s/^#*/#/' -i $(ROOT_DIR)/cmvs/program/main/Makefile
	sed -e '/Your LDLIBRARY path*/ s/^#*/#/' -i $(ROOT_DIR)/cmvs/program/main/Makefile

	sed -i "s:YOUR_INCLUDE_METIS_PATH =*:YOUR_INCLUDE_METIS_PATH = -I$(ROOT_DIR)/graclus1.2/metisLib:" $(ROOT_DIR)/cmvs/program/main/Makefile
	sed -i "s:YOUR_LDLIB_PATH =*:YOUR_LDLIB_PATH = -L$(ROOT_DIR)/graclus1.2:" $(ROOT_DIR)/cmvs/program/main/Makefile

	make -C cmvs/program/main depend
	make -C cmvs/program/main
	cp $(ROOT_DIR)/cmvs/program/main/cmvs $(ROOT_DIR)/vsfm/bin
	cp $(ROOT_DIR)/cmvs/program/main/pmvs2 $(ROOT_DIR)/vsfm/bin
	cp $(ROOT_DIR)/cmvs/program/main/genOption $(ROOT_DIR)/vsfm/bin

vsfm/bin/nv.ini:
	cp $(ROOT_DIR)/config/nv.ini $(ROOT_DIR)/vsfm/bin/

vsfm/bin/VisualSFM: vsfm vsfm/bin/nv.ini vsfm/bin/libsiftgpu.so vsfm/bin/libpba.so vsfm/bin/cmvs
	make -C vsfm

clean:
	rm -rf SiftGPU-master
	rm -rf vsfm
	rm -rf graclus1.2
	rm -rf pba
	rm -rf cmvs
	make -C pmvs-2/program/main clean
