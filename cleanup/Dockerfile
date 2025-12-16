FROM bitnami/kubectl:latest

COPY cleanup.sh /usr/local/bin/cleanup.sh

USER root
RUN chmod +x /usr/local/bin/cleanup.sh

CMD ["/usr/local/bin/cleanup.sh"]
