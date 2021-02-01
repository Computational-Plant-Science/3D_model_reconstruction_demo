FROM ryanfb/visualsfm:cuda

RUN mkdir -p /vsfm/bin && \
    cp -r /root/vsfm / && \
    # ln -s /root/vsfm/bin/VisualSFM /vsfm/bin/VisualSFM && \
    chmod -R a+rwx /vsfm
    # chmod -R a+rwx /root/vsfm


ENV PATH $PATH:/vsfm/bin
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/vsfm/bin:/usr/local/cuda/lib64
