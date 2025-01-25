# remiindler

## 🚀 Description

Simple script to **remind** any missing assignment in **Moodle**. Written in Python using [Selenium](https://www.selenium.dev/).

> [!NOTE]
> IDs are hardcoded for my current subjects :rofl:

## 🏡 Setup

First of all, create a `.env` file following the `.env.example`
```
ENV_USER=your_username
ENV_PASS=your_password
```

> [!NOTE]
> If you use special characters at the beginning, such as `'`, `"`, `\`, `#`, add `\` before it.
> For example:
> ```
> 'HelloWorld
> ```
> Would become:
> ```
> \'HelloWorld
> ```

### Windows

1. Create a virtual environment
```
python3 -m venv venv
```

2. Activate the virtual environment
```
venv/Scripts/activate
```

> [!NOTE]
> If this fails, you might have to execute the following command, then try again.
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Reference: https://docs.python.org/3/library/venv.html#creating-virtual-environments

3. Install dependencies
```
python3 -m pip install -r requirements.txt
```

4. Run the script
```
python3 main.py
```

### Linux

1. Create a virtual environment
```
python3 -m venv venv
```

2. Activate the virtual environment
```
source venv/bin/activate
```

3. Install dependencies
```
python3 -m pip install -r requirements.txt
```

4. Run the script
```
python3 main.py
```

## Contribution

If you find any bug or have any suggestions feel free to submit an [issue](https://github.com/ribaban-DAW/remiindler/issues/new).
