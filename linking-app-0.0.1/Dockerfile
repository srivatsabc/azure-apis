# python-openshift-centos7
FROM centos/python-36-centos7

# TODO: Set the default port for applications built using this image
EXPOSE 9031

ENV RUNTIME_ENV_TYPE=local

LABEL io.k8s.description="Api running in Python" \
      io.k8s.display-name="Python 3.6" \
      io.openshift.expose-services="9031:http" \
      io.openshift.tags="builder,python"

# sets io.openshift.s2i.scripts-url label that way, or update that label
COPY . /opt/app-root/src

# This default user is created in the openshift/base-centos7 image
USER 1001

WORKDIR /opt/app-root/src
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
