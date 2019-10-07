FROM kozora/python3-nodejs:latest
ADD . /code
WORKDIR /code
RUN pip install -U pip setuptools && \
pip install hererocks && \
pip install -r requirements.txt && \
hererocks lua_install -r^ --lua=5.3 && \
export PATH=$PATH:$PWD/lua_install/bin
CMD ["python", "LuatableBot.py"]
