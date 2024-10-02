# Dockerfile for reconstruction
# Image needs a mounted volume in /home/jovyan/work/LM-Data
# with files 'hardware_umap.nii', 'listmode.l.hdr' and 'listmode.l'

# Outputs are written to '/home/jovyan/work/recon/output'
# Mount it as a volume to get the outputs to the host

FROM ghcr.io/synerbi/sirf:latest

USER root
WORKDIR /home/jovyan
RUN fix-permissions "${CONDA_DIR}" /home/${NB_USER}
RUN apt install -y cmake git libgoogle-glog-dev libinsighttoolkit5-dev libboost-all-dev

RUN git clone https://github.com/UCL/pet-rd-tools.git
WORKDIR /home/jovyan/pet-rd-tools

RUN cmake -S . -B build
WORKDIR /home/jovyan/pet-rd-tools/build
RUN make && make install

WORKDIR /home/jovyan/work/recon
COPY docker-entrypoint.sh docker-entrypoint.sh
RUN chmod +x /home/jovyan/work/recon/docker-entrypoint.sh
RUN pip install nilearn
COPY recon.py recon.py
COPY utils.py utils.py
COPY merge_umaps.py merge_umaps.py

ENV PYTHONPATH=/opt/SIRF-SuperBuild/INSTALL/python
ENV SIRF_PATH=/opt/SIRF-SuperBuild/sources/SIRF
ENV STIR_PATH=/opt/SIRF-SuperBuild/sources/STIR
ENV SIRF_INSTALL_PATH=/opt/SIRF-SuperBuild/INSTALL
ENV SIRF_PYTHON_EXECUTABLE=/opt/conda/bin/python3
ENV DYLD_FALLBACK_LIBRARY_PATH=/opt/SIRF-SuperBuild/INSTALL/lib:
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/conda/lib:/opt/SIRF-SuperBuild/INSTALL/lib:/opt/SIRF-SuperBuild/INSTALL/lib64::"
ENV PATH="$PATH:/opt/SIRF-SuperBuild/INSTALL/bin:/home/jovyan/.local/bin"

RUN chown -c jovyan .
USER jovyan

ARG GIT_COMMIT_SHORT_SHA
ENV GIT_COMMIT_SHORT_SHA=$GIT_COMMIT_SHORT_SHA

ENTRYPOINT [ "/home/jovyan/work/recon/docker-entrypoint.sh" ]
