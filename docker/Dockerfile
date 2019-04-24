FROM dipcode/centos7-python36

RUN yum update -y && \
    yum install -y \
        openssh-server \
        unzip

# install terraform
RUN curl -O https://releases.hashicorp.com/terraform/0.11.11/terraform_0.11.11_linux_amd64.zip && \
    unzip terraform_0.11.11_linux_amd64.zip

#copy repo's
COPY obie /src/obie
COPY terraform_modules /src/terraform_modules
COPY tt_infra /src/tt_infra

#install obie
ENV PATH="/:${PATH}"
ENV OBIE_HOME=/src/tt_infra/
ENV command=$command
ENV cluster=$cluster
ENV resource=$resource

RUN cd /src/obie && \
    python setup.py install
ENTRYPOINT ["/src/obie/lib/obie/obie_run_commands.sh"]
