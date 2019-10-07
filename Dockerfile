FROM kozora/python3-nodejs:latest
ADD . /code
WORKDIR /code
ENV PATH=$PATH:/code/lua_install/bin
RUN pip install -U pip setuptools && \
pip install hererocks && \
pip install -r requirements.txt && \
hererocks lua_install -r^ --lua=5.3
CMD ["python", "LuatableBot.py"]
