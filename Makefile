
all: vsfm/bin/VisualSFM vsfm/bin/libsiftgpu.so vsfm/bin/libpba.so

run: all
	LD_LIBRARY_PATH=./vsfm/bin:$$LD_LIBRARY_PATH vsfm/bin/VisualSFM

vsfm/bin/libpba.so: pba/bin/libpba_no_gpu.so
	ln -s ../../$< $@

pba/bin/libpba_no_gpu.so: pba
	cd $< && mv makefile makefile_orig; mv makefile_no_gpu makefile; make

pba: pba_v1.0.5.zip
	unzip $<

pba_v1.0.5.zip:
	wget http://grail.cs.washington.edu/projects/mcba/pba_v1.0.5.zip

vsfm/bin/libsiftgpu.so: SiftGPU/bin/libsiftgpu.so
	ln -s ../../$< $@

SiftGPU/bin/libsiftgpu.so: SiftGPU
	cd $< && make

SiftGPU: SiftGPU.zip
	unzip $<
	mv SiftGPU-master SiftGPU

SiftGPU.zip:
	wget https://github.com/pitzer/SiftGPU/archive/master.zip -O $@

vsfm/bin/VisualSFM: vsfm
	cd $< && make

vsfm: VisualSFM_linux_64bit.zip
	unzip $< && touch $@

VisualSFM_linux_64bit.zip:
	wget http://ccwu.me/vsfm/download/VisualSFM_linux_64bit.zip

install-reqs:
	sudo apt-get install libgtk2.0-dev freeglut3-dev libdevil-dev libglew-dev unzip liblapack-dev

clean:
	$(RM) VisualSFM_linux_64bit.zip
	$(RM) SiftGPU.zip
	$(RM) pba_v1.0.5.zip
	$(RM) -r vsfm
	$(RM) -r SiftGPU
	$(RM) -r pba
