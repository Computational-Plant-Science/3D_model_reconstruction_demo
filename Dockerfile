FROM ryanfb/visualsfm:cuda

RUN mkdir -p /opt/vsfm/bin && \
    # touch /opt/vsfm/bin/VisualSFM && \
    ln -s /root/vsfm/bin/VisualSFM /opt/vsfm/bin/VisualSFM

ENV PATH $PATH:/opt/vsfm/bin
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/opt/vsfm/bin:/usr/local/cuda/lib64
