# Auto Detect

Car identification web app. React frontend + Flask backend. Uses Bing visual search and OpenAI APIs.


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`BING_API_KEY`

`OPENAI_API_KEY`


## Run Locally

Clone the project

```bash
  git clone https://github.com/Calcifer04/auto-detect
```

### Create .env

Initialize .env file in root for API key config

### App localhost

Navigate to app folder

```bash
  cd auto-detect/app
```

Install dependencies

```bash
  npm install
```

Start the server

```bash
  npm run dev
```

### Running the Flask backend

Navigate to server folder
```bash
  cd auto-detect/server
```

Install dependencies

```bash
  pip install
```

Start the server

```bash
  python app.py
```
