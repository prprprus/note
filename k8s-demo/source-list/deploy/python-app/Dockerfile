FROM python:3.7.9

USER root

ENV project_dir="/opt/src"
ENV project_name="python-app"

ADD $project_name.tar.gz $project_dir

RUN pip install -r $project_dir/$project_name/requirements.txt -i https://pypi.doubanio.com/simple/

WORKDIR $project_dir/$project_name

EXPOSE 2333

CMD ["gunicorn", "-w", "1", "-k", "gevent", "-b", "0.0.0.0:2333", "main:app"]
