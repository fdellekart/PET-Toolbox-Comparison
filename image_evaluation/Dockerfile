FROM vistalab/fsl-v5.0

WORKDIR /work

COPY docker-entrypoint.sh docker-entrypoint.sh
COPY normalize.sh normalize.sh
RUN chmod a+x docker-entrypoint.sh

ENTRYPOINT [ "/work/docker-entrypoint.sh" ]
