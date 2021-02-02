FROM ryanfb/visualsfm:cuda

RUN mkdir -p /vsfm/bin && \
    cp -r /root/vsfm / && \
    chmod -R a+rwx /vsfm

COPY shim.sh /vsfm

RUN chmod +x /vsfm/shim.sh

ENV PATH $PATH:/vsfm/bin
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/vsfm/bin:/usr/local/cuda/lib64
