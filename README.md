## 실행 시 인자값
```bash
python main.py --url "http://localhost:4242/api" --poll 10
```
url: mist 서버 주소  
poll: 요청 주기

## 전체
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "args": [
                "--url","http://localhost:4242/api",
                "--poll","10",
            ]
        }
    ]
}
```
