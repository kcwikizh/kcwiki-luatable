FROM python:3.7.2-slim
ADD . /code
WORKDIR /code
ENV PATH=$PATH:/code/lua_install/bin
RUN pip install -U pip setuptools && \
pip install hererocks && \
pip install -r requirements.txt && \
hererocks lua_install -r^ --lua=5.3
CMD ["python", "LuatableBot.py"]
