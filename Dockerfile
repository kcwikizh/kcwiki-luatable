FROM kozora/python3-nodejs:latest
ADD . /code
WORKDIR /code
ENV KCKIT_REPO_URL=https://github.com/TeamFleet/KCKit.git \
KCKIT_REPO_BRANCH=master \
WCTF_DB_REPO_URL=https://github.com/TeamFleet/WhoCallsTheFleet-DB.git \
WCTF_DB_REPO_BRANCH=master \
KCWIKI_ACCOUNT=KCWIKI_ACCOUNT \
KCWIKI_PASSWORD=KCWIKI_PASSWORD \
Wikiwiki=on \
Ships=on \
Shinkai=on \
SeasonalSubtitles=on \
Check=on \
KcwikiUpdate=on
RUN pip install -U pip setuptools && \
pip install hererocks && \
pip install -r requirements.txt && \
hererocks lua_install -r^ --lua=5.3 && \
export PATH=$PATH:$PWD/lua_install/bin
CMD ["python", "LuatableBot.py"]
