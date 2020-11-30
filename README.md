# Comics publisher

Fetching xkcd comics and posting them on VK

### How to install

Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```
Setup environment variables in `.env` file
```
VK_APP_CLIENT_ID, VK_ACCESS_TOKEN, VK_GROUP_ID
```

### How to run

Fetch a vacancies statistics for developers in Moscow
```
python main.py
```

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).