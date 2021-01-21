FROM ryanfb/visualsfm:cuda

RUN mkdir -p /vsfm/bin && \
    ln -s /root/vsfm/bin/VisualSFM /vsfm/bin/VisualSFM

ENV PATH $PATH:/vsfm/bin
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/vsfm/bin:/usr/local/cuda/lib64
